# Quickstart Guide

**Feature**: Chest X-Ray Abnormality Detection  
**Date**: 2025-11-08  
**Purpose**: Step-by-step instructions for setting up and verifying the application

---

## Prerequisites

- **Python**: 3.12.3 or higher
- **uv**: Package manager ([install guide](https://github.com/astral-sh/uv#installation))
- **Git**: Version control
- **Storage**: ~2GB free space (for model weights and dataset)
- **Optional**: NVIDIA GPU with CUDA for faster model training (CPU works but slower)

---

## Part 1: Initial Setup

### 1.1 Clone Repository

```bash
git clone <repository-url>
cd Abnormal-prediction-in-chest-X-ray
git checkout 001-xray-abnormality-detection
```

### 1.2 Verify Python Version

```bash
python --version
# Should output: Python 3.12.3 (or higher 3.12.x)
```

### 1.3 Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

---

## Part 2: Backend Setup

### 2.1 Navigate to Backend

```bash
cd backend
```

### 2.2 Create Virtual Environment

```bash
uv venv
```

### 2.3 Activate Virtual Environment

```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 2.4 Install Dependencies

```bash
uv pip install -e .
```

**Expected packages**:
- fastapi
- uvicorn
- python-multipart (for file uploads)
- pillow (image I/O)
- numpy (array operations)
- ultralytics (YOLOv11s)
- loguru (logging)

### 2.5 Create Required Directories

```bash
mkdir -p models logs
```

**Note**: No `uploads/` or `results/` directories needed - all processing happens in memory without file storage.

### 2.6 Download Pre-trained Model (if available)

If you have a fine-tuned model:
```bash
# Copy model weights to backend/models/
cp /path/to/yolov11s_finetuned.pt models/
```

Otherwise, the system will use base YOLOv11s (less accurate for chest X-rays).

### 2.7 Start Backend Server

```bash
uvicorn src.api.main:app --reload --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2.8 Verify Backend Health

Open browser: http://localhost:8000/health

**Expected response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T10:30:00Z"
}
```

### 2.9 View API Documentation

Open browser: http://localhost:8000/docs

You should see interactive Swagger UI with all endpoints.

---

## Part 3: Frontend Setup

### 3.1 Open New Terminal

Keep backend terminal running. Open a new terminal.

### 3.2 Navigate to Frontend

```bash
cd frontend
```

### 3.3 Create Virtual Environment

```bash
uv venv
```

### 3.4 Activate Virtual Environment

```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3.5 Install Dependencies

```bash
uv pip install -e .
```

**Expected packages**:
- streamlit
- requests (for API calls)
- pillow
- numpy

### 3.6 Start Frontend Server

```bash
streamlit run src/app.py
```

**Expected output**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 3.7 Open Web Application

Browser should auto-open to: http://localhost:8501

You should see the application with two tabs:
- **Image Filter Processing**
- **Disease Detection**

---

## Part 4: Basic Verification

### 4.1 Test Image Upload

1. Go to **Image Filter Processing** tab
2. Click "Browse files" or drag-and-drop
3. Upload a chest X-ray image (PNG/JPG, <10MB)
4. Image should display in the interface

**Success indicator**: Original image appears, no error messages

### 4.2 Test Filter Processing

1. Select one filter (e.g., "Gaussian Blur")
2. Click "Apply Filter"
3. Wait for processing (<5 seconds)
4. Processed image appears

**Success indicator**:
- Processed image displayed
- Log message: "Filter applied in X.XXs"
- Download button available

### 4.3 Test Multiple Filters

1. Select 2-3 filters (e.g., "Sobel", "Histogram Equalization", "Canny")
2. Click "Apply Filters"
3. Wait for processing (<15 seconds)
4. All processed images appear in grid

**Success indicator**:
- All selected filters produce results
- No error messages
- Processing time logged

### 4.4 Test Disease Detection

1. Go to **Disease Detection** tab
2. Upload a chest X-ray image
3. Click "Detect Abnormalities"
4. Wait for inference (<10 seconds)
5. Results appear with bounding boxes (if abnormalities) or "Bình thường" (if healthy)

**Success indicator**:
- Detection completes without errors
- If abnormalities: bounding boxes displayed with Vietnamese labels
- If healthy: "Bình thường" message shown
- Health information appears for detected conditions

---

## Part 5: Backend Filter Verification

### 5.1 Test Filter Implementations

Each filter should be tested independently:

```bash
cd backend
python -m src.filters.sobel --test
python -m src.filters.gaussian --test
python -m src.filters.canny --test
# ... repeat for all 8 filters
```

**Success indicator**: Each filter outputs test image without errors

### 5.2 Check Logs

```bash
tail -f logs/app_*.log
```

**Expected log entries**:
```
2025-11-08 10:30:15 | INFO | Image uploaded: chest_xray_001.jpg, size: 2400KB
2025-11-08 10:30:18 | INFO | Filter 'sobel' applied in 0.234s
2025-11-08 10:30:22 | INFO | Detection completed in 0.567s, found 2 abnormalities
```

---

## Part 6: Model Training (Optional - Offline)

### 6.1 Prepare Dataset

Ensure dataset is organized:
```
data/
├── train/
│   ├── images/  # chest X-ray images
│   └── labels/  # YOLO format .txt files
├── val/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

### 6.2 Open Training Notebook

```bash
jupyter notebook notebooks/finetune_yolo.ipynb
```

### 6.3 Configure WandB (Optional)

```python
import wandb
wandb.login()  # Enter API key when prompted
```

### 6.4 Run Training Cells

Execute cells sequentially:
1. Data loading and preprocessing
2. Model initialization (YOLOv11s)
3. Training loop with tqdm progress bars
4. Evaluation on validation set
5. Export trained weights

**Success indicator**:
- tqdm progress bars show epoch-by-epoch progress
- WandB dashboard shows loss curves
- Final model saved to `backend/models/yolov11s_finetuned.pt`

### 6.5 Verify Trained Model

```bash
cd backend
python -m src.models.yolo_detector --test --weights models/yolov11s_finetuned.pt
```

**Expected output**: Detection results on test images with confidence scores

---

## Part 7: End-to-End Workflow Verification

### 7.1 Complete Filter Workflow

1. Upload image → Original displayed
2. Select "Histogram Equalization" → Apply
3. Download processed image
4. Select "Sobel" + "Canny" → Apply both
5. Download both results

**Time**: Should complete in <2 minutes per constitution success criteria

**Logs to check**:
```bash
grep "Filter" logs/app_*.log | tail -20
```

### 7.2 Complete Detection Workflow

1. Upload image → Original displayed
2. Click "Detect Abnormalities" → Processing indicator
3. View annotated image with bounding boxes
4. Read Vietnamese health information
5. Download annotated result

**Time**: Should complete in <3 minutes per constitution success criteria

**Logs to check**:
```bash
grep "Detection" logs/app_*.log | tail -20
```

---

## Part 8: Troubleshooting

### Issue: Backend fails to start

**Symptom**: `uvicorn: command not found`

**Solution**:
```bash
cd backend
source .venv/bin/activate  # Ensure venv is activated
uv pip install uvicorn
```

### Issue: Frontend shows "Connection Error"

**Symptom**: Streamlit can't reach backend API

**Solution**:
1. Verify backend is running: http://localhost:8000/health
2. Check CORS configuration in `backend/src/api/main.py`
3. Check firewall blocking port 8000

### Issue: Filter processing very slow (>10s)

**Symptom**: Single filter takes longer than expected

**Solution**:
1. Check image resolution (resize if >2048x2048)
2. Profile filter code to find bottlenecks
3. Ensure NumPy is using optimized BLAS

### Issue: Model detection returns all "Normal"

**Symptom**: Every X-ray shows "Bình thường", no detections

**Solution**:
1. Verify model weights loaded: `ls -lh backend/models/`
2. Check confidence threshold (should be 0.4, not too high)
3. Test with known abnormal X-ray samples

### Issue: Missing Vietnamese labels

**Symptom**: English class names displayed instead of Vietnamese

**Solution**:
1. Verify `configs/class_mapping.json` exists
2. Check JSON format is valid: `python -m json.tool configs/class_mapping.json`
3. Restart backend to reload configuration

---

## Part 9: Configuration Files

### 9.1 Verify Class Mapping

```bash
cat configs/class_mapping.json
```

**Should contain** 14 disease classes + "Normal" mapped to Vietnamese

### 9.2 Verify Health Information

```bash
cat configs/health_info_vi.json | python -m json.tool
```

**Should contain** Vietnamese descriptions and warnings for each disease

### 9.3 Verify Filter Configuration

```bash
cat backend/src/config/filter_config.json | python -m json.tool
```

**Should contain** fixed parameters for all 8 filters

---

## Part 10: Success Checklist

Before proceeding to `/speckit.tasks`, verify:

- [ ] Backend starts successfully on port 8000
- [ ] Frontend starts successfully on port 8501
- [ ] `/health` endpoint returns 200 OK
- [ ] Image upload works (PNG/JPG, <10MB)
- [ ] All 8 filters produce results
- [ ] Single filter completes in <5 seconds
- [ ] Multiple filters complete in <15 seconds
- [ ] Disease detection completes in <10 seconds
- [ ] Vietnamese labels display correctly
- [ ] Health information shows for detected conditions
- [ ] Logs are written to `logs/` directory
- [ ] Logs contain timestamps, levels, and context
- [ ] Downloaded images are valid and viewable
- [ ] "Bình thường" displays for healthy X-rays
- [ ] Confidence-based display works (solid vs dashed boxes)

---

## Next Steps

Once all verification steps pass:

1. Run `/speckit.tasks` to generate task breakdown
2. Distribute tasks to 4 developers:
   - Backend: Implement 8 filter algorithms
   - Frontend: Build Streamlit UI components
   - Model: Fine-tune YOLOv11s in notebook
   - Integration: Connect frontend-backend, deploy model

3. Follow task dependencies and parallel execution strategy
4. Use this quickstart guide for ongoing verification after each task

---

## Logging Verification

### Expected Log Structure

```
2025-11-08 10:30:15.123 | INFO     | api.routes.upload:upload_image:45 - Image uploaded: chest_xray_001.jpg, size: 2400KB, format: JPEG
2025-11-08 10:30:18.456 | INFO     | filters.sobel:apply:67 - Starting Sobel edge detection on image_id=abc-123
2025-11-08 10:30:18.690 | INFO     | filters.sobel:apply:89 - Sobel completed in 0.234s
2025-11-08 10:30:22.123 | INFO     | models.yolo_detector:predict:112 - Starting detection on image_id=abc-123
2025-11-08 10:30:22.690 | INFO     | models.yolo_detector:predict:145 - Detection completed in 0.567s, found 2 abnormalities (confidence >0.4)
2025-11-08 10:30:22.700 | ERROR    | filters.canny:apply:78 - Canny edge detection failed: Invalid image dimensions (0, 0)
```

### Log File Rotation

Logs rotate at 10MB, keep last 7 days per `loguru` configuration.

---

## Constitution Compliance Verification

✅ **Comprehensive Logging**: All major steps logged with context  
✅ **Manual Testing**: No automated test suite, rely on quickstart verification  
✅ **Local Deployment**: Both servers run locally (ports 8000, 8501)  
✅ **Simple Architecture**: Streamlit + FastAPI, no complex patterns  
✅ **Performance Goals Met**: <5s, <15s, <10s targets verified

---

## Support

If you encounter issues not covered in troubleshooting:
1. Check logs in `backend/logs/` and `frontend/.streamlit/logs/`
2. Verify all dependencies installed: `uv pip list`
3. Test API endpoints individually via Swagger UI: http://localhost:8000/docs
4. Run backend filter tests: `python -m src.filters.<filtername> --test`

---

## Summary

This quickstart provides:
- **Setup Instructions**: Backend + Frontend + Training notebook
- **Verification Steps**: Upload, filter, detection workflows
- **Success Criteria**: Aligned with specification performance goals
- **Troubleshooting**: Common issues and solutions
- **Logging Validation**: Expected log output and rotation
- **Constitution Compliance**: All principles verified

Complete all steps to ensure the foundation is ready for task implementation.
