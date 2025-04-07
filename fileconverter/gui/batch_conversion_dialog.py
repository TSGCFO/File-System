import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QListWidget, QHBoxLayout, QProgressBar, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt

class BatchConversionDialog(QDialog):
    def __init__(self, engine, registry, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.registry = registry
        self.setWindowTitle("Batch Conversion")
        self.setMinimumSize(600, 400)

        self.layout = QVBoxLayout(self)

        self.select_button = QPushButton("Select Files")
        self.select_button.clicked.connect(self.select_files)
        self.layout.addWidget(self.select_button)

        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)

        self.format_label = QLabel("Select Output Format:")
        self.layout.addWidget(self.format_label)

        self.format_combo = QComboBox()
        all_formats = sorted(self.registry.get_all_output_formats())
        self.format_combo.addItems(all_formats)
        self.layout.addWidget(self.format_combo)

        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        self.convert_button = QPushButton("Start Batch Conversion")
        self.convert_button.clicked.connect(self.run_conversion)
        self.layout.addWidget(self.convert_button)

        self.selected_files = []

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files for Batch Conversion")
        if files:
            self.selected_files = files
            self.file_list.clear()
            self.file_list.addItems(files)

    def run_conversion(self):
        if not self.selected_files:
            QMessageBox.warning(self, "No Files", "Please select files to convert.")
            return

        output_format = self.format_combo.currentText()
        self.progress.setValue(0)
        success_count = 0

        for idx, file_path in enumerate(self.selected_files):
            try:
                result = self.engine.convert(
                    input_path=file_path,
                    output_format=output_format
                )
                success_count += 1 if result else 0
            except Exception as e:
                print(f"Failed to convert {file_path}: {e}")

            self.progress.setValue(int((idx + 1) / len(self.selected_files) * 100))

        QMessageBox.information(
            self, "Batch Conversion Complete",
            f"Successfully converted {success_count} of {len(self.selected_files)} files."
        )