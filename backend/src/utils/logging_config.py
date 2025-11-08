"""
Logging configuration using loguru.

This module configures comprehensive logging for the application with
file rotation, console output, and customizable log levels.
"""

import sys
from pathlib import Path
from loguru import logger

from backend.src.config.settings import (
    LOG_DIR,
    LOG_ROTATION,
    LOG_RETENTION,
    LOG_LEVEL,
    LOG_FORMAT,
)


def setup_logging() -> None:
    """
    Configure loguru logger with file and console output.

    Sets up:
    - Console logging with colored output
    - File logging with rotation (10 MB) and retention (7 days)
    - Custom log format with timestamps, levels, and context
    """
    # Remove default logger
    logger.remove()

    # Add console logger with colors
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        colorize=True,
    )

    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Add file logger with rotation and retention
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


def get_logger():
    """
    Get the configured logger instance.

    Returns:
        Loguru logger instance
    """
    return logger


# Example usage functions for different log levels
def log_image_upload(filename: str, size_bytes: int, format: str) -> None:
    """Log image upload event."""
    size_kb = size_bytes / 1024
    logger.info(f"Image uploaded: {filename}, size: {size_kb:.2f}KB, format: {format}")


def log_filter_start(filter_name: str, image_id: str) -> None:
    """Log filter processing start."""
    logger.info(f"Starting filter '{filter_name}' on image_id={image_id}")


def log_filter_complete(filter_name: str, processing_time_ms: int) -> None:
    """Log filter processing completion."""
    logger.info(f"Filter '{filter_name}' completed in {processing_time_ms}ms")


def log_detection_start(image_id: str) -> None:
    """Log detection start."""
    logger.info(f"Starting disease detection on image_id={image_id}")


def log_detection_complete(num_detections: int, inference_time_ms: int) -> None:
    """Log detection completion."""
    logger.info(
        f"Detection completed in {inference_time_ms}ms, found {num_detections} abnormalities"
    )


def log_error(operation: str, error: Exception) -> None:
    """Log error with context."""
    logger.error(f"{operation} failed: {str(error)}")
    logger.exception(error)


def log_api_request(method: str, path: str, client_host: str) -> None:
    """Log API request."""
    logger.debug(f"API Request: {method} {path} from {client_host}")


def log_api_response(
    method: str, path: str, status_code: int, response_time_ms: int
) -> None:
    """Log API response."""
    logger.debug(
        f"API Response: {method} {path} -> {status_code} ({response_time_ms}ms)"
    )


def log_model_load(model_path: str, load_time_ms: int) -> None:
    """Log model loading."""
    logger.info(f"Model loaded from {model_path} in {load_time_ms}ms")


def log_validation_error(field: str, error_message: str) -> None:
    """Log validation error."""
    logger.warning(f"Validation error for '{field}': {error_message}")
