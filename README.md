# 🫁 Chest X-Ray Abnormality Detection

> A web application for automated analysis of chest X-ray images combining custom image filters and AI-powered disease detection using YOLOv11s.

**Project Status**: MVP Complete | **Model**: YOLOv11s (2 disease classes) | **Validation mAP50**: 94.18%

---

## 📋 Overview

### 🎯 Project Goals

1. **Image Filter Processing**: Apply 8 custom NumPy-based filters for enhanced X-ray analysis
2. **Disease Detection**: Detect 2 chest abnormality classes with high precision (91.17%)
3. **Model Training**: Fine-tune YOLOv11s with data augmentation and experiment tracking via WandB

### ✨ Key Features

#### 🔍 Image Filter Processing (8 Filters)

All filters implemented from scratch using NumPy primitives:

- **Sobel Edge Detection** - Gradient-based edge detection
- **Canny Edge Detection** - Multi-stage edge detection  
- **Gaussian Blur** - Image smoothing (σ=1.4)
- **Median Filter** - Noise reduction (5×5 window)
- **Histogram Equalization** - Contrast enhancement
- **Fourier Transform** - Frequency domain analysis
- **Discrete Cosine Transform (DCT)** - Compression analysis
- **Otsu Thresholding** - Automatic binary segmentation

#### 🏥 Disease Detection (2 Classes)

**Fine-tuned YOLOv11s with Production Metrics**:

| Model | mAP50 | mAP50-95 | Precision | Recall |
|-------|-------|----------|-----------|--------|
| Baseline | 90.34% | 45.67% | 84.26% | 88.26% |
| Light Augmented | 93.10% | 49.11% | 85.18% | 92.81% |
| **Hard Augmented** | **94.18%** | **50.29%** | **91.16%** | **90.55%** |

> **Note**: Originally trained on 14 disease classes. Reduced to **2 focus classes** (Aortic Enlargement, Cardiomegaly) for production deployment and improved model performance.

**Features**:

- Bounding box detection with confidence tiers (high >70%, medium 40-70%, low <40%)
- Vietnamese labels and health information
- Medical consultation recommendations
- Fast inference (<10 seconds per image)

#### 🧪 Model Training

- Jupyter notebooks for offline model fine-tuning
- Data preprocessing with custom filters + augmentation (rotation, zoom, shift, blur)
- WandB experiment tracking and checkpointing
- Export to PyTorch format for deployment

---

## 🏗️ Architecture

```text
backend/                         # FastAPI REST API
├── src/
│   ├── api/                    # Endpoints & middleware
│   ├── filters/                # 8 custom filter implementations
│   ├── models/                 # YOLOv11s wrapper
│   ├── utils/                  # Image processing utilities
│   └── config/                 # Configuration constants
├── logs/                       # Application logs
└── models/                     # Model weights storage (only persistent storage)

frontend/                        # Streamlit web UI
├── src/
│   ├── pages/                  # Filter processing & disease detection tabs
│   ├── components/             # Reusable UI widgets
│   ├── utils/                  # API client & helpers
│   └── app.py                  # Main entry point
└── pyproject.toml

notebooks/                       # Model training (offline)
├── yolov11s-chest-xray-baseline.ipynb
├── yolov11s-chest-xray-soft-augmented.ipynb
└── yolov11s-chest-xray-hard-augmented.ipynb

data/                            # Training datasets
├── preprocessed_2classes/
├── preprocessed_2classes_aug/
└── ...

configs/                         # Configuration files
├── class_mapping_2classes.json
└── health_info_vi.json

models/                          # Model checkpoints
├── baseline.pt
├── light_augmented.pt
└── hard_augmented.pt (production)
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.12.3 |
| **Frontend** | Streamlit 1.28+ |
| **Backend** | FastAPI + Uvicorn |
| **ML Model** | YOLOv11s (Ultralytics) |
| **Image Processing** | NumPy + Pillow |
| **Logging** | Loguru |
| **Experiment Tracking** | WandB |
| **Package Manager** | uv |
| **Code Quality** | Ruff |

---

## 📦 Installation

### Prerequisites

- Python 3.11+ (recommended 3.12.3)
- uv package manager ([install here](https://docs.astral.sh/uv/))
- Git

### Setup Instructions

#### Step 1: Clone Repository

```bash
git clone https://github.com/minhquana1906/Abnormal-Prediction-In-Chest-X-Ray.git
cd Abnormal-Prediction-In-Chest-X-Ray
```

#### Step 2: Create Virtual Environment & Install Dependencies

1. **Linux/macOS setup**

```bash
# Create virtual environment
uv venv

# Activate
source .venv/bin/activate

# Install all dependencies
uv pip install -e ".[all]"
```

1. **Windows PowerShell setup**

```powershell
# Create virtual environment
uv venv

# Activate
.venv\Scripts\Activate.ps1

# Install all dependencies
uv pip install -e ".[all]"
```

1. **Windows CMD setup**

```cmd
# Create virtual environment
uv venv

# Activate
.venv\Scripts\activate.bat

