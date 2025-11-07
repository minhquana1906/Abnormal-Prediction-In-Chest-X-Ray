# Data Model

**Feature**: Chest X-Ray Abnormality Detection  
**Date**: 2025-11-08  
**Phase**: 1 - Data Model Design

## Overview

This document defines the data structures, entities, and relationships for the chest X-ray abnormality detection application. **MVP Simplicity**: No database, no persistent storage. All entities are in-memory runtime objects only. Images are processed and results returned immediately without saving to disk.

---

## Core Entities

### 1. UploadedImage

**Description**: Represents a chest X-ray image uploaded by the user

**Attributes**:
- `id`: string - Unique identifier (UUID) for this session
- `filename`: string - Original filename (e.g., "xray_001.jpg")
- `image_data`: numpy.ndarray - In-memory image array
- `format`: string - Image format ("PNG", "JPEG", "JPG")
- `size_bytes`: integer - File size in bytes (max 10MB = 10,485,760 bytes)
- `width`: integer - Image width in pixels
- `height`: integer - Image height in pixels
- `upload_timestamp`: string (ISO 8601) - When the image was uploaded

**Validation Rules**:
- `size_bytes` <= 10,485,760 (10MB limit)
- `format` in ["PNG", "JPEG", "JPG"]
- `width`, `height` >= 1

**State Transitions**: None (immutable after upload)

**Storage**: In-memory only - no disk storage

---

### 2. FilterRequest

**Description**: Request to apply image processing filter(s) to an uploaded image

**Attributes**:
- `image_id`: string - Reference to UploadedImage.id
- `filters`: list[string] - List of filter names to apply (e.g., ["sobel", "gaussian_blur"])
- `request_timestamp`: string (ISO 8601) - When request was made

**Validation Rules**:
- `filters` not empty
- Each filter in `filters` must be one of: ["sobel", "canny", "gaussian_blur", "median_filter", "histogram_equalization", "fourier_transform", "dct", "otsu_thresholding"]
- `image_id` must reference existing uploaded image

**State Transitions**: Request → Processing → Complete/Failed

---

### 3. ProcessedImage

**Description**: Result of applying a single filter to an image

**Attributes**:
- `id`: string - Unique identifier
- `source_image_id`: string - Reference to original UploadedImage.id
- `filter_name`: string - Name of applied filter (e.g., "sobel")
- `image_data`: numpy.ndarray - Processed image array in memory
- `processing_time_ms`: integer - Time taken to process (milliseconds)
- `created_timestamp`: string (ISO 8601) - When processing completed

**Relationships**:
- One UploadedImage → Many ProcessedImage
- One FilterRequest → Many ProcessedImage (one per filter)

**Storage**: In-memory only - returned as base64 or bytes to frontend, not saved to disk

---

### 4. ImageFilter

**Description**: Configuration for an image processing filter algorithm

**Attributes**:
- `name`: string - Filter identifier (e.g., "sobel", "canny")
- `display_name`: string - User-friendly name (e.g., "Sobel Edge Detection")
- `description`: string - Brief description of what the filter does
- `parameters`: dict - Fixed parameters for the filter

**Examples**:
```json
{
  "name": "sobel",
  "display_name": "Sobel Edge Detection",
  "description": "Detects edges using Sobel operators",
  "parameters": {"kernel_size": 3}
},
{
  "name": "gaussian_blur",
  "display_name": "Gaussian Blur",
  "description": "Smooths image using Gaussian kernel",
  "parameters": {"sigma": 1.4, "kernel_size": 5}
},
{
  "name": "canny",
  "display_name": "Canny Edge Detection",
  "description": "Multi-stage edge detection algorithm",
  "parameters": {"low_threshold": 100, "high_threshold": 200}
}
```

**Storage**: Static configuration in `backend/src/config/filter_config.json`

---

### 5. DetectionRequest

**Description**: Request to detect diseases in a chest X-ray image

**Attributes**:
- `image_id`: string - Reference to UploadedImage.id
- `request_timestamp`: string (ISO 8601) - When request was made

**Validation Rules**:
- `image_id` must reference existing uploaded image

**State Transitions**: Request → Model Inference → Complete/Failed

---

### 6. DetectionResult

**Description**: Results from disease detection on a chest X-ray

**Attributes**:
- `id`: string - Unique identifier
- `source_image_id`: string - Reference to UploadedImage.id
- `detections`: list[Detection] - List of detected abnormalities (empty if healthy)
- `is_normal`: boolean - True if no abnormalities detected
- `inference_time_ms`: integer - Model inference time
- `annotated_image_data`: numpy.ndarray - Image with bounding boxes drawn in memory
- `created_timestamp`: string (ISO 8601)

