import sys
from loguru import logger

from backend.src.config.settings import (
    LOG_DIR,
    LOG_ROTATION,
    LOG_RETENTION,
    LOG_LEVEL,
    LOG_FORMAT,
)


def setup_logging() -> None:

    logger.remove()

    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        colorize=True,
    )

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_file_path = LOG_DIR / "app_{time:YYYY-MM-DD}.log"
    logger.add(
        log_file_path,
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        rotation=LOG_ROTATION,
        retention=LOG_RETENTION,
        compression="zip",  # Compress rotated logs
        enqueue=True,  # Thread-safe logging
    )

    logger.info("Logging configured successfully")
    logger.info(f"Log directory: {LOG_DIR}")
    logger.info(f"Log rotation: {LOG_ROTATION}, retention: {LOG_RETENTION}")


def log_validation_error(field: str, error_message: str) -> None:
    logger.warning(f"Validation error for '{field}': {error_message}")
