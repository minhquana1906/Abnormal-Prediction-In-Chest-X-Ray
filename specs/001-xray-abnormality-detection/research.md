# Research & Technical Decisions

**Feature**: Chest X-Ray Abnormality Detection  
**Date**: 2025-11-08  
**Phase**: 0 - Technology Research & Selection

## Overview

This document captures research findings and technical decisions for implementing a chest X-ray abnormality detection web application with custom image processing filters and AI-powered disease detection.

## Technology Stack Decisions

### 1. Package Management: uv

**Decision**: Use `uv` for Python package dependency management

**Rationale**:
- **Speed**: uv is significantly faster than pip for dependency resolution and installation (10-100x)
- **Reliability**: Better dependency resolution algorithm, fewer conflicts
- **Modern**: Written in Rust, actively maintained, growing adoption in Python community
- **Compatibility**: Works with standard `pyproject.toml`, easy migration path
- **Local Development**: Excellent for academic/local projects with quick iteration cycles

**Alternatives Considered**:
- **pip + virtualenv**: Traditional but slower, manual dependency management
- **Poetry**: Good dependency management but heavier, more complex for simple projects
- **pipenv**: Slower than uv, less active development

**Implementation Notes**:
- Use `pyproject.toml` for dependency declaration in both frontend/ and backend/
- Each subsystem (frontend, backend) has its own virtual environment managed by uv
- Commands: `uv pip install`, `uv pip compile`, `uv venv`

---

### 2. Frontend Framework: Streamlit

**Decision**: Use Streamlit for web UI

**Rationale**:
- **Rapid Development**: Build web apps with pure Python, no HTML/CSS/JavaScript needed
- **Academic-Friendly**: Perfect for MVP/prototype/demonstration projects
- **Built-in Components**: File uploader, tabs, columns, image display out of the box
- **Easy Deployment**: Simple local execution with `streamlit run`
- **Good Documentation**: Extensive examples and community support
- **Aligns with Constitution**: Simple, maintainable, no production overhead

**Alternatives Considered**:
- **Flask + Jinja2**: More flexible but requires HTML/CSS knowledge, slower development
- **Gradio**: Similar to Streamlit but less mature, fewer UI customization options
- **React + Next.js**: Overkill for academic MVP, requires JavaScript expertise

**Implementation Notes**:
- Multi-page app with tabs for Filter Processing and Disease Detection
- Use st.file_uploader() for image upload (handles PNG/JPG/JPEG validation)
- Use st.columns() for side-by-side image display
- Use st.spinner() for processing status indicators

---

### 3. Backend Framework: FastAPI

**Decision**: Use FastAPI for REST API backend

**Rationale**:
- **Performance**: Async support, fast request handling (good for image processing)
- **Modern Python**: Uses type hints, automatic API documentation (OpenAPI/Swagger)
- **Easy Integration**: Works well with Streamlit frontend via HTTP requests
- **Separation of Concerns**: Clean separation between UI (Streamlit) and business logic (FastAPI)
- **Validation**: Pydantic models for request/response validation
- **Developer Experience**: Auto-generated interactive API docs at /docs

**Alternatives Considered**:
- **Flask**: Simpler but synchronous, less modern, no automatic API docs
- **Django**: Too heavy for this use case, includes ORM/admin panel we don't need
- **Direct Integration**: Streamlit calling functions directly - loses modularity, harder for parallel development

**Implementation Notes**:
- Separate backend/ directory with FastAPI app
- Endpoints: `/upload`, `/filter/apply`, `/detect/analyze`
- Use CORS middleware to allow Streamlit frontend requests
- Run on different port (e.g., backend on 8000, frontend on 8501)

---

### 4. Object Detection Model: YOLOv11s

**Decision**: Use YOLOv11s (ultralytics) as base model for chest X-ray disease detection

