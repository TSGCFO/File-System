"""
Configuration management for FileConverter.

This module provides functionality for loading, validating, and accessing
configuration settings for the FileConverter package.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from fileconverter.utils.error_handling import ConfigError
from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Default configuration paths
DEFAULT_CONFIG_PATHS = [
    # System-wide
    Path("/etc/fileconverter/config.yaml"),
    # User-specific
    Path.home() / ".config" / "fileconverter" / "config.yaml",
    # Current directory
    Path("fileconverter.yaml"),
]

# Default configuration settings
DEFAULT_CONFIG = {
    "general": {
        "temp_dir": None,  # Use system default if None
        "preserve_temp_files": False,
        "max_file_size_mb": 100,
    },
    "logging": {
        "level": "INFO",
        "file": None,  # No file logging by default
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    },
    "converters": {
        "document": {
            "enabled": True,
            "pdf": {
                "resolution": 300,
                "compression": "medium",
            },
            "docx": {
                "template": None,
            },
        },
        "spreadsheet": {
            "enabled": True,
            "excel": {
                "date_format": "YYYY-MM-DD",
                "number_format": "#,##0.00",
            },
            "csv": {
                "delimiter": ",",
                "quotechar": '"',
                "encoding": "utf-8",
            },
        },
        "image": {
            "enabled": True,
            "jpeg": {
                "quality": 85,
                "progressive": True,
            },
            "png": {
                "compression": 9,
            },
        },
        "data_exchange": {
            "enabled": True,
            "json": {
                "indent": 2,
                "sort_keys": True,
            },
            "xml": {
                "pretty": True,
                "encoding": "utf-8",
            },
        },
        "archive": {
            "enabled": True,
            "zip": {
                "compression": "deflate",
                "compress_level": 9,
            },
        },
    },
    "gui": {
        "theme": "system",
        "recent_files_limit": 10,
        "show_tooltips": True,
    },
}


class Config:
    """Configuration manager for FileConverter."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Initialize the configuration manager.
        
        Args:
            config_path: Optional path to a configuration file. If None,
                         default paths will be checked.
        """
        self._config: Dict[str, Any] = {}
        self._loaded_path: Optional[Path] = None
        
        # Load configuration
        self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Load configuration from the specified path or default paths.
        
        Args:
            config_path: Optional path to a configuration file.
        
        Raises:
            ConfigError: If the specified configuration file cannot be loaded.
        """
        # Start with default configuration
        self._config = DEFAULT_CONFIG.copy()
        
        # Check specific path if provided
        if config_path:
            path = Path(config_path)
            if not path.exists():
                raise ConfigError(f"Configuration file not found: {path}")
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        self._merge_config(self._config, user_config)
                self._loaded_path = path
                logger.info(f"Loaded configuration from {path}")
                return
            except Exception as e:
                raise ConfigError(f"Failed to load configuration from {path}: {str(e)}")
        
        # Check default paths
        for path in DEFAULT_CONFIG_PATHS:
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        user_config = yaml.safe_load(f)
                        if user_config:
                            self._merge_config(self._config, user_config)
                    self._loaded_path = path
                    logger.info(f"Loaded configuration from {path}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load configuration from {path}: {str(e)}")
        
        logger.info("Using default configuration (no config file found)")
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge two configuration dictionaries.
        
        Args:
            base: Base configuration dictionary to merge into.
            override: Configuration dictionary with values to override.
        """
        for key, value in override.items():
            if (
                key in base and 
                isinstance(base[key], dict) and 
                isinstance(value, dict)
            ):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, *keys: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            *keys: Sequence of keys to navigate the configuration hierarchy.
            default: Default value to return if the key is not found.
        
        Returns:
            The configuration value, or the default if not found.
        """
        if not keys:
            return default
        
        config = self._config
        for key in keys[:-1]:
            if key not in config or not isinstance(config[key], dict):
                return default
            config = config[key]
        
        return config.get(keys[-1], default)
    
    def set(self, value: Any, *keys: str) -> None:
        """Set a configuration value.
        
        Args:
            value: Value to set.
            *keys: Sequence of keys to navigate the configuration hierarchy.
        
        Raises:
            ConfigError: If the keys are invalid or empty.
        """
        if not keys:
            raise ConfigError("No keys specified for setting configuration value")
        
        config = self._config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            elif not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """Save the current configuration to a file.
        
        Args:
            path: Path where to save the configuration. If None,
                 the loaded path will be used, or a default path.
        
        Raises:
            ConfigError: If the configuration cannot be saved.
        """
        if path:
            save_path = Path(path)
        elif self._loaded_path:
            save_path = self._loaded_path
        else:
            save_path = Path.home() / ".config" / "fileconverter" / "config.yaml"
        
        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved configuration to {save_path}")
        except Exception as e:
            raise ConfigError(f"Failed to save configuration to {save_path}: {str(e)}")
    
    @property
    def as_dict(self) -> Dict[str, Any]:
        """Get the complete configuration as a dictionary.
        
        Returns:
            A copy of the configuration dictionary.
        """
        return self._config.copy()


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Get the global configuration instance.
    
    Args:
        config_path: Optional path to a configuration file.
    
    Returns:
        The global Configuration instance.
    """
    global _config_instance
    
    if _config_instance is None or config_path is not None:
        _config_instance = Config(config_path)
    
    return _config_instance
