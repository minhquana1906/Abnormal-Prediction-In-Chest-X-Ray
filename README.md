# Chest X-Ray Abnormality Detection

Web application for chest X-ray image analysis with custom filters and AI-powered disease detection.

## Features

### 🔍 Image Filter Processing (User Story 1 - P1)
Apply 8 custom-implemented image processing filters to chest X-rays:
- **Sobel Edge Detection** - Gradient-based edge detection
- **Canny Edge Detection** - Multi-stage edge detection
- **Gaussian Blur** - Image smoothing
- **Median Filter** - Noise reduction
- **Histogram Equalization** - Contrast enhancement
- **Fourier Transform** - Frequency domain visualization
- **Discrete Cosine Transform (DCT)** - Frequency analysis
- **Otsu Thresholding** - Automatic binary segmentation

All filters implemented from scratch using NumPy primitives.

### 🏥 Disease Detection (User Story 2 - P2)
AI-powered detection of 14 chest X-ray abnormality classes:
- Aortic enlargement (Phình động mạch chủ)
- Atelectasis (Xẹp phổi)
- Calcification (Vôi hóa)
- Cardiomegaly (Tim to)
- Consolidation (Đông đặc phổi)
- ILD (Tổn thương phổi kẽ)
- Infiltration (Vùng thâm nhiễm)
- Lung Opacity (Mờ phổi)
- Nodule-Mass (Nốt - Khối bất thường)
- Other lesion (Tổn thương khác)
- Pleural effusion (Tràn dịch màng phổi)
- Pleural thickening (Dày màng phổi)
- Pneumothorax (Tràn khí màng phổi)
- Pulmonary fibrosis (Xơ phổi)

Features:
- YOLOv11s-based detection with bounding boxes
- 3-tier confidence levels (high >70%, medium 40-70%, low <40%)
- Vietnamese labels and health information
- Medical consultation warnings

### 🧪 Model Training (User Story 3 - P3)
Offline Jupyter notebook for model fine-tuning:
- Dataset download from Roboflow (VinBigData Chest X-ray)
- Preprocessing with custom filters
- Auto-labeling for "Normal" images
- Training with tqdm progress + WandB experiment tracking
- Model export for deployment

## Architecture

```
├── backend/          # FastAPI REST API
│   ├── src/
│   │   ├── api/      # Endpoints and middleware
│   │   ├── filters/  # 8 custom filter implementations
│   │   ├── models/   # YOLOv11s wrapper
│   │   ├── utils/    # Image processing, mapping, logging
│   │   └── config/   # Configuration constants
│   └── models/       # Model weights storage (ONLY persistent storage)
├── frontend/         # Streamlit web UI
│   └── src/
│       ├── pages/    # Filter processing and detection tabs
│       ├── components/ # Reusable UI widgets
│       └── utils/    # API client and helpers
├── notebooks/        # Jupyter notebooks for training
└── configs/          # Class mappings and health info (Vietnamese)
```

## Tech Stack

- **Python**: 3.12.3
- **Frontend**: Streamlit 1.28+
- **Backend**: FastAPI + Uvicorn
- **Object Detection**: YOLOv11s (Ultralytics)
- **Image Processing**: NumPy + Pillow (custom implementations)
- **Logging**: Loguru
- **Training**: WandB + tqdm
- **Package Manager**: uv

## Setup

### Prerequisites
- Python 3.12.3
- uv package manager

### Installation

**Note**: This project uses a single `pyproject.toml` at the repository root with dependency groups for backend, frontend, and training.

1. Clone the repository
```bash
git clone git@github.com:minhquana1906/Abnormal-Prediction-In-Chest-X-Ray.git
cd Abnormal-prediction-in-chest-X-ray
```

2. Create virtual environment and install dependencies
```bash
# Create virtual environment at repository root
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Option 1: Install all dependencies (backend + frontend + training)
uv pip install -e ".[all]"  # or uv sync --all-extras

# Option 2: Install only what you need
uv pip install -e ".[backend]"        # Backend only
uv pip install -e ".[frontend]"       # Frontend only
uv pip install -e ".[backend,frontend]"  # Both backend and frontend
uv pip install -e ".[training]"       # Training notebook dependencies
```

### Dependency Groups

- **Core dependencies** (always installed): `pillow`, `numpy`, `loguru`
- **`[backend]`**: FastAPI, Uvicorn, Ultralytics, Pydantic
- **`[frontend]`**: Streamlit, Requests
- **`[training]`**: Roboflow, WandB, tqdm, Jupyter
- **`[dev]`**: Ruff (code formatter/linter)
- **`[all]`**: All dependency groups combined

### Running the Application

1. Start the backend API (terminal 1)
```bash
uvicorn backend.src.api.main:app --reload --port 8000
```

2. Start the frontend UI (terminal 2)
```bash
streamlit run frontend/src/app.py --server.port 8501
```

3. Open http://localhost:8501 in your browser

## Performance Goals

- Single filter processing: <5 seconds
- Multiple filters (8 filters): <15 seconds
- Disease detection: <10 seconds

## Implementation Status

### ✅ Phase 1: Setup (T001-T008) - COMPLETED
- [X] Project structure created
- [X] Backend and frontend projects initialized with uv
- [X] Configuration files created (class mapping, health info)
- [X] Python 3.12.3 configured
- [X] Directory structure established

### 🔄 Phase 2: Foundational (T009-T022) - NEXT
Backend foundation, frontend foundation, configuration loading

### ⏳ Phase 3: User Story 1 - Filters (T023-T042)
Filter implementations, filter API, filter UI

### ⏳ Phase 4: User Story 2 - Detection (T043-T057)
YOLO inference, detection API, detection UI

### ⏳ Phase 5: User Story 3 - Training (T058-T074)
Training notebook, dataset preparation, model export

### ⏳ Phase 6: Integration & Polish (T075-T095)
Cross-component integration, logging, performance validation

## Dataset

**Source**: Roboflow Universe - VinBigData Chest X-ray Symptom Detection  
**Format**: YOLOv11 (YOLO format with normalized bounding boxes)  
**Classes**: 14 disease classes + "Normal" class  
**Version**: 3  
**API Key**: 

Download in Jupyter notebook:
```python
from roboflow import Roboflow
rf = Roboflow(api_key="")
project = rf.workspace("vinbigdataxrayproject").project("chest-xray-symptom-detection")
version = project.version(3)
dataset = version.download("yolov11")
```

## Storage Philosophy

- **No persistent storage** - All images processed in memory
- **No database** - Stateless request-response model
- **Only exception**: Model weights in `backend/models/`
- **Benefits**: Simple, fast, no cleanup needed

## Development Workflow

### 4 Developer Roles
1. **Backend Developer (Dev1)**: Image processing filters
2. **Frontend Developer (Dev2)**: Streamlit UI components
3. **Model Developer (Dev3)**: YOLOv11s fine-tuning
4. **Integration Developer (Dev4)**: API endpoints and connections

### Parallel Development
- Setup phase: All developers collaborate
- Core development: Each developer works independently
- Integration phase: All developers collaborate

## Constitution Compliance

✅ **MVP Academic Simplicity** - Straightforward architecture  
✅ **No Test-Driven Development** - Manual testing with comprehensive logging  
✅ **Minimal Documentation** - Focus on clear code  
✅ **Comprehensive Logging** - loguru for all operations  
✅ **Implementation Summaries** - Progress tracked in tasks.md

## License

[To be determined]

## Contact

[To be determined]