**Rationale**:
- **Modern Architecture**: Latest YOLO version with improved accuracy and speed
- **Small Model**: YOLOv11s is the "small" variant, faster inference for local deployment
- **Transfer Learning**: Pre-trained on COCO, can be fine-tuned on chest X-ray dataset
- **Easy Fine-tuning**: Ultralytics library provides simple API for training
- **Good Documentation**: Extensive examples for custom dataset training
- **Medical Imaging**: YOLO models proven effective for medical image analysis with bounding boxes

**Alternatives Considered**:
- **Faster R-CNN**: More accurate but slower, overkill for 14-class detection
- **RetinaNet**: Good but less community support than YOLO
- **EfficientDet**: Competitive but YOLO ecosystem is more mature
- **YOLOv8**: Previous version, v11 has incremental improvements

**Implementation Notes**:
- Install via `ultralytics` package
- Fine-tune on custom chest X-ray dataset with 14 disease classes + "Bình thường"
- Export model weights to `backend/models/yolov11s_finetuned.pt`
- Inference via `YOLO().predict()` with confidence threshold filtering

---

### 5. Experiment Tracking: Weights & Biases (WandB)

**Decision**: Use WandB for training experiment tracking

**Rationale**:
- **Industry Standard**: Widely used in ML research and academic projects
- **Free Tier**: Generous free plan for academic/personal projects
- **Comprehensive Logging**: Loss curves, metrics, hyperparameters, model artifacts
- **Integration**: Native ultralytics support with `wandb` callback
- **Visualization**: Beautiful dashboards for comparing training runs
- **Reproducibility**: Tracks all training parameters and results

**Alternatives Considered**:
- **TensorBoard**: PyTorch-native but less user-friendly, requires local server
- **MLflow**: More complex setup, overkill for single-user academic project
- **Neptune.ai**: Similar to WandB but smaller community
- **Manual Logging**: Simple but loses visualization, comparison features

**Implementation Notes**:
- Initialize with `wandb.init(project="chest-xray-detection")`
- Log metrics: loss, mAP, precision, recall per epoch
- Log training config: learning rate, batch size, augmentation settings
- Use tqdm for console progress + WandB for dashboard tracking

---

### 6. Logging Library: loguru

**Decision**: Use loguru for application logging

**Rationale**:
- **Simpler than stdlib logging**: No complex handler/formatter setup
- **Better Defaults**: Colored output, exception tracing out of the box
- **Flexible**: Easy to configure file rotation, log levels, formats
- **Pythonic API**: `logger.info()`, `logger.error()` with formatting
- **Constitution Compliance**: Enables comprehensive logging requirement

**Alternatives Considered**:
- **stdlib logging**: More verbose configuration, harder to read output
- **structlog**: Great for structured logging but overkill for MVP
- **print() statements**: Not persistent, hard to filter by severity

**Implementation Notes**:
```python
from loguru import logger

# Configure file + console logging
logger.add("logs/app_{time}.log", rotation="10 MB", retention="7 days", level="DEBUG")
logger.info("Image uploaded: {filename}, size: {size}KB", filename=name, size=kb)
logger.error("Filter processing failed: {error}", error=str(e))
```

- Log all major operations: upload, validation, filter application, detection inference
- Include timing information: `logger.info("Filter applied in {elapsed}s", elapsed=duration)`
- Log error context: file paths, parameters, stack traces

---

### 7. Image Processing: NumPy + Pillow (Custom Algorithms)

**Decision**: Implement 8 filters from scratch using NumPy, use Pillow for I/O only

**Rationale**:
- **Educational Value**: Academic project benefits from understanding algorithm internals
- **Requirement Compliance**: Spec explicitly states "implemented from scratch without using pre-built library functions"
- **NumPy Allowed**: NumPy for array operations (convolutions, FFT) is acceptable; the "from scratch" applies to high-level filter functions like `cv2.Canny()`
- **Pillow for I/O**: Image loading/saving is infrastructure, not the algorithm itself

**Alternatives Considered**:
- **OpenCV (cv2)**: Would violate "from scratch" requirement (cv2.Canny, cv2.GaussianBlur are pre-built)
- **scikit-image**: Same issue, provides high-level filter implementations
- **PIL/Pillow only**: Too low-level for efficient array operations

