# Implementation Plan: Chest X-Ray Abnormality Detection

**Branch**: `001-xray-abnormality-detection` | **Date**: 2025-11-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-xray-abnormality-detection/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a web application for chest X-ray abnormality detection with two main features: (1) Image filter processing - apply 8 custom-implemented filters (Sobel, Canny, Gaussian Blur, Median, Histogram Equalization, Fourier Transform, DCT, Otsu) to uploaded X-ray images, and (2) Disease detection - use fine-tuned YOLOv11s to detect 14 disease classes with Vietnamese labels and health information. Additionally, provide an offline Jupyter notebook for model fine-tuning with preprocessing, data augmentation, and experiment tracking (tqdm + WandB). The web application consists of Streamlit frontend and FastAPI backend, designed for local deployment with comprehensive logging using loguru.

## Technical Context

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: Streamlit (frontend UI), FastAPI (backend API), YOLOv11s/ultralytics (object detection), loguru (logging), wandb (training tracking), uv (package management), numpy (image processing), pillow (image handling)  
**Storage**: No persistent storage - images processed in memory only; model weights stored in `backend/models/` directory  
**Testing**: Manual testing with comprehensive logging (no automated test suite per constitution)  
**Target Platform**: Local development machine (Linux/macOS/Windows)  
**Project Type**: Web application (frontend + backend separation)  
**Performance Goals**: Single filter processing <5s, multiple filters <15s, disease detection <10s for standard X-ray images (512x512 to 2048x2048)  
**Constraints**: Max 10MB file size, PNG/JPG/JPEG only, fixed filter parameters, local-only deployment, no production infrastructure  
**Scale/Scope**: Single-user local application, academic MVP demonstration, 8 filter algorithms, 14 disease classes, offline training notebook

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. MVP Academic Simplicity
- **Status**: PASS
- **Evidence**: Using straightforward web app architecture (Streamlit + FastAPI), avoiding complex enterprise patterns, focusing on demonstrable functionality
- **Note**: No overengineering - direct implementation of filters and model inference

### ✅ II. No Test-Driven Development
- **Status**: PASS
- **Evidence**: No test suite planned, validation through manual testing and logging
- **Note**: Aligns with academic MVP scope

### ✅ III. Minimal Documentation Standards
- **Status**: PASS
- **Evidence**: No pre-commit hooks, comprehensive docstrings, or extensive type hints required
- **Note**: Focus on self-explanatory code with clear naming

### ✅ IV. Comprehensive Logging
- **Status**: PASS
- **Evidence**: loguru integrated for all major workflow steps (upload, filter processing, detection, training)
- **Action Required**: Implement detailed logging in all modules covering:
  - Image upload and validation
  - Filter application with parameters and timing
  - Model inference with confidence scores
  - Training progress (tqdm + WandB in notebook)
  - Error conditions with context

### ✅ V. Implementation Summaries
- **Status**: PASS
- **Evidence**: Plan includes verification steps for each component
- **Action Required**: After each implementation phase, provide:
  - Component summary (what was built)
  - Verification commands (how to test manually)
  - Expected outputs and success indicators

### Additional Compliance Checks

✅ **Local Deployment Only**: Streamlit + FastAPI run locally, no cloud dependencies  
✅ **Python 3.12+**: Using Python 3.12.3 as specified  
✅ **Minimal Dependencies**: Core stack only (Streamlit, FastAPI, ultralytics, loguru, wandb)  
✅ **Filesystem Storage**: All data stored locally (no database)  
✅ **Code Quality**: Focus on clear structure, readable names, maintainable logic

### Gate Status: ✅ APPROVED TO PROCEED

All constitution principles satisfied. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-xray-abnormality-detection/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api-spec.yaml    # FastAPI endpoints OpenAPI spec
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── filters.py       # Filter processing endpoints (in-memory)
│   │   │   └── detection.py     # Disease detection endpoints (in-memory)
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── logging.py       # Request/response logging
│   │       └── validation.py    # File validation middleware
│   ├── filters/
│   │   ├── __init__.py
│   │   ├── sobel.py             # Sobel edge detection (from scratch)
│   │   ├── canny.py             # Canny edge detection (from scratch)
│   │   ├── gaussian.py          # Gaussian blur (from scratch)
│   │   ├── median.py            # Median filter (from scratch)
│   │   ├── histogram.py         # Histogram equalization (from scratch)
│   │   ├── fourier.py           # Fourier transform (from scratch)
│   │   ├── dct.py               # Discrete Cosine Transform (from scratch)
│   │   └── otsu.py              # Otsu thresholding (from scratch)
│   ├── models/
│   │   ├── __init__.py
│   │   └── yolo_detector.py     # YOLOv11s wrapper with Vietnamese mapping
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── image_utils.py       # Image processing in memory (no save)
│   │   ├── class_mapping.py     # English-Vietnamese disease class mapping
│   │   └── health_info.py       # Vietnamese health information texts
│   └── config/
│       ├── __init__.py
│       └── settings.py          # Configuration constants
├── models/                       # Trained YOLO model weights directory (ONLY storage)
│   └── yolov11s_finetuned.pt
├── pyproject.toml               # Backend dependencies (uv)
└── README.md

frontend/
├── src/
│   ├── app.py                   # Streamlit main application
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── filter_processing.py # Tab 1: Image filter processing
│   │   └── detection.py         # Tab 2: Disease detection
│   ├── components/
│   │   ├── __init__.py
│   │   ├── image_uploader.py    # Reusable image upload widget
│   │   ├── filter_selector.py   # Filter selection UI
│   │   ├── result_display.py    # Image result display
│   │   └── health_card.py       # Vietnamese health info display
│   └── utils/
│       ├── __init__.py
│       ├── api_client.py        # Backend API communication
│       └── ui_helpers.py        # UI utility functions
├── pyproject.toml               # Frontend dependencies (uv)
└── README.md

notebooks/
├── finetune_yolo.ipynb          # Model fine-tuning notebook
├── data_preprocessing.ipynb     # Dataset preprocessing exploration
└── filter_analysis.ipynb        # Filter testing and parameter tuning

data/                             # Training dataset (not in repo)
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/

configs/
├── class_mapping.json           # English-Vietnamese mapping
└── health_info_vi.json          # Vietnamese health information

.specify/                         # Speckit configuration
pyproject.toml                    # Root project config (workspace)
README.md                         # Main project documentation
```

**Structure Decision**: Web application architecture with separate `frontend/` (Streamlit UI) and `backend/` (FastAPI services). This separation enables parallel development by 4 developers:
1. **Backend Developer**: Implement 8 image processing filter algorithms in `backend/src/filters/`
2. **Frontend Developer**: Build Streamlit UI in `frontend/src/` with tabs and components  
3. **Model Developer**: Fine-tune YOLOv11s in `notebooks/finetune_yolo.ipynb`
4. **Integration Developer**: Connect frontend-backend via `api_client.py` and implement FastAPI routes

The `notebooks/` directory contains offline training workflow, separate from the web application.

**Storage Philosophy**: MVP simplicity - no persistent storage, no database, no file saving. Images are processed entirely in memory and results returned immediately to the frontend. Only exception: model weights stored in `backend/models/` for inference.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. Project adheres to all constitutional principles.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
