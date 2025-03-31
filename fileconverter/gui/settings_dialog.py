"""
Settings dialog for the FileConverter GUI application.

This module provides a dialog for configuring application settings.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

try:
    from PyQt6.QtCore import Qt, QSettings
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
        QLabel, QLineEdit, QComboBox, QPushButton, QFileDialog,
        QWidget, QSpinBox, QCheckBox, QDialogButtonBox,
        QMessageBox, QGroupBox
    )
    GUI_AVAILABLE = True
except ImportError:
    # Create dummy classes as placeholders when PyQt is not available
    class QDialog:
        pass
    GUI_AVAILABLE = False

from fileconverter.core.engine import ConversionEngine
from fileconverter.config import get_config, Config
from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    
    def __init__(self, engine: ConversionEngine, parent=None):
        """Initialize the settings dialog.
        
        Args:
            engine: The conversion engine.
            parent: Parent widget.
        """
        if not GUI_AVAILABLE:
            raise ImportError("PyQt6 is required for GUI functionality")
        
        super().__init__(parent)
        
        self.engine = engine
        self.settings = QSettings("TSG Fulfillment", "FileConverter")
        self.config = get_config()
        self.config_path = None
        
        # Set dialog properties
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.resize(700, 500)
        
        # Check if config file exists, create default if not
        if not self.config._loaded_path:
            try:
                from fileconverter.config import create_default_config_file
                self.config_path = str(create_default_config_file())
            except Exception as e:
                logger.error(f"Failed to create default config file: {str(e)}")
        
        # Setup UI
        self.setup_ui()
        
        # Load settings
        self.load_settings()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # General tab
        self.setup_general_tab()
        
        # Converters tabs
        self.setup_converters_tabs()
        
        # Advanced tab
        self.setup_advanced_tab()
        
        # Create direct access to config values
        self.config_widgets = {}
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.on_accepted)
        button_box.rejected.connect(self.reject)
        
        self.apply_button = button_box.button(QDialogButtonBox.StandardButton.Apply)
        self.apply_button.clicked.connect(self.on_apply)
        
        layout.addWidget(button_box)
    
    def setup_general_tab(self):
        """Set up the general settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Configuration file
        config_layout = QHBoxLayout()
        
        self.config_path_edit = QLineEdit()
        self.config_path_edit.setReadOnly(True)
        config_layout.addWidget(self.config_path_edit)
        
        self.browse_config_button = QPushButton("Browse...")
        self.browse_config_button.clicked.connect(self.on_browse_config)
        config_layout.addWidget(self.browse_config_button)
        
        layout.addRow("Configuration File:", config_layout)
        
        # Recent files limit
        self.recent_files_limit = QSpinBox()
        self.recent_files_limit.setMinimum(1)
        self.recent_files_limit.setMaximum(50)
        self.recent_files_limit.setValue(10)
        layout.addRow("Recent Files Limit:", self.recent_files_limit)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        layout.addRow("Theme:", self.theme_combo)
        
        # Tooltips
        self.show_tooltips = QCheckBox("Show tooltips")
        self.show_tooltips.setChecked(True)
        layout.addWidget(self.show_tooltips)
        
        self.tab_widget.addTab(tab, "General")
    
    def setup_converters_tabs(self):
        """Set up tabs for each converter category."""
        # General conversion settings tab
        self._setup_general_conversion_tab()
        
        # Create a tab for each converter category
        converter_categories = [
            ("document", "Document"),
            ("spreadsheet", "Spreadsheet"),
            ("image", "Image"),
            ("data_exchange", "Data Exchange"),
            ("archive", "Archive"),
        ]
        
        for category_key, category_name in converter_categories:
            self._setup_converter_tab(category_key, category_name)
    
    def _setup_general_conversion_tab(self):
        """Set up the general conversion settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Max file size
        self.max_file_size = QSpinBox()
        self.max_file_size.setMinimum(1)
        self.max_file_size.setMaximum(10000)
        self.max_file_size.setValue(100)
        self.max_file_size.setSuffix(" MB")
        layout.addRow("Maximum File Size:", self.max_file_size)
        self.config_widgets[("general", "max_file_size_mb")] = self.max_file_size
        
        # Temporary directory
        temp_layout = QHBoxLayout()
        
        self.temp_dir_edit = QLineEdit()
        temp_layout.addWidget(self.temp_dir_edit)
        self.config_widgets[("general", "temp_dir")] = self.temp_dir_edit
        
        self.browse_temp_button = QPushButton("Browse...")
        self.browse_temp_button.clicked.connect(self.on_browse_temp)
        temp_layout.addWidget(self.browse_temp_button)
        
        layout.addRow("Temporary Directory:", temp_layout)
        
        # Preserve temp files
        self.preserve_temp = QCheckBox("Preserve temporary files")
        layout.addWidget(self.preserve_temp)
        self.config_widgets[("general", "preserve_temp_files")] = self.preserve_temp
        
        self.tab_widget.addTab(tab, "General Conversion")
    
    def _setup_converter_tab(self, category_key, category_name):
        """Set up a tab for a specific converter category.
        
        Args:
            category_key: Configuration key for the converter category.
            category_name: Display name for the converter category.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Enable checkbox
        enable_layout = QHBoxLayout()
        enable_checkbox = QCheckBox(f"Enable {category_name} Converter")
        enable_checkbox.setChecked(
            self.config.get("converters", category_key, "enabled", default=True)
        )
        enable_layout.addWidget(enable_checkbox)
        self.config_widgets[("converters", category_key, "enabled")] = enable_checkbox
        
        # Add stretch to push the checkbox to the left
        enable_layout.addStretch(1)
        
        layout.addLayout(enable_layout)
        
        # Create scrollable area for converter settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QFormLayout(scroll_content)
        
        # Get converter-specific settings from config
        converter_config = self.config.get("converters", category_key, default={})
        
        # Create widgets for each format's settings
        for format_key, format_settings in converter_config.items():
            # Skip the 'enabled' flag, we handled it separately
            if format_key == "enabled":
                continue
                
            # Create a group box for this format
            format_group = QGroupBox(format_key.upper())
            format_layout = QFormLayout(format_group)
            
            # Add settings for this format
            if isinstance(format_settings, dict):
                for setting_key, setting_value in format_settings.items():
                    # Create appropriate widget based on value type
                    if isinstance(setting_value, bool):
                        widget = QCheckBox()
                        widget.setChecked(setting_value)
                    elif isinstance(setting_value, int):
                        widget = QSpinBox()
                        widget.setMinimum(0)
                        widget.setMaximum(10000)
                        widget.setValue(setting_value)
                    elif isinstance(setting_value, float):
                        widget = QDoubleSpinBox()
                        widget.setMinimum(0)
                        widget.setMaximum(10000)
                        widget.setValue(setting_value)
                    elif setting_value is None:
                        widget = QLineEdit()
                        widget.setPlaceholderText("None (default)")
                    else:
                        widget = QLineEdit()
                        widget.setText(str(setting_value))
                    
                    # Special handling for delimiters
                    if setting_key == "delimiter":
                        widget = QComboBox()
                        delimiters = [
                            (",", "Comma (,)"),
                            (";", "Semicolon (;)"),
                            ("\t", "Tab (\\t)"),
                            ("|", "Pipe (|)"),
                            (" ", "Space ( )"),
                        ]
                        for value, display in delimiters:
                            widget.addItem(display, value)
                        
                        # Set current value
                        for i, (value, _) in enumerate(delimiters):
                            if value == setting_value:
                                widget.setCurrentIndex(i)
                                break
                    
                    # Store widget for later access
                    config_key = ("converters", category_key, format_key, setting_key)
                    self.config_widgets[config_key] = widget
                    
                    # Make setting key more user-friendly
                    display_key = " ".join(s.capitalize() for s in setting_key.split("_"))
                    format_layout.addRow(f"{display_key}:", widget)
            
            scroll_layout.addRow(format_group)
        
        # If no settings were added, show a message
        if len(scroll_layout) == 0:
            scroll_layout.addRow(QLabel("No configurable settings for this converter."))
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(tab, category_name)
    
    def setup_advanced_tab(self):
        """Set up the advanced settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Logging level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        layout.addRow("Logging Level:", self.log_level_combo)
        
        # Log file
        log_layout = QHBoxLayout()
        
        self.log_file_edit = QLineEdit()
        log_layout.addWidget(self.log_file_edit)
        
        self.browse_log_button = QPushButton("Browse...")
        self.browse_log_button.clicked.connect(self.on_browse_log)
        log_layout.addWidget(self.browse_log_button)
        
        layout.addRow("Log File:", log_layout)
        
        # Converter settings groups
        converters_group = QGroupBox("Enabled Converters")
        converters_layout = QVBoxLayout(converters_group)
        
        # Document converter
        self.document_converter = QCheckBox("Document Converter")
        self.document_converter.setChecked(True)
        converters_layout.addWidget(self.document_converter)
        
        # Spreadsheet converter
        self.spreadsheet_converter = QCheckBox("Spreadsheet Converter")
        self.spreadsheet_converter.setChecked(True)
        converters_layout.addWidget(self.spreadsheet_converter)
        
        # Image converter
        self.image_converter = QCheckBox("Image Converter")
        self.image_converter.setChecked(True)
        converters_layout.addWidget(self.image_converter)
        
        # Data exchange converter
        self.data_exchange_converter = QCheckBox("Data Exchange Converter")
        self.data_exchange_converter.setChecked(True)
        converters_layout.addWidget(self.data_exchange_converter)
        
        # Archive converter
        self.archive_converter = QCheckBox("Archive Converter")
        self.archive_converter.setChecked(True)
        converters_layout.addWidget(self.archive_converter)
        
        layout.addRow(converters_group)
        
        self.tab_widget.addTab(tab, "Advanced")
    
    def load_settings(self):
        """Load settings from the configuration."""
        # Get config path
        if self.config._loaded_path:
            self.config_path = str(self.config._loaded_path)
            self.config_path_edit.setText(self.config_path)
        
        # Load general settings
        self.recent_files_limit.setValue(
            self.settings.value("general/recentFilesLimit", 10, type=int)
        )
        
        theme = self.settings.value("gui/theme", "System")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.show_tooltips.setChecked(
            self.settings.value("gui/showTooltips", True, type=bool)
        )
        
        # Load conversion settings
        self.max_file_size.setValue(
            self.config.get("general", "max_file_size_mb", default=100)
        )
        
        temp_dir = self.config.get("general", "temp_dir")
        if temp_dir:
            self.temp_dir_edit.setText(temp_dir)
        
        self.preserve_temp.setChecked(
            self.config.get("general", "preserve_temp_files", default=False)
        )
        
        # Load advanced settings
        log_level = self.config.get("logging", "level", default="INFO")
        index = self.log_level_combo.findText(log_level)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)
        
        log_file = self.config.get("logging", "file")
        if log_file:
            self.log_file_edit.setText(log_file)
        
        # Load converter enabled settings (in case they weren't already set)
        for category in ["document", "spreadsheet", "image", "data_exchange", "archive"]:
            config_key = ("converters", category, "enabled")
            if config_key in self.config_widgets:
                self.config_widgets[config_key].setChecked(
                    self.config.get("converters", category, "enabled", default=True)
                )
    
    def save_settings(self):
        """Save settings to the configuration."""
        # Save general settings
        self.settings.setValue(
            "general/recentFilesLimit",
            self.recent_files_limit.value()
        )
        
        self.settings.setValue(
            "gui/theme",
            self.theme_combo.currentText()
        )
        
        self.settings.setValue(
            "gui/showTooltips",
            self.show_tooltips.isChecked()
        )
        
        # Save configuration settings
        if self.config_path:
            # Create new config instance
            config = Config(self.config_path)
            
            # Save general settings
            self.settings.setValue(
                "general/recentFilesLimit",
                self.recent_files_limit.value()
            )
            
            self.settings.setValue(
                "gui/theme",
                self.theme_combo.currentText()
            )
            
            self.settings.setValue(
                "gui/showTooltips",
                self.show_tooltips.isChecked()
            )
            
            # Save all configured settings
            for config_key, widget in self.config_widgets.items():
                # Extract value based on widget type
                if isinstance(widget, QLineEdit):
                    value = widget.text() if widget.text() else None
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    value = widget.value()
                elif isinstance(widget, QCheckBox):
                    value = widget.isChecked()
                elif isinstance(widget, QComboBox):
                    # Special handling for delimiters
                    if config_key[-1] == "delimiter":
                        value = widget.currentData()
                    else:
                        value = widget.currentText()
                else:
                    continue
                
                # Set the value in the config
                config.set(value, *config_key)
            
            # Save configuration
            try:
                config.save()
                logger.info(f"Settings saved to {self.config_path}")
                
                # Show success message
                QMessageBox.information(
                    self,
                    "Settings Saved",
                    "Settings have been saved successfully."
                )
                
                return True
            except Exception as e:
                logger.error(f"Error saving settings: {str(e)}")
                
                # Show error message
                QMessageBox.critical(
                    self,
                    "Error Saving Settings",
                    f"An error occurred while saving settings:\n{str(e)}"
                )
                
                return False
        else:
            # No config path specified
            result = QMessageBox.question(
                self,
                "Choose Configuration File",
                "No configuration file specified. Would you like to choose one?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if result == QMessageBox.StandardButton.Yes:
                self.on_browse_config()
                
                # If config path was set, try again
                if self.config_path:
                    return self.save_settings()
            
            return False
    
    def get_config_path(self) -> Optional[str]:
        """Get the path to the configuration file.
        
        Returns:
            Path to the configuration file, or None if not set.
        """
        return self.config_path
    
    def on_browse_config(self):
        """Handle browse config button click."""
        # Get current config path
        current_path = self.config_path_edit.text()
        
        # Get directory
        directory = os.path.dirname(current_path) if current_path else ""
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Configuration File",
            directory,
            "YAML files (*.yaml);;All files (*)"
        )
        
        if file_path:
            self.config_path = file_path
            self.config_path_edit.setText(file_path)
    
    def on_browse_temp(self):
        """Handle browse temp button click."""
        # Get current temp dir
        current_path = self.temp_dir_edit.text()
        
        # Show directory dialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Temporary Directory",
            current_path
        )
        
        if directory:
            self.temp_dir_edit.setText(directory)
    
    def on_browse_log(self):
        """Handle browse log button click."""
        # Get current log file
        current_path = self.log_file_edit.text()
        
        # Get directory
        directory = os.path.dirname(current_path) if current_path else ""
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Log File",
            directory,
            "Log files (*.log);;All files (*)"
        )
        
        if file_path:
            self.log_file_edit.setText(file_path)
    
    def on_apply(self):
        """Handle apply button click."""
        self.save_settings()
    
    def on_accepted(self):
        """Handle dialog acceptance."""
        if self.save_settings():
            self.accept()