**Relationships**:
- One UploadedImage → One DetectionResult
- One DetectionResult → Many Detection

**Storage**: In-memory only - annotated image returned to frontend as base64, not saved to disk

---

### 7. Detection (Bounding Box)

**Description**: A single detected abnormality with bounding box coordinates

**Attributes**:
- `class_name_en`: string - English disease class name (e.g., "Pleural effusion")
- `class_name_vi`: string - Vietnamese translation (e.g., "Tràn dịch màng phổi")
- `confidence`: float - Detection confidence score (0.0 to 1.0)
- `confidence_tier`: string - "high" (>0.7), "medium" (0.4-0.7), "low" (<0.4, hidden)
- `bbox`: BoundingBox - Coordinates of detection region
- `health_info`: HealthInfo - Vietnamese health information for this condition

**Validation Rules**:
- `confidence` between 0.0 and 1.0
- `confidence` >= 0.4 (low confidence detections are filtered out before display)
- `class_name_en` must exist in class mapping

**Display Rules** (from clarification):
- High confidence (>70%): Solid bounding box
- Medium confidence (40-70%): Dashed bounding box
- Low confidence (<40%): Hidden, not included in result

---

### 8. BoundingBox

**Description**: Rectangular coordinates for a detected region

**Attributes**:
- `x`: integer - Top-left X coordinate (pixels)
- `y`: integer - Top-left Y coordinate (pixels)
- `width`: integer - Box width (pixels)
- `height`: integer - Box height (pixels)

**Validation Rules**:
- All values >= 0
- `x + width` <= image width
- `y + height` <= image height

**Format**: Normalized or absolute depending on YOLO output format

---

### 9. DiseaseClass

**Description**: A disease category that can be detected in chest X-rays

**Attributes**:
- `id`: string - Unique identifier (e.g., "pleural_effusion")
- `name_en`: string - English name (e.g., "Pleural effusion")
- `name_vi`: string - Vietnamese name (e.g., "Tràn dịch màng phổi")
- `health_info`: HealthInfo - Health information for this disease

**Storage**: Configuration in `configs/class_mapping.json`:
```json
{
  "Aortic enlargement": "Phình động mạch chủ",
  "Atelectasis": "Xẹp phổi",
  "Calcification": "Vôi hóa",
  "Cardiomegaly": "Tim to",
  "Consolidation": "Đông đặc phổi",
  "ILD": "Tổn thương phổi kẽ",
  "Infiltration": "Vùng thâm nhiễm",
  "Lung Opacity": "Mờ phổi",
  "Nodule-Mass": "Nốt - Khối bất thường",
  "Other lesion": "Tổn thương khác",
  "Pleural effusion": "Tràn dịch màng phổi",
  "Pleural thickening": "Dày màng phổi",
  "Pneumothorax": "Tràn khí màng phổi",
  "Pulmonary fibrosis": "Xơ phổi",
  "Normal": "Bình thường"
}
```

---

### 10. HealthInfo

**Description**: Vietnamese health information text for a disease

**Attributes**:
- `description`: string - Vietnamese description of the condition
- `warning`: string - Medical consultation warning text

**Example** (from spec):
```json
{
  "Pleural effusion": {
    "description": "Tràn dịch màng phổi là tình trạng tích tụ dịch bất thường trong khoang màng phổi...",
    "warning": "🚨 Cảnh báo quan trọng: Thông tin trên chỉ mang tính chất tham khảo và giáo dục..."
  }
}
```

**Storage**: Configuration in `configs/health_info_vi.json`

---

### 11. TrainingDataset (Offline)

**Description**: Dataset structure for model fine-tuning (used in notebook, not in web app)

