import logging
import logging.config
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

class Logger:
    """Logger configuration and management."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._setup_logging()
    
    def _setup_logging(self, config_path: Optional[str] = None) -> None:
        """Set up logging configuration.
        
        Args:
            config_path: Path to logging configuration file. If None, uses default config.
        """
        if config_path is None:
            config_path = os.path.join("config", "logging.yaml")
        
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            
            # Create log directory if it doesn't exist
            log_dir = Path(config.get("handlers", {}).get("file", {}).get("filename", "logs")).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            logging.config.dictConfig(config)
        except Exception as e:
            # Fallback to basic configuration if file loading fails
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler("logs/research_assistant.log")
                ]
            )
            logging.warning(f"Failed to load logging config: {e}. Using basic configuration.")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance.
        
        Args:
            name: Logger name (typically __name__ of the calling module)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        return logging.getLogger(name)
    
    @staticmethod
    def set_level(level: str) -> None:
        """Set the logging level for the root logger.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        logging.getLogger().setLevel(getattr(logging, level.upper()))
    
    @staticmethod
    def add_handler(handler: logging.Handler) -> None:
        """Add a handler to the root logger.
        
        Args:
            handler: Logging handler to add
        """
        logging.getLogger().addHandler(handler)
    
    @staticmethod
    def remove_handler(handler: logging.Handler) -> None:
        """Remove a handler from the root logger.
        
        Args:
            handler: Logging handler to remove
        """
        logging.getLogger().removeHandler(handler)
    
    @staticmethod
    def get_handlers() -> list[logging.Handler]:
        """Get all handlers of the root logger.
        
        Returns:
            list[logging.Handler]: List of handlers
        """
        return logging.getLogger().handlers
    
    @staticmethod
    def clear_handlers() -> None:
        """Remove all handlers from the root logger."""
        for handler in logging.getLogger().handlers[:]:
            logging.getLogger().removeHandler(handler)
    
    @staticmethod
    def get_log_level() -> int:
        """Get the current logging level.
        
        Returns:
            int: Current logging level
        """
        return logging.getLogger().getEffectiveLevel()
    
    @staticmethod
    def is_enabled_for(level: str) -> bool:
        """Check if logging is enabled for the given level.
        
        Args:
            level: Logging level to check
            
        Returns:
            bool: True if logging is enabled for the level
        """
        return logging.getLogger().isEnabledFor(getattr(logging, level.upper())) 