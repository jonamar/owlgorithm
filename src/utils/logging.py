"""Centralized logging configuration for the Duolingo tracker."""
from __future__ import annotations

import logging
import os
from typing import Optional

from config import app_config as cfg


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    console: bool = True
) -> logging.Logger:
    """Set up a logger with consistent formatting and handlers.
    
    Args:
        name: Logger name
        log_file: Optional log file path (defaults to logs/<name>.log)
        level: Logging level
        console: Whether to also log to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    if log_file is None:
        os.makedirs(cfg.LOG_DIR, exist_ok=True)
        log_file = os.path.join(cfg.LOG_DIR, f"{name}.log")
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_tracker_logger(name: str = "duolingo_tracker") -> logging.Logger:
    """Get the main tracker logger with standard configuration."""
    return setup_logger(name) 