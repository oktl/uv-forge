"""Logging configuration for UV Forger.

This module configures loguru with console and rotating file handlers,
including a separate error log for long-term retention.
"""

import sys

from loguru import logger

from uv_forger.core.constants import LOG_DIR


def setup_logging():
    """Configure loguru logging for the application."""

    # Remove default handler to avoid duplicate console output
    logger.remove()

    # Add console handler with custom format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",  # Only show INFO and above in console
    )

    # Create logs directory in platform data dir
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_folder = LOG_DIR

    # Add file handler for all logs
    logger.add(
        log_folder / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="00:00",  # New file each day
        retention="30 days",
        compression="zip",  # Compress old logs
    )

    # Add separate error log
    logger.add(
        log_folder / "errors_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",  # Only errors and critical
        rotation="00:00",
        retention="90 days",  # Keep error logs longer
        compression="zip",
    )

    logger.info("Logging configured successfully")
