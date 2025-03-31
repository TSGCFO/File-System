"""
GUI components for FileConverter.

This package contains the graphical user interface components for 
the FileConverter application, including the main window, dialogs,
and utility functions for GUI operations.
"""

try:
    from PyQt6.QtWidgets import QApplication
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

def check_gui_dependencies():
    """Check if GUI dependencies are available.
    
    Returns:
        bool: True if GUI dependencies are available, False otherwise.
    """
    return GUI_AVAILABLE

# Import main components if GUI dependencies are available
if GUI_AVAILABLE:
    try:
        from fileconverter.gui.main_window import MainWindow
        from fileconverter.gui.conversion_dialog import ConversionDialog
        from fileconverter.gui.settings_dialog import SettingsDialog
        
        __all__ = [
            'MainWindow',
            'ConversionDialog',
            'SettingsDialog',
            'check_gui_dependencies',
            'GUI_AVAILABLE'
        ]
    except ImportError:
        __all__ = ['check_gui_dependencies', 'GUI_AVAILABLE']
else:
    __all__ = ['check_gui_dependencies', 'GUI_AVAILABLE']