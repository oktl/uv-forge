import sys

from loguru import logger

from app.core.constants import PROJECT_DIR


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

    # Create logs directory relative to the project root
    log_folder = PROJECT_DIR / "logs"
    log_folder.mkdir(exist_ok=True)

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
