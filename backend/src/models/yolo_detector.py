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
from backend.src.utils.preprocessing import preprocess_image


class YOLODetector:

    def __init__(
        self,
        model_path: Optional[Path] = None,
        confidence_threshold: float = YOLO_CONFIDENCE_THRESHOLD,
    ):

        self.model_path = model_path or MODEL_WEIGHTS_PATH
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.model_loaded = False
        self.load_time_ms = None

        logger.info(f"YOLODetector initialized with threshold: {confidence_threshold}")
        logger.info(f"Model path: {self.model_path}")

    def load_model(self):
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
        if not self.model_loaded:
            raise RuntimeError(ERROR_MODEL_NOT_LOADED)

        logger.info(f"Inference - Image: {image.shape}, {image.dtype}")

        # Preprocess: histogram equalization only
        image = preprocess_image(image)
        logger.info(f"Preprocessed: {image.shape}, {image.dtype}")

        start_time = time.time()

        # YOLO auto-handles: resize, normalize, letterbox, grayscale→RGB
        results = self.model.predict(
            image,
            conf=self.confidence_threshold,
            verbose=False,
            imgsz=1024,
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
                        },
                    }

                    detections.append(detection)

        inference_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Found {len(detections)} detections in {inference_time_ms}ms")

        return detections

    def classify_confidence_tier(self, confidence: float) -> str:
        if confidence > YOLO_CONFIDENCE_HIGH:
            return "high"
        elif confidence >= YOLO_CONFIDENCE_MEDIUM:
            return "medium"
        else:
            return "low"

    def add_vietnamese_labels_and_health_info(
        self, detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
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
        draw_low_confidence: bool = False,
    ) -> np.ndarray:
        # Convert to PIL for drawing
        if len(image.shape) == 2:
            # Grayscale to RGB
            pil_image = Image.fromarray(image).convert("RGB")
        else:
            pil_image = Image.fromarray(image)

        draw = ImageDraw.Draw(pil_image)

        font = None
        font_size = 48  # Even larger font for better visibility
        font_paths = [
            "C:/Windows/Fonts/arialuni.ttf",  # Arial Unicode MS (best for Vietnamese)
            "C:/Windows/Fonts/arial.ttf",  # Arial
            "C:/Windows/Fonts/segoeui.ttf",  # Segoe UI
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux fallback
        ]
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                logger.debug(f"Loaded font: {font_path} with size {font_size}")
                break
            except:
                continue
        if font is None:
            logger.warning("Could not load TrueType font, using default font")
            font = ImageFont.load_default()

        colors = {
            "high": (255, 0, 0),  # Red for high confidence
            "medium": (255, 165, 0),  # Orange for medium confidence
            "low": (128, 128, 128),  # Gray for low confidence
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
                    width=3,
                )
            else:
                # Dashed box (draw segments)
                self._draw_dashed_rectangle(
                    draw,
                    [(bbox["x1"], bbox["y1"]), (bbox["x2"], bbox["y2"])],
                    outline=color,
                    width=2,
                    dash_length=10,
                )

            # Draw label with Vietnamese text - T045
            class_name_vi = det["class_name_vi"]
            confidence = det["confidence"]
            label = f"{class_name_vi} {confidence:.0%}"

            # Calculate text position with padding
            text_padding = 8
            label_x = bbox["x1"]
            label_y = bbox["y1"] - font_size - text_padding * 2

            # If label goes above image, put it below the top of bbox
            if label_y < 0:
                label_y = bbox["y1"] + 5

            # Background for text with padding
            bbox_text = draw.textbbox(
                (label_x + text_padding, label_y + text_padding), label, font=font
            )
            # Expand background box for padding
            background_box = [
                bbox_text[0] - text_padding,
                bbox_text[1] - text_padding,
                bbox_text[2] + text_padding,
                bbox_text[3] + text_padding,
            ]
            draw.rectangle(background_box, fill=color)

            # Draw text in yellow with bold effect (draw multiple times slightly offset)
            text_pos = (label_x + text_padding, label_y + text_padding)
            # Draw shadow for better readability
            draw.text(
                (text_pos[0] + 2, text_pos[1] + 2), label, fill=(0, 0, 0), font=font
            )
            # Draw main text in yellow
            draw.text(text_pos, label, fill=(255, 255, 0), font=font)

        # Convert back to numpy
        annotated_image = np.array(pil_image)

        logger.info(
            f"Drew {len([d for d in detections if d['confidence_tier'] != 'low' or draw_low_confidence])} bounding boxes"
        )

        return annotated_image

    def _draw_dashed_rectangle(self, draw, coords, outline, width=1, dash_length=10):
        x1, y1 = coords[0]
        x2, y2 = coords[1]

        # Top edge
        for x in range(x1, x2, dash_length * 2):
            draw.line(
                [(x, y1), (min(x + dash_length, x2), y1)], fill=outline, width=width
            )

        # Bottom edge
        for x in range(x1, x2, dash_length * 2):
            draw.line(
                [(x, y2), (min(x + dash_length, x2), y2)], fill=outline, width=width
            )

        # Left edge
        for y in range(y1, y2, dash_length * 2):
            draw.line(
                [(x1, y), (x1, min(y + dash_length, y2))], fill=outline, width=width
            )

        # Right edge
        for y in range(y1, y2, dash_length * 2):
            draw.line(
                [(x2, y), (x2, min(y + dash_length, y2))], fill=outline, width=width
            )

    def detect_and_annotate(
        self, image: np.ndarray
    ) -> Tuple[np.ndarray, List[Dict[str, Any]], bool]:
        if not self.model_loaded:
            self.load_model()

        # Run detection
        detections = self.predict(image)

        # Check if normal (no detections above threshold)
        is_normal = len(detections) == 0

        if is_normal:
            logger.info("No abnormalities detected")
            if len(image.shape) == 2:
                annotated_image = np.stack([image] * 3, axis=-1)
            else:
                annotated_image = image.copy()
            return annotated_image, [], True

        # Add Vietnamese labels + health info
        detections = self.add_vietnamese_labels_and_health_info(detections)

        # Draw bounding boxes
        annotated_image = self.draw_bounding_boxes(image, detections)

        logger.info(f"Detection complete - {len(detections)} abnormalities found")

        return annotated_image, detections, False


_detector_instance = None


def get_detector() -> YOLODetector:

    global _detector_instance

    if _detector_instance is None:
        _detector_instance = YOLODetector()
        logger.info("Created new YOLODetector singleton instance")

    return _detector_instance


__all__ = ["YOLODetector", "get_detector"]