**Implementation Guidelines**:

**Allowed**:
- `numpy.convolve()`, `numpy.fft.fft2()` - mathematical primitives
- `PIL.Image.open()`, `PIL.Image.save()` - I/O operations
- `numpy.histogram()`, `numpy.median()` - statistical functions

**Not Allowed (must implement)**:
- Edge detection logic (Sobel kernels, Canny non-maximum suppression, hysteresis)
- Gaussian blur (must define kernel, apply convolution)
- Otsu threshold calculation (must implement inter-class variance algorithm)
- DCT/FFT frequency filtering (can use FFT primitive, must implement frequency domain filtering)

**Implementation Notes**:
- Each filter in separate module: `backend/src/filters/{sobel,canny,gaussian,...}.py`
- Common utilities: `_convolve()`, `_normalize()`, `_to_uint8()` in shared module
- Fixed parameters per filter (from clarification Q3), optimized for chest X-rays
- Example: Sobel uses 3x3 kernels, Gaussian uses sigma=1.4, Canny uses thresholds 100/200

---

### 8. Python Version: 3.12.3

**Decision**: Use Python 3.12.3 as specified

**Rationale**:
- **User Specification**: Explicitly requested in tech stack preferences
- **Modern Features**: Pattern matching, better error messages, performance improvements
- **Library Compatibility**: All chosen libraries (Streamlit, FastAPI, ultralytics, loguru) support 3.12
- **Long-term Support**: 3.12 released Oct 2023, stable and well-supported

**Implementation Notes**:
- Specify in `pyproject.toml`: `requires-python = ">=3.12,<3.13"`
- Use `.python-version` file for version pinning: `3.12.3`
- Leverage 3.12 features where appropriate (e.g., type hints improvements)

---

## Architecture Decisions

### Frontend-Backend Separation

**Decision**: Separate `frontend/` (Streamlit) and `backend/` (FastAPI) directories

**Rationale**:
- **Parallel Development**: 4 developers can work independently:
  1. Backend developer implements filters
  2. Frontend developer builds UI
  3. Model developer fine-tunes YOLO
  4. Integration developer connects components
- **Clear Responsibilities**: UI logic vs business logic separation
- **Scalability**: Can add more frontend technologies later (mobile app, CLI) without touching backend
- **Testability**: Backend can be tested independently via API calls

**Alternative**: Single monolith with Streamlit directly importing filter functions
- Rejected: Harder to parallelize, tighter coupling, less modular

---

### Offline Training Notebook

**Decision**: Training in Jupyter notebook (`notebooks/finetune_yolo.ipynb`), separate from web app

**Rationale**:
- **Clarification**: User clarified training is offline, not part of UI
- **Iterative Experimentation**: Notebooks ideal for training experiments
- **Resource Management**: Training can run overnight without UI server running
- **Reproducibility**: Notebook captures full training pipeline with markdown explanations

**Implementation**:
- Web app loads pre-trained model weights from `backend/models/yolov11s_finetuned.pt`
- Training notebook exports weights after fine-tuning
- No UI for training; researchers run notebook manually

---

### Class Mapping Strategy

**Decision**: Centralized JSON config for English-Vietnamese mapping

**Rationale**:
- **Single Source of Truth**: One file (`configs/class_mapping.json`) used by training and inference
- **Easy Updates**: Change translations without code changes
- **Internationalization**: Could add more languages later (e.g., `class_mapping_en.json`)

**Structure**:
```json
{
  "Pleural effusion": "Tràn dịch màng phổi",
  "Cardiomegaly": "Tim to",
  ...
  "Normal": "Bình thường"
}
```

---

## Performance Optimization Strategies

### Image Processing Performance

**Challenge**: Processing high-resolution X-rays (up to 2048x2048) with custom filters within 5s (single) / 15s (multiple)

