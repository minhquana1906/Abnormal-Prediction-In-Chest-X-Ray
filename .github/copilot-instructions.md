# Abnormal-prediction-in-chest-X-ray Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-09

## Active Technologies
- No persistent storage - images processed in memory only; model weights stored in `backend/models/` directory (001-xray-abnormality-detection)

- Python 3.12.3 + Streamlit (frontend UI), FastAPI (backend API), YOLOv11s/ultralytics (object detection), loguru (logging), wandb (training tracking), uv (package management), numpy (image processing), pillow (image handling) (001-xray-abnormality-detection)

- **Dataset**: Roboflow Universe - VinBigData Chest X-ray Symptom Detection (version 3, YOLOv11 format). Downloaded via Roboflow Python SDK in Jupyter notebook. API key: wQ9S049DhK8xjIhNy6zv (001-xray-abnormality-detection)

## Project Structure

```text
backend/
  src/
    api/          # FastAPI endpoints and middleware
    filters/      # Custom image processing filters (8 filters)
    models/       # YOLOv11s wrapper
    utils/        # Image processing, mapping, logging, preprocessing, augmentation utilities
      preprocessing.py   # Standard preprocessing pipeline (NEW)
      augmentation.py    # Data augmentation utilities (NEW)
      image_utils.py     # Image conversion utilities
      class_mapping.py   # English-Vietnamese mapping
      health_info.py     # Health information lookup
    config/       # Configuration constants
  models/         # Model weights storage (ONLY persistent storage)
frontend/
  src/
    pages/        # Streamlit page modules (filter_processing, detection)
    components/   # Reusable UI components
    utils/        # API client and helpers
notebooks/        # Jupyter notebooks for training
  finetune_yolo.ipynb   # YOLOv11s training notebook (UPDATED: preprocessing + augmentation)
configs/          # JSON configuration files (class_mapping.json, health_info_vi.json)
docs/             # Documentation (NEW)
  PREPROCESSING_AND_AUGMENTATION.md   # Preprocessing and augmentation guide
pyproject.toml    # Single dependency file with groups: [backend], [frontend], [training], [dev], [all]
```

## Dependency Management

This project uses a **single `pyproject.toml`** at the repository root with dependency groups:

- **Core dependencies** (always installed): `pillow`, `numpy`, `loguru`
- **`[backend]`**: FastAPI, Uvicorn, Ultralytics, Pydantic
- **`[frontend]`**: Streamlit, Requests  
- **`[training]`**: Roboflow, WandB, tqdm, Jupyter
- **`[dev]`**: Ruff (linter/formatter)
- **`[all]`**: All dependency groups combined

### Installation Commands

```bash
# Create virtual environment at repository root
uv venv
source .venv/bin/activate

# Install specific dependency groups
uv pip install -e ".[backend]"           # Backend only
uv pip install -e ".[frontend]"          # Frontend only
uv pip install -e ".[backend,frontend]"  # Both
uv pip install -e ".[all]"               # Everything
```

## Commands

```bash
# Backend development
cd backend
uvicorn src.api.main:app --reload --port 8000

# Frontend development  
cd frontend
streamlit run src/app.py --server.port 8501

# Code formatting/linting
ruff check .
ruff format .

# Jupyter notebooks
cd notebooks
jupyter notebook
```

## Code Style

Python 3.12.3: Follow standard conventions

## Dataset Information
- **Source**: Roboflow Universe - VinBigData Chest X-ray Symptom Detection project
- **URL**: https://universe.roboflow.com/vinbigdataxrayproject/chest-xray-symptom-detection
- **Version**: 3
- **Format**: YOLOv11 (YOLO format with normalized bounding boxes)
- **Classes**: 14 chest X-ray abnormality classes (NO "Normal" class - YOLO learns from negative samples)
- **Normal Image Handling**: Images without abnormalities have NO annotations. YOLO learns from these negative samples. During inference, images with no detections above confidence threshold (0.3) are classified as Normal.
- **Download method**: Roboflow Python SDK in Jupyter notebook
- **API Key**: wQ9S049DhK8xjIhNy6zv
- **Download code**:
```python
!pip -q install roboflow
from roboflow import Roboflow
rf = Roboflow(api_key="wQ9S049DhK8xjIhNy6zv")
project = rf.workspace("vinbigdataxrayproject").project("chest-xray-symptom-detection")
version = project.version(3)
dataset = version.download("yolov11")
```

