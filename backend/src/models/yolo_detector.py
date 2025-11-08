"""
YOLO Detector for Chest X-Ray Abnormality Detection.

This module provides a wrapper around YOLOv11s for detecting abnormalities
in chest X-ray images with Vietnamese labeling and health information.
"""

import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from loguru import logger

from backend.src.config.settings import (
    MODEL_WEIGHTS_PATH,
    YOLO_CONFIDENCE_THRESHOLD,
    YOLO_CONFIDENCE_HIGH,
    YOLO_CONFIDENCE_MEDIUM,
    ERROR_MODEL_NOT_LOADED,
)
from backend.src.utils.class_mapping import get_vietnamese_name
from backend.src.utils.health_info import get_health_info


class YOLODetector:
    """
    Wrapper class for YOLOv11s model for chest X-ray abnormality detection.
    
    Features:
    - Load and cache YOLO model
    - Perform inference with confidence filtering
    - Classify detections by confidence tier
    - Draw bounding boxes with Vietnamese labels
    - Provide health information for detected conditions
    """
    
    def __init__(self, model_path: Optional[Path] = None, confidence_threshold: float = YOLO_CONFIDENCE_THRESHOLD):
        """
        Initialize YOLO detector.
        
        Args:
            model_path: Path to model weights file (default: from settings)
            confidence_threshold: Minimum confidence for detection (default: 0.4)
        """
        self.model_path = model_path or MODEL_WEIGHTS_PATH
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.model_loaded = False
        self.load_time_ms = None
        
        logger.info(f"YOLODetector initialized with threshold: {confidence_threshold}")
        logger.info(f"Model path: {self.model_path}")
    
    def load_model(self):
        """
        Load YOLO model from weights file.
        
        Raises:
            FileNotFoundError: If model weights file doesn't exist
            Exception: If model loading fails
        """
        if self.model_loaded:
            logger.debug("Model already loaded, skipping")
            return
        
        if not self.model_path.exists():
            error_msg = f"Model weights not found at {self.model_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logger.info(f"Loading YOLO model from {self.model_path}...")
        start_time = time.time()
        
        try:
            from ultralytics import YOLO
            self.model = YOLO(str(self.model_path))
            
            end_time = time.time()
            self.load_time_ms = int((end_time - start_time) * 1000)
            self.model_loaded = True
            
            logger.success(f"Model loaded successfully in {self.load_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {str(e)}")
            logger.exception(e)
            raise
    
    def predict(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Perform inference on chest X-ray image.
        
        Args:
            image: Input image as numpy array (H, W) or (H, W, 3)
            
        Returns:
            List of detection dictionaries with class, confidence, bbox
            
        Raises:
            RuntimeError: If model not loaded
        """
        if not self.model_loaded:
            error_msg = ERROR_MODEL_NOT_LOADED
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info(f"Running YOLO inference - Image shape: {image.shape}, dtype: {image.dtype}")
        start_time = time.time()
        
        # Run inference
        results = self.model.predict(
            image,
            conf=self.confidence_threshold,
            verbose=False
        )
        
        end_time = time.time()
        inference_time_ms = int((end_time - start_time) * 1000)
        
        # Parse results
        detections = []
        
        if len(results) > 0:
            result = results[0]  # First image result
            
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes
                
                for box in boxes:
                    # Extract detection data
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox_xyxy = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                    
                    # Get class name (English)
                    class_name = self.model.names[class_id]
                    
                    # Create detection dictionary
                    detection = {
                        "class_id": class_id,
                        "class_name_en": class_name,
                        "confidence": confidence,
                        "bbox": {
                            "x1": int(bbox_xyxy[0]),
                            "y1": int(bbox_xyxy[1]),
                            "x2": int(bbox_xyxy[2]),
                            "y2": int(bbox_xyxy[3]),
                        }
                    }
                    
                    detections.append(detection)
        
        logger.info(f"YOLO inference complete - {len(detections)} detections found in {inference_time_ms}ms")
        
        # Log detected classes (T047)
        if detections:
            for det in detections:
                logger.info(
                    f"  - {det['class_name_en']}: {det['confidence']:.3f} "
                    f"at [{det['bbox']['x1']}, {det['bbox']['y1']}, {det['bbox']['x2']}, {det['bbox']['y2']}]"
                )
        else:
            logger.info("  - No abnormalities detected (Normal)")
        
        return detections
    
    def classify_confidence_tier(self, confidence: float) -> str:
        """
        Classify confidence score into tier (T044).
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            Tier name: 'high', 'medium', or 'low'
        """
        if confidence > YOLO_CONFIDENCE_HIGH:
            return "high"
        elif confidence >= YOLO_CONFIDENCE_MEDIUM:
            return "medium"
        else:
            return "low"
    
    def add_vietnamese_labels_and_health_info(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add Vietnamese labels, confidence tiers, and health information to detections (T046).
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Enhanced detection dictionaries with Vietnamese info
        """
        enhanced_detections = []
        
        for det in detections:
            # Get Vietnamese label
            class_name_en = det["class_name_en"]
            class_name_vi = get_vietnamese_name(class_name_en)
            
            # Get confidence tier (T044)
            confidence_tier = self.classify_confidence_tier(det["confidence"])
            
            # Get health information (T046)
            health_info = get_health_info(class_name_en)
            
            # Create enhanced detection
            enhanced_det = {
                **det,
                "class_name_vi": class_name_vi,
                "confidence_tier": confidence_tier,
                "health_description": health_info.get("description", ""),
                "health_warning": health_info.get("warning", ""),
            }
            
            enhanced_detections.append(enhanced_det)
            
            logger.debug(
                f"Enhanced detection: {class_name_en} -> {class_name_vi} "
                f"(tier: {confidence_tier}, conf: {det['confidence']:.3f})"
            )
        
        return enhanced_detections
    
    def draw_bounding_boxes(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]],
        draw_low_confidence: bool = False
    ) -> np.ndarray:
        """
        Draw bounding boxes on image with Vietnamese labels (T045).
        
        Args:
            image: Input image as numpy array
            detections: List of detection dictionaries (with Vietnamese labels)
            draw_low_confidence: Whether to draw low confidence (<40%) boxes
            
        Returns:
            Image with bounding boxes drawn
        """
        # Convert to PIL for drawing
        if len(image.shape) == 2:
            # Grayscale to RGB
            pil_image = Image.fromarray(image).convert("RGB")
        else:
            pil_image = Image.fromarray(image)
        
        draw = ImageDraw.Draw(pil_image)
        
        # Try to load a font (fall back to default if not available)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        colors = {
            "high": (255, 0, 0),      # Red for high confidence
            "medium": (255, 165, 0),  # Orange for medium confidence
            "low": (128, 128, 128),   # Gray for low confidence
        }
        
        for det in detections:
            confidence_tier = det["confidence_tier"]
            
            # Skip low confidence if not drawing them
            if confidence_tier == "low" and not draw_low_confidence:
                continue
            
            bbox = det["bbox"]
            color = colors.get(confidence_tier, (0, 255, 0))
            
            # Draw box (solid for high, dashed for medium) - T045
            if confidence_tier == "high":
                # Solid box
                draw.rectangle(
                    [(bbox["x1"], bbox["y1"]), (bbox["x2"], bbox["y2"])],
                    outline=color,
                    width=3
                )
            else:
                # Dashed box (draw segments)
                self._draw_dashed_rectangle(
                    draw,
                    [(bbox["x1"], bbox["y1"]), (bbox["x2"], bbox["y2"])],
                    outline=color,
                    width=2,
                    dash_length=10
                )
            
            # Draw label with Vietnamese text - T045
            class_name_vi = det["class_name_vi"]
            confidence = det["confidence"]
            label = f"{class_name_vi} {confidence:.0%}"
            
            # Background for text
            bbox_text = draw.textbbox((bbox["x1"], bbox["y1"] - 25), label, font=font)
            draw.rectangle(bbox_text, fill=color)
            draw.text((bbox["x1"], bbox["y1"] - 25), label, fill=(255, 255, 255), font=font)
        
        # Convert back to numpy
        annotated_image = np.array(pil_image)
        
        logger.info(f"Drew {len([d for d in detections if d['confidence_tier'] != 'low' or draw_low_confidence])} bounding boxes")
        
        return annotated_image
    
    def _draw_dashed_rectangle(self, draw, coords, outline, width=1, dash_length=10):
        """
        Draw a dashed rectangle (helper for T045).
        
        Args:
            draw: PIL ImageDraw object
            coords: [(x1, y1), (x2, y2)]
            outline: Color
            width: Line width
            dash_length: Length of each dash
        """
        x1, y1 = coords[0]
        x2, y2 = coords[1]
        
        # Top edge
        for x in range(x1, x2, dash_length * 2):
            draw.line([(x, y1), (min(x + dash_length, x2), y1)], fill=outline, width=width)
        
        # Bottom edge
        for x in range(x1, x2, dash_length * 2):
            draw.line([(x, y2), (min(x + dash_length, x2), y2)], fill=outline, width=width)
        
        # Left edge
        for y in range(y1, y2, dash_length * 2):
            draw.line([(x1, y), (x1, min(y + dash_length, y2))], fill=outline, width=width)
        
        # Right edge
        for y in range(y1, y2, dash_length * 2):
            draw.line([(x2, y), (x2, min(y + dash_length, y2))], fill=outline, width=width)
    
    def detect_and_annotate(
        self,
        image: np.ndarray,
        return_enhanced: bool = True
    ) -> Tuple[np.ndarray, List[Dict[str, Any]], bool]:
        """
        Complete detection pipeline: predict, enhance, and annotate.
        
        Args:
            image: Input image as numpy array
            return_enhanced: Whether to return enhanced detections with health info
            
        Returns:
            Tuple of (annotated_image, detections, is_normal)
        """
        logger.info("Starting complete detection pipeline")
        
        # Ensure model is loaded
        if not self.model_loaded:
            self.load_model()
        
        # Perform detection (T043)
        detections = self.predict(image)
        
        # Check if normal (no detections) - T049
        is_normal = len(detections) == 0
        
        if is_normal:
            logger.info("Image classified as NORMAL (no abnormalities detected)")
            # Return original image for normal cases
            if len(image.shape) == 2:
                annotated_image = np.stack([image] * 3, axis=-1)
            else:
                annotated_image = image.copy()
            
            return annotated_image, [], True
        
        # Enhance detections with Vietnamese labels and health info (T046)
        if return_enhanced:
            detections = self.add_vietnamese_labels_and_health_info(detections)
        
        # Draw bounding boxes (T045)
        annotated_image = self.draw_bounding_boxes(image, detections)
        
        logger.success(f"Detection pipeline complete - {len(detections)} abnormalities found")
        
        return annotated_image, detections, False


# Singleton instance
_detector_instance = None


def get_detector() -> YOLODetector:
    """
    Get singleton YOLO detector instance.
    
    Returns:
        YOLODetector instance
    """
    global _detector_instance
    
    if _detector_instance is None:
        _detector_instance = YOLODetector()
        logger.info("Created new YOLODetector singleton instance")
    
    return _detector_instance


__all__ = ["YOLODetector", "get_detector"]
