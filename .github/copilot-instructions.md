# Abnormal-prediction-in-chest-X-ray Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-08

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
    utils/        # Image processing, mapping, logging utilities
    config/       # Configuration constants
  models/         # Model weights storage (ONLY persistent storage)
frontend/
  src/
    pages/        # Streamlit page modules (filter_processing, detection)
    components/   # Reusable UI components
    utils/        # API client and helpers
notebooks/        # Jupyter notebooks for training
configs/          # JSON configuration files (class_mapping.json, health_info_vi.json)
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
