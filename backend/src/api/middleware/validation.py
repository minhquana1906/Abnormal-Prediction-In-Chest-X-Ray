from fastapi import UploadFile, HTTPException, status

from backend.src.config.settings import (
    MAX_FILE_SIZE_BYTES,
    ALLOWED_IMAGE_FORMATS,
    ALLOWED_MIME_TYPES,
    ERROR_FILE_TOO_LARGE,
    ERROR_INVALID_FORMAT,
    ERROR_CORRUPTED_IMAGE,
)
from backend.src.utils.logging_config import logger, log_validation_error
from backend.src.utils.image_utils import (
    load_image_from_bytes,
    validate_image_dimensions,
)


async def validate_uploaded_file(file: UploadFile) -> bytes:
    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file size
    if file_size > MAX_FILE_SIZE_BYTES:
        log_validation_error("file_size", f"File too large: {file_size} bytes")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=ERROR_FILE_TOO_LARGE,
        )

    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        log_validation_error("content_type", f"Invalid MIME type: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=ERROR_INVALID_FORMAT,
        )

    # Validate file can be opened and is not corrupted
    try:
        image = load_image_from_bytes(content)
    except ValueError as e:
        log_validation_error("image_integrity", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_CORRUPTED_IMAGE
        )

    # Validate image format
    if image.format not in ALLOWED_IMAGE_FORMATS:
        log_validation_error("image_format", f"Invalid format: {image.format}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=ERROR_INVALID_FORMAT,
        )

    # Validate image dimensions
    try:
        validate_image_dimensions(image)
    except ValueError as e:
        log_validation_error("image_dimensions", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    logger.info(
        f"File validation passed: {file.filename}, "
        f"size: {file_size / 1024:.2f}KB, "
        f"format: {image.format}, "
        f"dimensions: {image.size[0]}x{image.size[1]}"
    )

    return content


def validate_filter_name(filter_name: str, available_filters: list) -> None:
    if filter_name not in available_filters:
        log_validation_error("filter_name", f"Unknown filter: {filter_name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filter name: '{filter_name}'. Available filters: {', '.join(available_filters)}",
        )


def validate_filter_list(filter_names: list, available_filters: list) -> None:
    if not filter_names:
        log_validation_error("filter_list", "Empty filter list")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filter list cannot be empty",
        )

    for filter_name in filter_names:
        validate_filter_name(filter_name, available_filters)


def validate_image_id(image_id: str, stored_images: dict) -> None:
    if not image_id:
        log_validation_error("image_id", "Empty image ID")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Image ID is required"
        )

    if image_id not in stored_images:
        log_validation_error("image_id", f"Image not found: {image_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image not found: {image_id}. Image may have expired.",
        )


def validate_confidence_threshold(threshold: float) -> None:
    if not (0.0 <= threshold <= 1.0):
        log_validation_error("confidence_threshold", f"Invalid threshold: {threshold}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Confidence threshold must be between 0.0 and 1.0, got: {threshold}",
        )
