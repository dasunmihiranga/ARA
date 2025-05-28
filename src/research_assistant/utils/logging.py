import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

import yaml

def setup_logging(
    default_path: str = "config/logging.yaml",
    default_level: int = logging.INFO,
    env_key: str = "LOG_CFG"
) -> None:
    """Set up logging configuration from a YAML file.

    Args:
        default_path: Path to the logging configuration file
        default_level: Default logging level if config file is not found
        env_key: Environment variable that can override the config file path
    """
    path = os.getenv(env_key, default_path)
    if os.path.exists(path):
        with open(path, "rt") as f:
            try:
                config = yaml.safe_load(f)
                # Ensure log directory exists
                log_dir = Path("logs")
                log_dir.mkdir(exist_ok=True)
                logging.config.dictConfig(config)
            except Exception as e:
                print(f"Error in logging configuration: {e}")
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        print(f"Failed to load logging configuration from {path}. Using default config.")

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Name of the logger. If None, returns the root logger.

    Returns:
        A logger instance configured according to the logging configuration.
    """
    return logging.getLogger(name if name else "research_assistant") 