## Recent Changes
- 2025-11-10: **REMOVED "Normal" class** - Not needed. YOLO learns from negative samples (images without annotations). Normal images identified by confidence threshold (detections < 0.3 = Normal)
- 2025-11-10: Updated confidence threshold from 0.4 to 0.3 for better sensitivity
- 2025-11-09: Added standard preprocessing pipeline (`backend/src/utils/preprocessing.py`) - applied to ALL images (training + user uploads) for consistency
- 2025-11-09: Added enhanced data augmentation (`backend/src/utils/augmentation.py`) - vertical flip, zoom, shift, dynamic Gaussian blur
- 2025-11-09: Updated training config to use native 1024x1024 image size (imgsz=1024, batch=8) instead of downscaled 640x640
- 2025-11-09: Integrated preprocessing into `YOLODetector.predict()` with `apply_preprocessing=True` parameter
- 2025-11-09: Updated notebook `finetune_yolo.ipynb` with new preprocessing and augmentation steps
- 001-xray-abnormality-detection: Added Roboflow dataset integration (VinBigData Chest X-ray Symptom Detection v3, YOLOv11 format)
- 001-xray-abnormality-detection: Added Python 3.12.3 + Streamlit (frontend UI), FastAPI (backend API), YOLOv11s/ultralytics (object detection), loguru (logging), wandb (training tracking), uv (package management), numpy (image processing), pillow (image handling)

## Preprocessing & Augmentation (CRITICAL)

**Standard Preprocessing Pipeline** (applied to ALL images):
```python
# File: backend/src/utils/preprocessing.py
from backend.src.utils.preprocessing import preprocess_image

preprocessed = preprocess_image(
    image,                      # Input: numpy array (H, W) or (H, W, 3)
    target_size=None,           # Optional: (width, height) for resizing
    apply_normalization=True    # Normalize to [0, 1] range
)
```

**Pipeline Steps:**
1. Grayscale conversion (if RGB)
2. Histogram equalization (contrast enhancement)
3. Light Gaussian blur 3x3 (noise reduction)
4. Optional resize
5. Normalization to [0, 1] range (float32)

**⚠️ CRITICAL**: Same preprocessing MUST be applied to:
- Training dataset (in notebook)
- Validation/test sets
- User-uploaded images (in API - automatic via `YOLODetector`)

**Data Augmentation** (training only):
- Vertical flip (50%)
- Horizontal flip (50%)
- Rotation ±15° (50%)
- Random zoom 0.9-1.1x (50%)
- Random shift ±10% (50%)
- Dynamic Gaussian blur (50%): 70% 3x3, 25% 5x5, 5% 7x7
- Brightness 0.8-1.2x (50%)
- Contrast 0.8-1.2x (50%)

**Image Size**: Native 1024x1024 (training + inference)

See `/docs/PREPROCESSING_AND_AUGMENTATION.md` for details.

## Normal Image Detection (CRITICAL)

**NO "Normal" class exists in the model**. Normal images are identified by:
1. YOLO learns from **negative samples** (images with NO annotations/bboxes)
2. During inference, if no detections have `confidence >= 0.3` → Image is classified as **Normal**
3. Confidence threshold = 0.3 (adjustable in `backend/src/config/settings.py`)

**Logic**:
```python
# In YOLODetector.detect_and_annotate()
detections = self.predict(image, apply_preprocessing=True)
is_normal = len(detections) == 0  # No detections above threshold = Normal

if is_normal:
    # Return original image without bboxes
    return annotated_image, [], True
```

**Why this approach is better**:
- YOLO naturally learns from negative samples without explicit "Normal" class
- Avoids class imbalance and noise from synthetic "Normal" class
- More accurate: Low-confidence detections are filtered → cleaner Normal classification
- Flexible: Threshold adjustable based on precision/recall trade-off

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