**Source**: Dataset downloaded from Roboflow Universe - VinBigData Chest X-ray Symptom Detection project (https://universe.roboflow.com/vinbigdataxrayproject/chest-xray-symptom-detection)

**Download Method**: In Jupyter notebook, use Roboflow API:
```python
!pip -q install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="wQ9S049DhK8xjIhNy6zv")
project = rf.workspace("vinbigdataxrayproject").project("chest-xray-symptom-detection")
version = project.version(3)
dataset = version.download("yolov11")
```

**Attributes**:
- `split`: string - "train", "val", or "test"
- `images_dir`: string - Path to images directory
- `labels_dir`: string - Path to YOLO format label files
- `num_images`: integer - Number of images in split
- `num_normal`: integer - Number of images without annotations (auto-labeled as "Normal")
- `class_distribution`: dict[string, integer] - Count of each disease class

**Format**: YOLO format with `.txt` label files (YOLOv11 format from Roboflow)

**Example Label File** (`data/train/labels/image_001.txt`):
```
0 0.5 0.5 0.3 0.2  # class_id x_center y_center width height (normalized)
2 0.7 0.3 0.1 0.15
```

**Auto-labeling**: Images with no `.txt` file or empty `.txt` → labeled as class "Normal" (Bình thường)

---

## Entity Relationships

```
UploadedImage (1) ──→ (N) ProcessedImage
UploadedImage (1) ──→ (1) DetectionResult
DetectionResult (1) ──→ (N) Detection
Detection (1) ──→ (1) BoundingBox
Detection (1) ──→ (1) HealthInfo
DiseaseClass (1) ──→ (1) HealthInfo
FilterRequest (1) ──→ (N) ProcessedImage
```

---

## Configuration Files

### 1. `configs/class_mapping.json`

Maps English disease names to Vietnamese translations.

**Usage**: Training notebook and inference API

**Format**:
```json
{
  "Aortic enlargement": "Phình động mạch chủ",
  "Atelectasis": "Xẹp phổi",
  ...
  "Normal": "Bình thường"
}
```

### 2. `configs/health_info_vi.json`

Vietnamese health information for each disease class.

**Usage**: Detection result display in frontend

**Format**:
```json
{
  "Pleural effusion": {
    "description": "⚠️ Thông tin về Tràn dịch màng phổi\nTràn dịch màng phổi là...",
    "warning": "🚨 Cảnh báo quan trọng: Thông tin trên chỉ mang tính chất tham khảo..."
  }
}
```

### 3. `backend/src/config/filter_config.json`

Fixed parameters for each image processing filter.

**Usage**: Filter application in backend

**Format**:
```json
{
  "sobel": {"kernel_size": 3},
  "gaussian_blur": {"sigma": 1.4, "kernel_size": 5},
  "canny": {"low_threshold": 100, "high_threshold": 200},
  "median_filter": {"kernel_size": 5},
  "otsu_thresholding": {}
}
```

---

## API Request/Response Models (Pydantic)

### FilterApplyRequest
```python
class FilterApplyRequest(BaseModel):
    image_id: str
    filters: List[str]  # ["sobel", "gaussian_blur", ...]
```

### FilterApplyResponse
```python
class ProcessedImageInfo(BaseModel):
    filter_name: str
    image_base64: str  # Base64-encoded processed image (no URL, in-memory only)
    processing_time_ms: int

class FilterApplyResponse(BaseModel):
    request_id: str
    results: List[ProcessedImageInfo]
    total_time_ms: int
```

### DetectionAnalyzeRequest
```python
class DetectionAnalyzeRequest(BaseModel):
    image_id: str
```

### DetectionAnalyzeResponse
```python
class BoundingBoxData(BaseModel):
    x: int
    y: int
    width: int
    height: int

class DetectionData(BaseModel):
    class_name_en: str
    class_name_vi: str
    confidence: float
    confidence_tier: str  # "high" or "medium"
    bbox: BoundingBoxData
    health_description: str
    health_warning: str

class DetectionAnalyzeResponse(BaseModel):
    request_id: str
    is_normal: bool
    detections: List[DetectionData]
    annotated_image_base64: str  # Base64-encoded annotated image (no URL, in-memory only)
    inference_time_ms: int
```

---

## File Storage Layout

```
backend/
└── models/           # Model weights (ONLY persistent storage)
    └── yolov11s_finetuned.pt
```

**Storage Philosophy**: No file storage for images. All processing happens in memory:
- Uploaded images → stored as numpy arrays in request context
- Processed images → returned as base64-encoded strings to frontend
- Annotated images → drawn in memory and returned immediately

**Why No Storage**: MVP simplicity - no need for cleanup tasks, no disk space concerns, no file management complexity

---

## Summary

This data model defines:
- **Runtime Entities**: UploadedImage, ProcessedImage, DetectionResult, Detection (all in-memory, no persistence)
- **Configuration Entities**: DiseaseClass, HealthInfo, ImageFilter (static JSON config files)
- **Request/Response Models**: API contracts for Streamlit-FastAPI communication (base64 image encoding)
- **Storage Strategy**: No storage - all image data in memory only; model weights are the only persistent files
- **Validation Rules**: File size limits, confidence thresholds, format constraints

All entities align with specification requirements and support the 4-developer parallel workflow with MVP simplicity.
