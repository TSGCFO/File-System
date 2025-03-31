"""
Main window for the FileConverter GUI application.

This module provides the main window class for the FileConverter GUI.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

try:
    from PyQt6.QtCore import Qt, QSize, QSettings, QTimer, pyqtSlot
    from PyQt6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QFileDialog, QMessageBox,
        QToolBar, QStatusBar, QVBoxLayout, QHBoxLayout,
        QWidget, QPushButton, QLabel, QComboBox, QListWidget,
        QSplitter, QFrame, QStyle
    )
    GUI_AVAILABLE = True
except ImportError:
    # Create dummy classes as placeholders when PyQt is not available
    class QMainWindow:
        pass
    GUI_AVAILABLE = False

from fileconverter.core.engine import ConversionEngine
from fileconverter.core.registry import ConverterRegistry
from fileconverter.config import get_config
from fileconverter.utils.error_handling import ConversionError, format_error_for_user
from fileconverter.utils.logging_utils import get_logger

# Only import GUI components if PyQt is available
if GUI_AVAILABLE:
    from fileconverter.gui.conversion_dialog import ConversionDialog
    from fileconverter.gui.settings_dialog import SettingsDialog
    from fileconverter.gui.resources import load_stylesheet

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main window for the FileConverter GUI application."""
    
    def __init__(self):
        """Initialize the main window."""
        if not GUI_AVAILABLE:
            raise ImportError("PyQt6 is required for GUI functionality")
        
        super().__init__()
        
        # Initialize settings
        self.settings = QSettings("TSG Fulfillment", "FileConverter")
        
        # Initialize engine and registry
        self.engine = ConversionEngine()
        self.registry = ConverterRegistry()
        
        # Setup UI
        self.setWindowTitle("FileConverter")
        self.setMinimumSize(800, 600)
        
        # Apply stylesheet
        try:
            stylesheet = load_stylesheet("default.qss")
            if stylesheet:
                self.setStyleSheet(stylesheet)
        except Exception as e:
            logger.warning(f"Failed to load stylesheet: {str(e)}")
        
        self.setup_ui()
        
        # Restore geometry and state
        self.restore_settings()
        
        # Setup file handling
        self.setAcceptDrops(True)
        
        # Update status
        self.statusBar().showMessage("Ready")
    
    def setup_ui(self):
        """Set up the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Splitter for main areas
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - file formats
        formats_panel = QFrame()
        formats_layout = QVBoxLayout(formats_panel)
        formats_label = QLabel("<h3>Supported Formats</h3>")
        formats_layout.addWidget(formats_label)
        
        self.formats_list = QListWidget()
        formats_layout.addWidget(self.formats_list)
        
        # Populate formats list
        self.update_formats_list()
        
        # Right panel - recent conversions
        recent_panel = QFrame()
        recent_layout = QVBoxLayout(recent_panel)
        recent_label = QLabel("<h3>Recent Conversions</h3>")
        recent_layout.addWidget(recent_label)
        
        self.recent_list = QListWidget()
        recent_layout.addWidget(self.recent_list)
        
        # Add panels to splitter
        splitter.addWidget(formats_panel)
        splitter.addWidget(recent_panel)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        
        # Convert button
        self.convert_button = QPushButton("Convert File")
        self.convert_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogStart))
        self.convert_button.clicked.connect(self.on_convert_clicked)
        button_layout.addWidget(self.convert_button)
        
        # Batch convert button
        self.batch_button = QPushButton("Batch Convert")
        self.batch_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        self.batch_button.clicked.connect(self.on_batch_clicked)
        button_layout.addWidget(self.batch_button)
        
        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.settings_button.clicked.connect(self.on_settings_clicked)
        button_layout.addWidget(self.settings_button)
        
        # Menu bar
        self.setup_menu()
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Toolbar
        self.setup_toolbar()
        
        # Update recent conversions list
        self.update_recent_list()
    
    def setup_menu(self):
        """Set up the menu bar."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # Open action
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open a file for conversion")
        open_action.triggered.connect(self.on_open_file)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = self.menuBar().addMenu("&Tools")
        
        # Convert action
        convert_action = QAction("&Convert...", self)
        convert_action.setShortcut("Ctrl+C")
        convert_action.setStatusTip("Convert a file")
        convert_action.triggered.connect(self.on_convert_clicked)
        tools_menu.addAction(convert_action)
        
        # Batch convert action
        batch_action = QAction("&Batch Convert...", self)
        batch_action.setShortcut("Ctrl+B")
        batch_action.setStatusTip("Convert multiple files")
        batch_action.triggered.connect(self.on_batch_clicked)
        tools_menu.addAction(batch_action)
        
        tools_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+P")
        settings_action.setStatusTip("Configure application settings")
        settings_action.triggered.connect(self.on_settings_clicked)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("Show the application's About box")
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Set up the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # Open action
        open_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton), "Open", self)
        open_action.setStatusTip("Open a file for conversion")
        open_action.triggered.connect(self.on_open_file)
        toolbar.addAction(open_action)
        
        # Convert action
        convert_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Convert", self)
        convert_action.setStatusTip("Convert a file")
        convert_action.triggered.connect(self.on_convert_clicked)
        toolbar.addAction(convert_action)
        
        # Batch convert action
        batch_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon), "Batch", self)
        batch_action.setStatusTip("Convert multiple files")
        batch_action.triggered.connect(self.on_batch_clicked)
        toolbar.addAction(batch_action)
        
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "Settings", self)
        settings_action.setStatusTip("Configure application settings")
        settings_action.triggered.connect(self.on_settings_clicked)
        toolbar.addAction(settings_action)
    
    def update_formats_list(self):
        """Update the list of supported formats."""
        self.formats_list.clear()
        
        formats = self.registry.get_supported_formats()
        if not formats:
            self.formats_list.addItem("No supported formats found")
            return
        
        for category, format_list in formats.items():
            self.formats_list.addItem(f"--- {category.upper()} ---")
            for fmt in sorted(format_list):
                extensions = self.registry.get_format_extensions(fmt)
                ext_str = ", ".join(f".{ext}" for ext in extensions)
                self.formats_list.addItem(f"{fmt} ({ext_str})")
    
    def update_recent_list(self):
        """Update the list of recent conversions."""
        self.recent_list.clear()
        
        recent_files = self.settings.value("recentFiles", [])
        if not recent_files:
            self.recent_list.addItem("No recent conversions")
            return
        
        for file_path in recent_files:
            if Path(file_path).exists():
                self.recent_list.addItem(file_path)
    
    def update_recent_menu(self):
        """Update the recent files submenu."""
        self.recent_menu.clear()
        
        recent_files = self.settings.value("recentFiles", [])
        if not recent_files:
            no_recent_action = QAction("No recent files", self)
            no_recent_action.setEnabled(False)
            self.recent_menu.addAction(no_recent_action)
            return
        
        for i, file_path in enumerate(recent_files):
            if Path(file_path).exists():
                action = QAction(f"{i+1}. {Path(file_path).name}", self)
                action.setData(file_path)
                action.triggered.connect(self.on_open_recent)
                self.recent_menu.addAction(action)
        
        self.recent_menu.addSeparator()
        
        clear_action = QAction("Clear Recent Files", self)
        clear_action.triggered.connect(self.on_clear_recent)
        self.recent_menu.addAction(clear_action)
    
    def add_recent_file(self, file_path: str):
        """Add a file to the recent files list.
        
        Args:
            file_path: Path to the file to add.
        """
        recent_files = self.settings.value("recentFiles", [])
        
        # Convert to list if it's not already (can happen with QSettings)
        if not isinstance(recent_files, list):
            recent_files = [recent_files] if recent_files else []
        
        # Remove existing entry (if any)
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to start of list
        recent_files.insert(0, file_path)
        
        # Limit list size
        max_recent = self.settings.value("general/recentFilesLimit", 10, type=int)
        if len(recent_files) > max_recent:
            recent_files = recent_files[:max_recent]
        
        # Save to settings
        self.settings.setValue("recentFiles", recent_files)
        
        # Update UI
        self.update_recent_list()
        self.update_recent_menu()
    
    def save_settings(self):
        """Save application settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
    
    def restore_settings(self):
        """Restore application settings."""
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        
        if self.settings.contains("windowState"):
            self.restoreState(self.settings.value("windowState"))
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.save_settings()
        event.accept()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.open_file(file_path)
    
    def open_file(self, file_path: str):
        """Open a file for conversion.
        
        Args:
            file_path: Path to the file to open.
        """
        if not Path(file_path).exists():
            QMessageBox.warning(
                self,
                "File not found",
                f"The file {file_path} does not exist."
            )
            return
        
        # Add to recent files
        self.add_recent_file(file_path)
        
        # Start conversion dialog
        self.show_conversion_dialog(file_path)
    
    def show_conversion_dialog(self, input_path: str):
        """Show the conversion dialog.
        
        Args:
            input_path: Path to the input file.
        """
        dialog = ConversionDialog(self.engine, self.registry, input_path, parent=self)
        if dialog.exec():
            # Get result from dialog
            result = dialog.get_conversion_result()
            if result:
                QMessageBox.information(
                    self,
                    "Conversion Complete",
                    f"File successfully converted to: {result.get('output_path', '')}"
                )
                
                # Add output to recent files
                output_path = result.get("output_path", "")
                if output_path and Path(output_path).exists():
                    self.add_recent_file(output_path)
            else:
                QMessageBox.warning(
                    self,
                    "Conversion Failed",
                    "The conversion operation did not complete successfully."
                )
    
    @pyqtSlot()
    def on_open_file(self):
        """Handle open file action."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setWindowTitle("Open File for Conversion")
        
        # Get all supported extensions
        formats = self.registry.get_supported_formats()
        extensions = []
        for category, format_list in formats.items():
            for fmt in format_list:
                fmt_extensions = self.registry.get_format_extensions(fmt)
                extensions.extend(fmt_extensions)
        
        # Remove duplicates and sort
        extensions = sorted(set(extensions))
        
        # Create filter string
        filter_str = "All supported formats ("
        filter_str += " ".join(f"*.{ext}" for ext in extensions)
        filter_str += ")"
        
        # Add individual format filters
        for category, format_list in formats.items():
            cat_extensions = []
            for fmt in format_list:
                fmt_extensions = self.registry.get_format_extensions(fmt)
                cat_extensions.extend(fmt_extensions)
            
            # Remove duplicates and sort
            cat_extensions = sorted(set(cat_extensions))
            
            # Add filter
            filter_str += f";;{category.capitalize()} formats ("
            filter_str += " ".join(f"*.{ext}" for ext in cat_extensions)
            filter_str += ")"
        
        # Add all files filter
        filter_str += ";;All files (*)"
        
        file_dialog.setNameFilter(filter_str)
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.open_file(file_path)
    
    @pyqtSlot()
    def on_open_recent(self):
        """Handle open recent file action."""
        action = self.sender()
        if action:
            file_path = action.data()
            self.open_file(file_path)
    
    @pyqtSlot()
    def on_clear_recent(self):
        """Handle clear recent files action."""
        self.settings.setValue("recentFiles", [])
        self.update_recent_list()
        self.update_recent_menu()
    
    @pyqtSlot()
    def on_convert_clicked(self):
        """Handle convert button click."""
        self.on_open_file()
    
    @pyqtSlot()
    def on_batch_clicked(self):
        """Handle batch convert button click."""
        QMessageBox.information(
            self,
            "Batch Conversion",
            "Batch conversion is not yet implemented in the GUI. "
            "Please use the command-line interface for batch operations."
        )
    
    @pyqtSlot()
    def on_settings_clicked(self):
        """Handle settings button click."""
        dialog = SettingsDialog(self.engine, parent=self)
        if dialog.exec():
            # Reload engine with new settings
            config_path = dialog.get_config_path()
            if config_path:
                self.engine = ConversionEngine(config_path=config_path)
    
    @pyqtSlot()
    def on_about(self):
        """Handle about action."""
        from fileconverter.version import __version__, __author__, __email__
        
        QMessageBox.about(
            self,
            "About FileConverter",
            f"<h3>FileConverter {__version__}</h3>"
            f"<p>A comprehensive file conversion utility.</p>"
            f"<p>Author: {__author__} ({__email__})</p>"
            f"<p>Copyright © 2023-2025 TSG Fulfillment</p>"
        )


def start_gui():
    """Start the GUI application.
    
    Returns:
        Exit code from the application.
    """
    if not GUI_AVAILABLE:
        print("Error: PyQt6 is required for GUI functionality")
        print("Please install with 'pip install fileconverter[gui]' or 'pip install PyQt6'")
        return 1
    
    app = QApplication(sys.argv)
    app.setApplicationName("FileConverter")
    app.setOrganizationName("TSG Fulfillment")
    app.setOrganizationDomain("tsgfulfillment.com")
    
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(start_gui())