**Strategies**:
1. **NumPy Vectorization**: Use array operations instead of Python loops
2. **FFT Optimization**: Use `numpy.fft.rfft2()` for real-valued images (2x faster than `fft2`)
3. **Downsampling for Preview**: Option to process at lower resolution for speed (e.g., 1024x1024) if original too large
4. **Lazy Loading**: Don't process until user clicks "Apply Filter" button
5. **Caching**: Cache processed images during session to avoid recomputation

**Monitoring**: Log processing time per filter to verify performance goals

---

### Model Inference Performance

**Challenge**: Detection within 10s for standard X-rays

**Strategies**:
1. **YOLOv11s**: Small variant is faster than medium/large (30-50ms per image on GPU, 200-500ms on CPU)
2. **Model Warmup**: Load model at backend startup, not per request
3. **Input Size**: Resize to YOLO training size (e.g., 640x640) before inference
4. **Batch Size 1**: Single image inference, no batching needed
5. **CPU Inference**: Local deployment likely CPU-only; acceptable given 10s target

**Monitoring**: Log inference time (preprocessing + model forward pass + postprocessing)

---

## Development Workflow Recommendations

### Parallel Development Phases

**Phase 1 - Foundation** (Week 1):
- Backend developer: Implement 2-3 simple filters (Gaussian, Median, Histogram Equalization)
- Frontend developer: Build basic Streamlit UI skeleton with tabs and file uploader
- Model developer: Prepare dataset, explore preprocessing in notebook
- Integration developer: Set up FastAPI structure, basic endpoints

**Phase 2 - Core Features** (Week 2):
- Backend developer: Complete remaining 5 filters (Sobel, Canny, Fourier, DCT, Otsu)
- Frontend developer: Implement filter selection UI and result display
- Model developer: Start YOLOv11s fine-tuning with preprocessed data
- Integration developer: Connect frontend to backend, implement error handling

**Phase 3 - AI Integration** (Week 3):
- Backend developer: Implement YOLO inference API with confidence filtering
- Frontend developer: Build detection tab with bounding box overlay
- Model developer: Complete training, export best model weights
- Integration developer: Integrate trained model, add Vietnamese labels

**Phase 4 - Polish** (Week 4):
- All: Add comprehensive logging, error messages, verification
- All: Manual testing, bug fixes, performance optimization
- Documentation: README with setup instructions, verification steps

---

## Risk Mitigation

### Risk 1: Filter Performance Too Slow

**Mitigation**:
- Profile each filter implementation early
- If >5s for single filter, optimize hot loops or add C extension (numba)
- Fallback: Provide "Fast Mode" with reduced image resolution

### Risk 2: YOLO Training Accuracy Insufficient

**Mitigation**:
- Use extensive data augmentation (preprocessing filters)
- Try different preprocessing combinations
- Fallback: Use pre-trained medical imaging YOLO if available

### Risk 3: Integration Complexity

**Mitigation**:
- Define API contracts early (Phase 1)
- Use OpenAPI spec for frontend-backend communication
- Integration developer starts work early to identify issues

---

## References

- **uv**: https://github.com/astral-sh/uv
- **Streamlit**: https://docs.streamlit.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Ultralytics YOLOv11**: https://docs.ultralytics.com/models/yolo11/
- **WandB**: https://docs.wandb.ai/
- **loguru**: https://loguru.readthedocs.io/
- **NumPy Image Processing**: https://numpy.org/doc/stable/reference/routines.fft.html

---

## Summary

All technology decisions align with:
- ✅ **User Preferences**: uv, Python 3.12.3, Streamlit, FastAPI, YOLOv11s, WandB, loguru
- ✅ **Constitution**: MVP simplicity, no TDD, minimal docs, comprehensive logging, local deployment
- ✅ **Performance Goals**: <5s single filter, <15s multiple, <10s detection
- ✅ **Parallel Development**: 4-developer workflow (backend, frontend, model, integration)

All NEEDS CLARIFICATION items from Technical Context are now resolved with concrete technology selections and implementation strategies.
