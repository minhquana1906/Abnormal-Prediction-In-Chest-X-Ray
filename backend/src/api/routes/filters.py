"""
Filter processing API routes for image upload and filter application.

This module provides endpoints for uploading chest X-ray images,
listing available filters, and applying image processing filters.
All image processing is done in-memory with no file storage.
"""

import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from io import BytesIO

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from pydantic import BaseModel, Field
from loguru import logger

from backend.src.config.settings import (
    MAX_FILE_SIZE_BYTES,
    ALLOWED_IMAGE_FORMATS,
    SESSION_TIMEOUT_MINUTES,
    ERROR_FILE_TOO_LARGE,
    ERROR_INVALID_FORMAT,
    ERROR_CORRUPTED_IMAGE,
    ERROR_INVALID_IMAGE_ID,
    ERROR_FILTER_NOT_FOUND,
    ERROR_PROCESSING_FAILED,
)
from backend.src.utils.image_utils import (
    load_image_from_bytes,
    validate_image_dimensions,
    pil_to_numpy,
    numpy_to_base64,
    get_image_info,
)
from backend.src.filters import get_filter_list, apply_filter

# Router instance
router = APIRouter()

# In-memory storage for uploaded images
# Format: {image_id: {"image_array": np.ndarray, "metadata": dict, "upload_time": datetime}}
IMAGE_STORAGE: Dict[str, dict] = {}


# Vietnamese error messages for user-facing errors
ERROR_MESSAGES_VI = {
    "FILE_TOO_LARGE": f"Kích thước tệp vượt quá giới hạn tối đa. Vui lòng tải lên tệp nhỏ hơn 10MB.",
    "INVALID_FORMAT": "Định dạng tệp không hợp lệ. Chỉ chấp nhận các định dạng: PNG, JPG, JPEG.",
    "CORRUPTED_IMAGE": "Tệp hình ảnh bị hỏng hoặc không thể mở. Vui lòng thử tệp khác.",
    "IMAGE_TOO_SMALL": "Kích thước hình ảnh quá nhỏ. Vui lòng tải lên hình ảnh có độ phân giải cao hơn.",
    "IMAGE_TOO_LARGE": "Kích thước hình ảnh quá lớn. Vui lòng tải lên hình ảnh nhỏ hơn 2048x2048 pixel.",
    "INVALID_IMAGE_ID": "ID hình ảnh không hợp lệ hoặc đã hết hạn. Vui lòng tải lên hình ảnh mới.",
    "FILTER_NOT_FOUND": "Bộ lọc không tồn tại. Vui lòng chọn bộ lọc hợp lệ.",
    "PROCESSING_FAILED": "Xử lý hình ảnh thất bại. Vui lòng thử lại hoặc sử dụng hình ảnh khác.",
    "NO_FILTERS_SELECTED": "Vui lòng chọn ít nhất một bộ lọc để áp dụng.",
    "NETWORK_ERROR": "Lỗi kết nối mạng. Vui lòng kiểm tra kết nối và thử lại.",
}


# Pydantic models for request/response
class UploadResponse(BaseModel):
    """Response model for image upload."""
    image_id: str = Field(..., description="Unique identifier for the uploaded image")
    filename: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., description="File size in bytes")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    format: str = Field(..., description="Image format (PNG, JPEG, JPG)")
    upload_timestamp: str = Field(..., description="ISO 8601 timestamp of upload")


class FilterInfo(BaseModel):
    """Filter metadata information."""
    id: str = Field(..., description="Filter identifier")
    name: str = Field(..., description="Filter display name (English)")
    name_vi: str = Field(..., description="Filter display name (Vietnamese)")
    description: str = Field(..., description="Filter description (English)")
    description_vi: str = Field(..., description="Filter description (Vietnamese)")
    parameters: dict = Field(..., description="Fixed filter parameters")
    output_type: str = Field(..., description="Output type (grayscale, binary, spectrum)")


class FilterListResponse(BaseModel):
    """Response model for filter list."""
    filters: List[FilterInfo] = Field(..., description="List of available filters")


class FilterApplyRequest(BaseModel):
    """Request model for applying filters."""
    image_id: str = Field(..., description="ID of uploaded image")
    filters: List[str] = Field(..., min_items=1, description="List of filter IDs to apply")


