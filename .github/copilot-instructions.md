# Abnormal-prediction-in-chest-X-ray Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-08

## Active Technologies
- No persistent storage - images processed in memory only; model weights stored in `backend/models/` directory (001-xray-abnormality-detection)

- Python 3.12.3 + Streamlit (frontend UI), FastAPI (backend API), YOLOv11s/ultralytics (object detection), loguru (logging), wandb (training tracking), uv (package management), numpy (image processing), pillow (image handling) (001-xray-abnormality-detection)

- **Dataset**: Roboflow Universe - VinBigData Chest X-ray Symptom Detection (version 3, YOLOv11 format). Downloaded via Roboflow Python SDK in Jupyter notebook. API key: wQ9S049DhK8xjIhNy6zv (001-xray-abnormality-detection)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12.3: Follow standard conventions

## Dataset Information
- **Source**: Roboflow Universe - VinBigData Chest X-ray Symptom Detection project
- **URL**: https://universe.roboflow.com/vinbigdataxrayproject/chest-xray-symptom-detection
- **Version**: 3
- **Format**: YOLOv11 (YOLO format with normalized bounding boxes)
- **Classes**: 14 chest X-ray abnormality classes + 1 "Normal" class for images without annotations
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
- 001-xray-abnormality-detection: Added Roboflow dataset integration (VinBigData Chest X-ray Symptom Detection v3, YOLOv11 format)
- 001-xray-abnormality-detection: Added Python 3.12.3 + Streamlit (frontend UI), FastAPI (backend API), YOLOv11s/ultralytics (object detection), loguru (logging), wandb (training tracking), uv (package management), numpy (image processing), pillow (image handling)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