# Install all dependencies
uv pip install -e ".[all]"
```

#### Step 3 (Optional): Install Specific Components

```bash
uv pip install -e ".[backend]"           # Backend only
uv pip install -e ".[frontend]"          # Frontend only
uv pip install -e ".[backend,frontend]"  # Both
uv pip install -e ".[training]"          # Training notebooks
```

---

## 🚀 Running the Application

The application consists of 2 components running in separate terminals:

### Terminal 1: Backend API (FastAPI)

1. **Linux/macOS**

```bash
source .venv/bin/activate
uvicorn backend.src.api.main:app --reload --port 8000
```

1. **Windows**

```powershell
.venv\Scripts\Activate.ps1
uvicorn backend.src.api.main:app --reload --port 8000
```

**Expected Output**:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2: Frontend (Streamlit)

1. **Linux/macOS**

```bash
source .venv/bin/activate
streamlit run frontend/src/app.py --server.port 8501
```

1. **Windows**

```powershell
.venv\Scripts\Activate.ps1
streamlit run frontend/src/app.py --server.port 8501
```

**Expected Output**:

```text
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### Step 3: Access Application

Open your browser and navigate to:

```text
http://localhost:8501
```

✅ **Application is ready to use!**

---

## 📊 Usage

### Tab 1: Filter Processing

1. Upload a chest X-ray image (PNG, JPG, JPEG)
2. Select one or multiple filters
3. View processed results instantly
4. Download filtered images

**Performance**: <5 sec (single filter), <15 sec (8 filters)

### Tab 2: Disease Detection

1. Upload a chest X-ray image
2. Select model version (Baseline, Light Augmented, or Hard Augmented)
3. View detections with:
   - Bounding boxes around abnormalities
   - English & Vietnamese disease names
   - Confidence scores
   - Medical information

**Performance**: <10 seconds per image

---

## 📓 Model Training

### Quick Start (Notebooks)

```bash
cd notebooks
jupyter notebook
```

Select one of the training notebooks:

- `yolov11s-chest-xray-baseline.ipynb` - Baseline model
- `yolov11s-chest-xray-soft-augmented.ipynb` - Light augmentation
- `yolov11s-chest-xray-hard-augmented.ipynb` - Heavy augmentation

### Training Configuration

Before running, configure in the notebook:

```python
# Dataset
ROBOFLOW_API_KEY = "wQ9S049DhK8xjIhNy6zv"
EPOCHS = 50
BATCH_SIZE = 8
IMGSZ = 1024

# Experiment tracking (optional)
USE_WANDB = True
WANDB_PROJECT = "chest-xray-detection"
```

### Training Pipeline

1. **Download Dataset** - VinBigData Chest X-ray v3 from Roboflow (auto)
2. **Preprocess** - Histogram equalization for contrast enhancement
3. **Augment** - Rotation, zoom, shift, blur (depends on notebook)
4. **Train** - YOLOv11s with metrics tracking
5. **Evaluate** - Precision, Recall, mAP50, mAP50-95
6. **Export** - Save model weights to `models/`

### View Results on WandB

If `USE_WANDB = True`, visit:

```text
https://wandb.ai/your-username/chest-xray-detection
```

You can track:

- Training/Validation loss curves
- Precision, Recall, mAP metrics
- Inference examples
- Model checkpoints

---

## ⚙️ Configuration

### Backend Settings

File: `backend/src/config/settings.py`

- **YOLO_CONFIDENCE_THRESHOLD**: 0.4 (detection display threshold)
- **YOLO_INPUT_SIZE**: 640 (model input size)
- **MAX_FILE_SIZE_MB**: 10 (upload limit)
- **ALLOWED_FORMATS**: PNG, JPG, JPEG

### Dataset Information

**Source**: Roboflow - VinBigData Chest X-ray Symptom Detection v3  
**Format**: YOLOv11 (normalized bounding boxes)  
**Classes**: 2 (Aortic Enlargement, Cardiomegaly)  
**Training Strategy**: Originally 14 classes, reduced to 2 for focus and better performance

---

## 📈 Performance Benchmarks

| Task | Target | Actual |
|------|--------|--------|
| Single Filter | <5 sec | ~2-3 sec |
| All 8 Filters | <15 sec | ~8-10 sec |
| Disease Detection | <10 sec | ~4-6 sec |
| Model Inference | - | ~2-4 sec |

---

## 🎨 Code Quality

```bash
# Formatting
ruff format .

# Linting
ruff check .

# Fix issues
ruff check . --fix
```

**Settings** (pyproject.toml):

- Line length: 100 characters
- Target Python: 3.12
- Import sorting: Enabled

## � Logging Configuration

All API requests/responses logged via Loguru:

- **Location**: `backend/logs/app.log`
- **Level**: DEBUG (development)
- **Rotation**: 10 MB files, 7-day retention

---

## 📋 License & Attribution

MIT License - See LICENSE file for details

---

## 👤 Contact & Support

**Author**: Minh Quana  
**GitHub**: [@minhquana1906](https://github.com/minhquana1906)  
**Email**: [quann1906@gmail.com](mailto:quann1906@gmail.com)

---

## 🙏 Acknowledgments

- **Roboflow** - VinBigData Chest X-ray Dataset
- **Ultralytics** - YOLOv11 Implementation
- **Streamlit** - Frontend Framework
- **FastAPI** - Backend Framework
- **NumPy/Pillow** - Image Processing

---

> **Happy analyzing! 🫁**

---