class ProcessedImageInfo(BaseModel):
    """Information about a processed image."""
    filter_name: str = Field(..., description="Filter identifier")
    display_name: str = Field(..., description="Filter display name (English)")
    image_base64: str = Field(..., description="Base64-encoded processed image")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class FilterApplyResponse(BaseModel):
    """Response model for filter application."""
    request_id: str = Field(..., description="Unique request identifier")
    results: List[ProcessedImageInfo] = Field(..., description="Processed images")
    total_time_ms: int = Field(..., description="Total processing time in milliseconds")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message (Vietnamese for user-facing errors)")
    details: Optional[dict] = Field(None, description="Additional error context")


def clean_expired_images():
    """Remove images older than SESSION_TIMEOUT_MINUTES from memory."""
    now = datetime.now()
    expired_ids = []
    
    for image_id, data in IMAGE_STORAGE.items():
        upload_time = data["upload_time"]
        if now - upload_time > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            expired_ids.append(image_id)
    
    for image_id in expired_ids:
        del IMAGE_STORAGE[image_id]
        logger.info(f"Cleaned up expired image: {image_id}")
    
    if expired_ids:
        logger.info(f"Removed {len(expired_ids)} expired images from memory")


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_200_OK)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a chest X-ray image for processing (in-memory storage only).
    
    Accepts PNG, JPG, or JPEG files up to 10MB.
    Returns a unique image_id for use with filter/apply endpoint.
    
    Args:
        file: Uploaded image file
        
    Returns:
        UploadResponse with image_id and metadata
        
    Raises:
        HTTPException: 400 for invalid files, 500 for processing errors
    """
    logger.info(f"Upload request received: {file.filename} ({file.content_type})")
    
    # Clean up expired images before processing new upload
    clean_expired_images()
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE_BYTES:
            logger.warning(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE_BYTES})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "FILE_TOO_LARGE",
                    "message": ERROR_MESSAGES_VI["FILE_TOO_LARGE"],
                    "details": {"size_bytes": file_size, "max_bytes": MAX_FILE_SIZE_BYTES}
                }
            )
        
        # Load and validate image
        try:
            pil_image = load_image_from_bytes(file_content)
            validate_image_dimensions(pil_image)
        except ValueError as e:
            logger.error(f"Image validation failed: {str(e)}")
            
            # Determine specific error type
            error_type = "CORRUPTED_IMAGE"
            if "too small" in str(e).lower():
                error_type = "IMAGE_TOO_SMALL"
            elif "too large" in str(e).lower():
                error_type = "IMAGE_TOO_LARGE"
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": error_type,
                    "message": ERROR_MESSAGES_VI[error_type],
                    "details": {"reason": str(e)}
                }
            )
        
        # Validate format
        image_format = pil_image.format
        if image_format not in ALLOWED_IMAGE_FORMATS:
            logger.warning(f"Invalid format: {image_format}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_FORMAT",
                    "message": ERROR_MESSAGES_VI["INVALID_FORMAT"],
                    "details": {"format": image_format, "allowed": ALLOWED_IMAGE_FORMATS}
                }
            )
        
        # Convert to numpy array (grayscale for X-rays)
        image_array = pil_to_numpy(pil_image, grayscale=True)
        
        # Get image metadata
        image_info = get_image_info(pil_image)
        
        # Generate unique image ID
        image_id = str(uuid.uuid4())
        
        # Store in memory
        IMAGE_STORAGE[image_id] = {
            "image_array": image_array,
            "metadata": {
                "filename": file.filename,
                "size_bytes": file_size,
                "width": image_info["width"],
                "height": image_info["height"],
                "format": image_format,
            },
            "upload_time": datetime.now(),
        }
        
        logger.info(
            f"Image uploaded successfully: {image_id} "
            f"({image_info['width']}x{image_info['height']}, {file_size} bytes)"
        )
        logger.debug(f"Current in-memory storage: {len(IMAGE_STORAGE)} images")
        
        # Return response
        return UploadResponse(
            image_id=image_id,
            filename=file.filename,
            size_bytes=file_size,
            width=image_info["width"],
            height=image_info["height"],
            format=image_format,
            upload_timestamp=datetime.now().isoformat() + "Z",
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PROCESSING_FAILED",
                "message": ERROR_MESSAGES_VI["PROCESSING_FAILED"],
                "details": {"reason": str(e)}
            }
        )


@router.get("/filter/list", response_model=FilterListResponse, status_code=status.HTTP_200_OK)
async def list_filters():
    """
    Get list of available image processing filters.
    
    Returns metadata for all 8 implemented filters including names,
    descriptions (English and Vietnamese), and fixed parameters.
    
    Returns:
        FilterListResponse with list of filter metadata
    """
    logger.info("Filter list request received")
    
    try:
        filters = get_filter_list()
        
        logger.info(f"Returning {len(filters)} available filters")
        
        return FilterListResponse(
            filters=[FilterInfo(**f) for f in filters]
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve filter list: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PROCESSING_FAILED",
                "message": ERROR_MESSAGES_VI["PROCESSING_FAILED"],
                "details": {"reason": str(e)}
            }
        )


@router.post("/filter/apply", response_model=FilterApplyResponse, status_code=status.HTTP_200_OK)
async def apply_filters(request: FilterApplyRequest):
    """
    Apply image processing filters to uploaded image.
    
    Accepts image_id and list of filter names. Processes all filters
    in-memory and returns base64-encoded results with timing information.
    
    Args:
        request: FilterApplyRequest with image_id and filter list
        
    Returns:
        FilterApplyResponse with processed images and timing
        
    Raises:
        HTTPException: 400 for invalid image_id/filters, 500 for processing errors
    """
    logger.info(
        f"Filter apply request: image_id={request.image_id}, "
        f"filters={request.filters}"
    )
    
    # Clean up expired images
    clean_expired_images()
    
    # Validate image_id exists
    if request.image_id not in IMAGE_STORAGE:
        logger.warning(f"Invalid or expired image_id: {request.image_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_IMAGE_ID",
                "message": ERROR_MESSAGES_VI["INVALID_IMAGE_ID"],
                "details": {"image_id": request.image_id}
            }
        )
    
    # Validate filter list is not empty
    if not request.filters:
        logger.warning("No filters specified in request")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "NO_FILTERS_SELECTED",
                "message": ERROR_MESSAGES_VI["NO_FILTERS_SELECTED"],
            }
        )
    
    # Get image from storage
    image_data = IMAGE_STORAGE[request.image_id]
    image_array = image_data["image_array"]
    
    logger.info(
        f"Processing image: {image_data['metadata']['filename']} "
        f"({image_data['metadata']['width']}x{image_data['metadata']['height']})"
    )
    
    # Get available filter IDs for validation
    available_filters = {f["id"] for f in get_filter_list()}
    
    # Process each filter
    results = []
    total_start_time = time.time()
    
    for filter_id in request.filters:
        # Validate filter exists
        if filter_id not in available_filters:
            logger.warning(f"Invalid filter requested: {filter_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "FILTER_NOT_FOUND",
                    "message": ERROR_MESSAGES_VI["FILTER_NOT_FOUND"],
                    "details": {
                        "filter": filter_id,
                        "available": list(available_filters)
                    }
                }
            )
        
        try:
            # Apply filter with timing
            filter_start_time = time.time()
            
            filtered_array = apply_filter(filter_id, image_array.copy())
            
            filter_end_time = time.time()
            processing_time_ms = int((filter_end_time - filter_start_time) * 1000)
            
            # Convert to base64
            image_base64 = numpy_to_base64(filtered_array, format="PNG")
            
            # Get filter display name
            filter_metadata = next(f for f in get_filter_list() if f["id"] == filter_id)
            
            results.append(
                ProcessedImageInfo(
                    filter_name=filter_id,
                    display_name=filter_metadata["name"],
                    image_base64=image_base64,
                    processing_time_ms=processing_time_ms,
                )
            )
            
            logger.info(
                f"Filter '{filter_id}' applied successfully "
                f"(processing time: {processing_time_ms}ms)"
            )
            
        except Exception as e:
            logger.error(f"Filter '{filter_id}' processing failed: {str(e)}")
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "PROCESSING_FAILED",
                    "message": ERROR_MESSAGES_VI["PROCESSING_FAILED"],
                    "details": {
                        "filter": filter_id,
                        "reason": str(e)
                    }
                }
            )
    
    total_end_time = time.time()
    total_time_ms = int((total_end_time - total_start_time) * 1000)
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    logger.info(
        f"All filters applied successfully: {len(results)} filters, "
        f"total time: {total_time_ms}ms"
    )
    
    return FilterApplyResponse(
        request_id=request_id,
        results=results,
        total_time_ms=total_time_ms,
    )


# Export router
__all__ = ["router"]
