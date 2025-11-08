"""
Detection API endpoints for chest X-ray abnormality detection.

Provides endpoints for running YOLOv11s disease detection on uploaded images.
"""

import time
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status
from loguru import logger
from pydantic import BaseModel, Field

from backend.src.models.yolo_detector import get_detector
from backend.src.utils.image_utils import numpy_to_base64
from backend.src.api.routes.filters import IMAGE_STORAGE
from backend.src.config.settings import (
    ERROR_INVALID_IMAGE_ID,
    ERROR_DETECTION_FAILED,
    PERFORMANCE_TARGET_DETECTION,
)


# Router for detection endpoints
router = APIRouter(tags=["detection"])


# Request/Response models
class DetectionRequest(BaseModel):
    """Request model for detection analysis."""
    
    image_id: str = Field(..., description="UUID of uploaded image")
    draw_low_confidence: bool = Field(
        default=False,
        description="Whether to draw low confidence (<40%) bounding boxes"
    )


class BoundingBox(BaseModel):
    """Bounding box coordinates."""
    
    x1: int
    y1: int
    x2: int
    y2: int


class Detection(BaseModel):
    """Single detection result."""
    
    class_id: int
    class_name_en: str
    class_name_vi: str
    confidence: float
    confidence_tier: str
    bbox: BoundingBox
    health_description: str
    health_warning: str


class DetectionResponse(BaseModel):
    """Response model for detection analysis."""
    
    success: bool
    is_normal: bool = Field(description="True if no abnormalities detected (T049)")
    detections: List[Detection] = Field(default_factory=list)
    annotated_image: str = Field(description="Base64-encoded annotated image")
    processing_time_ms: int
    num_detections: int


class ErrorResponse(BaseModel):
    """Error response model (T050)."""
    
    success: bool = False
    error: str
    error_code: str


@router.post(
    "/detect/analyze",
    response_model=DetectionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image ID"},
        500: {"model": ErrorResponse, "description": "Detection processing failed"},
    },
)
async def analyze_image(request: DetectionRequest):
    """
    Analyze chest X-ray image for abnormalities using YOLOv11s (T048).
    
    This endpoint performs disease detection on a previously uploaded image
    and returns detected abnormalities with Vietnamese labels, confidence scores,
    bounding boxes, and health information.
    
    **Confidence Tiers:**
    - **High (>70%)**: Solid red bounding box - high confidence detection
    - **Medium (40-70%)**: Dashed orange bounding box - moderate confidence
    - **Low (<40%)**: Filtered out by default (unless draw_low_confidence=True)
    
    **Normal Classification (T049):**
    - If no detections meet the confidence threshold (≥40%), image is classified as "Normal"
    
    Args:
        request: Detection request with image_id and drawing options
        
    Returns:
        DetectionResponse with annotated image, detections, and health info
        
    Raises:
        HTTPException 400: Invalid or expired image ID (T050)
        HTTPException 500: Detection processing failed (T050)
    """
    logger.info(f"[DETECTION] Analyzing image: {request.image_id}")
    start_time = time.time()
    
    try:
        # Retrieve image from storage
        if request.image_id not in IMAGE_STORAGE:
            logger.warning(f"[DETECTION] Invalid image ID: {request.image_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": "ID ảnh không hợp lệ hoặc đã hết hạn. Vui lòng tải lên ảnh mới.",
                    "error_code": "INVALID_IMAGE_ID",
                },
            )
        
        # Get image data from storage
        image_data = IMAGE_STORAGE[request.image_id]
        numpy_image = image_data["image_array"]
        logger.info(
            f"[DETECTION] Retrieved image from storage: "
            f"{image_data['metadata']['width']}x{image_data['metadata']['height']}"
        )
        
        # Get YOLO detector instance
        detector = get_detector()
        
        # Run detection pipeline
        try:
            annotated_image, detections, is_normal = detector.detect_and_annotate(
                numpy_image,
                return_enhanced=True
            )
        except Exception as detection_error:
            logger.error(f"[DETECTION] Detection failed: {str(detection_error)}")
            logger.exception(detection_error)
            # T050: Vietnamese error message
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "success": False,
                    "error": "Phát hiện bệnh thất bại. Vui lòng thử lại hoặc sử dụng ảnh khác.",
                    "error_code": "DETECTION_FAILED",
                },
            )
        
        # Convert annotated image to base64
        annotated_base64 = numpy_to_base64(annotated_image)
        
        # Calculate processing time
        end_time = time.time()
        processing_time_ms = int((end_time - start_time) * 1000)
        
        # Log performance (T047)
        logger.info(
            f"[DETECTION] Complete - {len(detections)} detections in {processing_time_ms}ms "
            f"(target: {int(PERFORMANCE_TARGET_DETECTION * 1000)}ms)"
        )
        
        if processing_time_ms > PERFORMANCE_TARGET_DETECTION * 1000:
            logger.warning(
                f"[DETECTION] Performance target exceeded: {processing_time_ms}ms > "
                f"{int(PERFORMANCE_TARGET_DETECTION * 1000)}ms"
            )
        
        # Build response
        response = DetectionResponse(
            success=True,
            is_normal=is_normal,  # T049: Normal classification flag
            detections=[
                Detection(
                    class_id=det["class_id"],
                    class_name_en=det["class_name_en"],
                    class_name_vi=det["class_name_vi"],
                    confidence=det["confidence"],
                    confidence_tier=det["confidence_tier"],
                    bbox=BoundingBox(**det["bbox"]),
                    health_description=det["health_description"],
                    health_warning=det["health_warning"],
                )
                for det in detections
            ],
            annotated_image=annotated_base64,
            processing_time_ms=processing_time_ms,
            num_detections=len(detections),
        )
        
        # Log result summary
        if is_normal:
            logger.success(f"[DETECTION] Image classified as NORMAL")
        else:
            logger.success(f"[DETECTION] Found {len(detections)} abnormalities:")
            for det in detections:
                logger.info(
                    f"  - {det['class_name_vi']} ({det['class_name_en']}): "
                    f"{det['confidence']:.1%} [{det['confidence_tier']}]"
                )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Handle unexpected errors (T050)
        logger.error(f"[DETECTION] Unexpected error: {str(e)}")
        logger.exception(e)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau.",
                "error_code": "INTERNAL_ERROR",
            },
        )


@router.get("/detect/health")
async def health_check():
    """
    Health check endpoint for detection service.
    
    Returns:
        Service status and model loading state
    """
    detector = get_detector()
    
    return {
        "success": True,
        "service": "detection",
        "model_loaded": detector.model_loaded,
        "model_path": str(detector.model_path),
        "confidence_threshold": detector.confidence_threshold,
    }


__all__ = ["router"]
