"""
Logging utilities for FileConverter.

This module provides logging setup and utility functions for the
FileConverter package.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Constants
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
DEFAULT_LOG_BACKUP_COUNT = 3


def get_default_log_dir() -> Path:
    """Get the default log directory based on the OS.
    
    Returns:
        Path to the default log directory.
    """
    if sys.platform.startswith("win"):
        # Windows: use %APPDATA%\FileConverter\logs
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "FileConverter" / "logs"
        else:
            return Path.home() / "AppData" / "Roaming" / "FileConverter" / "logs"
    
    elif sys.platform.startswith("darwin"):
        # macOS: use ~/Library/Logs/FileConverter
        return Path.home() / "Library" / "Logs" / "FileConverter"
    
    else:
        # Linux/Unix: use ~/.local/share/fileconverter/logs
        return Path.home() / ".local" / "share" / "fileconverter" / "logs"


def setup_logging(
    level: Optional[Union[int, str]] = None,
    log_file: Optional[Union[str, Path]] = None,
    log_format: Optional[str] = None,
    console: bool = True
) -> None:
    """Set up logging for the FileConverter package.
    
    Args:
        level: Log level (e.g., logging.INFO, 'INFO', 20).
        log_file: Path to the log file. If None, logs go to the default location.
        log_format: Format string for log messages.
        console: Whether to log to the console.
    """
    # Get configuration
    from fileconverter.config import get_config
    config = get_config()
    
    # Use provided values or get from config
    if level is None:
        level_str = config.get("logging", "level", default="INFO")
        level = getattr(logging, level_str.upper(), DEFAULT_LOG_LEVEL)
    elif isinstance(level, str):
        level = getattr(logging, level.upper(), DEFAULT_LOG_LEVEL)
    
    if log_format is None:
        log_format = config.get("logging", "format", default=DEFAULT_LOG_FORMAT)
    
    if log_file is None:
        log_file = config.get("logging", "file")
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        log_path = Path(log_file)
        
        # Create directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=DEFAULT_LOG_FILE_SIZE,
            backupCount=DEFAULT_LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configure fileconverter logger
    logger = logging.getLogger("fileconverter")
    logger.setLevel(level)
    
    # Log configuration
    logger.debug(f"Logging initialized at level {level}")
    if log_file:
        logger.debug(f"Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module.
    
    Args:
        name: Name of the module (typically __name__).
    
    Returns:
        Logger instance.
    """
    if name.startswith("fileconverter."):
        # Use the module name as is
        return logging.getLogger(name)
    else:
        # Prefix with "fileconverter." for external modules
        return logging.getLogger(f"fileconverter.{name}")
