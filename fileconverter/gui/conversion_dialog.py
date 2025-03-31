"""
Conversion dialog for the FileConverter GUI application.

This module provides a dialog for configuring and executing file conversions.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

try:
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
        QLabel, QLineEdit, QComboBox, QPushButton, QFileDialog,
        QProgressBar, QWidget, QTabWidget, QScrollArea, QFrame,
        QSpinBox, QDoubleSpinBox, QCheckBox, QDialogButtonBox,
        QMessageBox, QGroupBox
    )
    GUI_AVAILABLE = True
except ImportError:
    # Create dummy classes as placeholders when PyQt is not available
    class QDialog:
        pass
    GUI_AVAILABLE = False

from fileconverter.core.engine import ConversionEngine
from fileconverter.core.registry import ConverterRegistry
from fileconverter.utils.error_handling import ConversionError, format_error_for_user
from fileconverter.utils.file_utils import get_file_extension, get_file_format
from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)


class ConversionThread(QThread):
    """Thread for performing file conversion."""
    
    conversion_complete = pyqtSignal(bool, dict)
    
    def __init__(
        self,
        engine: ConversionEngine,
        input_path: str,
        output_path: str,
        parameters: Dict[str, Any]
    ):
        """Initialize the conversion thread.
        
        Args:
            engine: The conversion engine to use.
            input_path: Path to the input file.
            output_path: Path where the output will be saved.
            parameters: Conversion parameters.
        """
        super().__init__()
        self.engine = engine
        self.input_path = input_path
        self.output_path = output_path
        self.parameters = parameters
        self.result = {}
    
    def run(self):
        """Execute the conversion."""
        try:
            result = self.engine.convert_file(
                input_path=self.input_path,
                output_path=self.output_path,
                parameters=self.parameters
            )
            self.result = result
            self.conversion_complete.emit(True, result)
        except Exception as e:
            logger.exception(f"Error in conversion thread: {str(e)}")
            self.conversion_complete.emit(False, {"error": str(e)})


class ConversionDialog(QDialog):
    """Dialog for configuring and executing file conversions."""
    
    def __init__(
        self,
        engine: ConversionEngine,
        registry: ConverterRegistry,
        input_path: str,
        parent=None
    ):
        """Initialize the conversion dialog.
        
        Args:
            engine: The conversion engine to use.
            registry: The converter registry.
            input_path: Path to the input file.
            parent: Parent widget.
        """
        if not GUI_AVAILABLE:
            raise ImportError("PyQt6 is required for GUI functionality")
        
        super().__init__(parent)
        
        self.engine = engine
        self.registry = registry
        self.input_path = input_path
        self.conversion_thread = None
        self.conversion_result = None
        
        # Determine input format
        self.input_format = get_file_format(input_path)
        if not self.input_format:
            self.input_format = get_file_extension(input_path)
        
        # Find available output formats
        self.output_formats = self._get_available_output_formats()
        
        # Set dialog properties
        self.setWindowTitle("Convert File")
        self.setMinimumWidth(500)
        self.resize(600, 400)
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Input file section
        input_group = QGroupBox("Input File")
        input_layout = QFormLayout(input_group)
        
        self.input_path_edit = QLineEdit(self.input_path)
        self.input_path_edit.setReadOnly(True)
        input_layout.addRow("Input File:", self.input_path_edit)
        
        self.input_format_edit = QLineEdit(self.input_format or "Unknown")
        self.input_format_edit.setReadOnly(True)
        input_layout.addRow("Input Format:", self.input_format_edit)
        
        layout.addWidget(input_group)
        
        # Output section
        output_group = QGroupBox("Output Options")
        output_layout = QFormLayout(output_group)
        
        # Output format selection
        self.output_format_combo = QComboBox()
        for fmt in self.output_formats:
            self.output_format_combo.addItem(fmt)
        
        # Default to first format
        if self.output_formats:
            # If there's a PDF option, default to that (common case)
            pdf_index = self.output_formats.index("pdf") if "pdf" in self.output_formats else -1
            if pdf_index >= 0:
                self.output_format_combo.setCurrentIndex(pdf_index)
        
        # Connect to slot to update parameter fields
        self.output_format_combo.currentTextChanged.connect(self.on_output_format_changed)
        
        output_layout.addRow("Output Format:", self.output_format_combo)
        
        # Output path
        output_path_layout = QHBoxLayout()
        
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setReadOnly(True)
        
        # Default output path with current format
        self._update_default_output_path()
        
        output_path_layout.addWidget(self.output_path_edit)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.on_browse_clicked)
        output_path_layout.addWidget(self.browse_button)
        
        output_layout.addRow("Output File:", output_path_layout)
        
        layout.addWidget(output_group)
        
        # Parameters section
        self.params_group = QGroupBox("Conversion Parameters")
        self.params_layout = QFormLayout(self.params_group)
        
        # Parameter fields will be dynamically created
        self.param_widgets = {}
        self._update_parameter_fields()
        
        layout.addWidget(self.params_group)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.on_accepted)
        button_box.rejected.connect(self.reject)
        
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Convert")
        
        layout.addWidget(button_box)
    
    def _get_available_output_formats(self) -> List[str]:
        """Get the list of available output formats.
        
        Returns:
            List of output formats available for the input format.
        """
        if not self.input_format:
            return []
        
        conversion_map = self.registry.get_conversion_map()
        if self.input_format not in conversion_map:
            return []
        
        return sorted(conversion_map[self.input_format])
    
    def _update_default_output_path(self):
        """Update the default output path based on the selected format."""
        input_path = Path(self.input_path)
        current_format = self.output_format_combo.currentText()
        
        if not current_format:
            return
        
        # Get extensions for the format
        extensions = self.registry.get_format_extensions(current_format)
        if not extensions:
            extensions = [current_format]
        
        # Use first extension
        output_path = input_path.with_suffix(f".{extensions[0]}")
        self.output_path_edit.setText(str(output_path))
    
    def _update_parameter_fields(self):
        """Update parameter fields based on the selected output format."""
        # Clear existing fields
        for widget in self.param_widgets.values():
            widget.setParent(None)
        self.param_widgets.clear()
        
        # Get parameters for current format
        current_format = self.output_format_combo.currentText()
        
        # Get converter for input -> output format
        converter = self.registry.get_converter(self.input_format, current_format)
        if not converter:
            return
        
        # Get parameter definitions
        params = converter.get_parameters()
        
        # Create fields for parameters
        for group_name, group_params in params.items():
            # Skip groups that don't match the current output format
            if group_name != current_format and group_name != "general":
                continue
            
            for param_name, param_def in group_params.items():
                # Create appropriate widget based on parameter type
                param_type = param_def.get("type", "string")
                param_default = param_def.get("default")
                param_desc = param_def.get("description", "")
                
                # Special handling for delimiter parameter in CSV/TSV conversions
                if param_name == "delimiter" and current_format in ["csv", "tsv"]:
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
                    
                    # Set default value
                    default_index = 0  # Default to comma
                    if param_default == "\t":
                        default_index = 2  # Tab
                    elif param_default == ";":
                        default_index = 1  # Semicolon
                    elif param_default == "|":
                        default_index = 3  # Pipe
                    elif param_default == " ":
                        default_index = 4  # Space
                        
                    widget.setCurrentIndex(default_index)
                    
                elif param_type == "string":
                    widget = QLineEdit()
                    if param_default is not None:
                        widget.setText(str(param_default))
                
                elif param_type == "number":
                    if param_def.get("int", False):
                        widget = QSpinBox()
                        if "min" in param_def:
                            widget.setMinimum(int(param_def["min"]))
                        if "max" in param_def:
                            widget.setMaximum(int(param_def["max"]))
                    else:
                        widget = QDoubleSpinBox()
                        if "min" in param_def:
                            widget.setMinimum(float(param_def["min"]))
                        if "max" in param_def:
                            widget.setMaximum(float(param_def["max"]))
                    
                    if param_default is not None:
                        widget.setValue(float(param_default))
                
                elif param_type == "boolean":
                    widget = QCheckBox()
                    if param_default is not None:
                        widget.setChecked(bool(param_default))
                
                elif param_type == "select":
                    widget = QComboBox()
                    options = param_def.get("options", [])
                    for option in options:
                        widget.addItem(str(option))
                    
                    if param_default is not None:
                        index = widget.findText(str(param_default))
                        if index >= 0:
                            widget.setCurrentIndex(index)
                
                else:
                    # Default to string input
                    widget = QLineEdit()
                    if param_default is not None:
                        widget.setText(str(param_default))
                
                # Set tooltip with description
                widget.setToolTip(param_desc)
                
                # Store widget and add to layout
                self.param_widgets[f"{group_name}.{param_name}"] = widget
                self.params_layout.addRow(f"{param_name}:", widget)
    
    def _get_parameter_values(self) -> Dict[str, Any]:
        """Get the current parameter values.
        
        Returns:
            Dictionary of parameter values.
        """
        params = {}
        
        for param_key, widget in self.param_widgets.items():
            # Get group and parameter name
            parts = param_key.split(".")
            if len(parts) != 2:
                continue
            
            group_name, param_name = parts
            
            # Get value based on widget type
            # Special handling for delimiter ComboBox
            if param_key.endswith(".delimiter") and isinstance(widget, QComboBox):
                # Get the actual delimiter value, not the display text
                value = widget.currentData()
            elif isinstance(widget, QLineEdit):
                value = widget.text()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            else:
                continue
            
            # Store in params dictionary
            params[param_name] = value
        
        return params
    
    def get_conversion_result(self) -> Optional[Dict[str, Any]]:
        """Get the result of the conversion.
        
        Returns:
            Dictionary with conversion result, or None if conversion failed
            or was not performed.
        """
        return self.conversion_result
    
    @pyqtSlot(str)
    def on_output_format_changed(self, format_name: str):
        """Handle output format change.
        
        Args:
            format_name: Name of the selected format.
        """
        # Update output path
        self._update_default_output_path()
        
        # Update parameter fields
        self._update_parameter_fields()
    
    @pyqtSlot()
    def on_browse_clicked(self):
        """Handle browse button click."""
        # Get current output path
        current_path = self.output_path_edit.text()
        
        # Get directory and filename
        directory = os.path.dirname(current_path) if current_path else ""
        filename = os.path.basename(current_path) if current_path else ""
        
        # Get current format
        current_format = self.output_format_combo.currentText()
        
        # Get file extensions for format
        extensions = self.registry.get_format_extensions(current_format)
        if not extensions:
            extensions = [current_format]
        
        # Create filter string
        filter_parts = []
        for ext in extensions:
            filter_parts.append(f"*.{ext}")
        
        filter_str = f"{current_format.upper()} files ({' '.join(filter_parts)})"
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Output File",
            os.path.join(directory, filename),
            filter_str
        )
        
        if file_path:
            self.output_path_edit.setText(file_path)
    
    @pyqtSlot()
    def on_accepted(self):
        """Handle dialog acceptance."""
        # Get parameters
        parameters = self._get_parameter_values()
        
        # Get output path
        output_path = self.output_path_edit.text()
        if not output_path:
            QMessageBox.warning(
                self,
                "Missing Output Path",
                "Please specify an output file path."
            )
            return
        
        # Confirm overwrite if file exists
        if os.path.exists(output_path):
            result = QMessageBox.question(
                self,
                "Confirm Overwrite",
                f"The file {output_path} already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if result != QMessageBox.StandardButton.Yes:
                return
        
        # Disable controls
        self.setEnabled(False)
        self.progress_bar.show()
        
        # Start conversion thread
        self.conversion_thread = ConversionThread(
            self.engine,
            self.input_path,
            output_path,
            parameters
        )
        
        self.conversion_thread.conversion_complete.connect(self.on_conversion_complete)
        self.conversion_thread.start()
    
    @pyqtSlot(bool, dict)
    def on_conversion_complete(self, success: bool, result: Dict[str, Any]):
        """Handle conversion completion.
        
        Args:
            success: Whether the conversion was successful.
            result: Conversion result or error information.
        """
        # Hide progress bar
        self.progress_bar.hide()
        
        # Re-enable controls
        self.setEnabled(True)
        
        if success:
            self.conversion_result = result
            
            # Show success in status bar if parent is MainWindow
            if hasattr(self.parent(), "statusBar"):
                self.parent().statusBar().showMessage("Conversion successful")
            
            # Accept dialog
            self.accept()
        else:
            # Show error message
            error_msg = result.get("error", "Unknown error")
            QMessageBox.critical(
                self,
                "Conversion Failed",
                f"An error occurred during conversion:\n{error_msg}"
            )
            
            # Show error in status bar if parent is MainWindow
            if hasattr(self.parent(), "statusBar"):
                self.parent().statusBar().showMessage("Conversion failed")