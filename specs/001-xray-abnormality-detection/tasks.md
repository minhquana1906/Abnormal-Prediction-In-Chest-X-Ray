# Tasks: Chest X-Ray Abnormality Detection

**Feature Branch**: `001-xray-abnormality-detection`  
**Date**: 2025-11-08  
**Input**: Design documents from `/specs/001-xray-abnormality-detection/`

**Team Structure**: 4 Developers working in parallel
- **Developer 1 (Backend - Filters)**: Image processing algorithms
- **Developer 2 (Frontend - UI)**: Streamlit interface
- **Developer 3 (Model - Training)**: YOLOv11s fine-tuning
- **Developer 4 (Integration - API)**: FastAPI routes and connections

**Tests**: No automated tests per constitution - validation through manual testing and comprehensive logging

## Format: `- [ ] [ID] [P?] [Story?] [Dev#] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- **[Dev#]**: Developer responsible (Dev1, Dev2, Dev3, Dev4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure  
**Team**: All developers collaborate

- [ ] T001 [P] [Dev4] Create project structure: `backend/`, `frontend/`, `notebooks/`, `configs/` directories
- [ ] T002 [P] [Dev1] Initialize backend Python project with uv in `backend/pyproject.toml`
- [ ] T003 [P] [Dev2] Initialize frontend Python project with uv in `frontend/pyproject.toml`
- [ ] T004 [P] [Dev3] Create Jupyter notebook structure in `notebooks/`
- [ ] T005 [P] [Dev4] Create configuration files: `configs/class_mapping.json` and `configs/health_info_vi.json`
- [ ] T006 [P] [Dev4] Create `.python-version` file with `3.12.3`
- [ ] T007 [P] [Dev1] Create `backend/models/` directory for YOLO weights storage
- [ ] T008 [P] [Dev2] Create `frontend/src/` directory structure with `pages/`, `components/`, `utils/` subdirectories

**Checkpoint**: Project structure ready - parallel development can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before user stories  
**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation (Developer 1 + 4)

- [ ] T009 [P] [Dev1] Create `backend/src/config/settings.py` with configuration constants (max file size 10MB, allowed formats, performance targets)
- [ ] T010 [P] [Dev1] Create `backend/src/utils/image_utils.py` with image loading and in-memory processing utilities (PIL for I/O, numpy array conversion)
- [ ] T011 [P] [Dev4] Setup loguru logging in `backend/src/utils/logging_config.py` (file rotation, console output, log levels)
- [ ] T012 [P] [Dev4] Create `backend/src/api/main.py` FastAPI application entry point with CORS middleware
- [ ] T013 [Dev4] Create `backend/src/api/middleware/validation.py` with file upload validation (size, format, corruption checks)
- [ ] T014 [Dev4] Create `backend/src/api/middleware/logging.py` with request/response logging middleware

### Frontend Foundation (Developer 2)

- [ ] T015 [P] [Dev2] Create `frontend/src/app.py` Streamlit main application with tab structure
- [ ] T016 [P] [Dev2] Create `frontend/src/utils/api_client.py` for backend HTTP communication
- [ ] T017 [P] [Dev2] Create `frontend/src/components/image_uploader.py` reusable upload widget with Vietnamese error messages
- [ ] T018 [Dev2] Create `frontend/src/utils/ui_helpers.py` with Vietnamese message formatting utilities

### Configuration Foundation (Developer 4)

- [ ] T019 [Dev4] Populate `configs/class_mapping.json` with 14 disease classes + "Bình thường" English-Vietnamese mapping
- [ ] T020 [Dev4] Populate `configs/health_info_vi.json` with Vietnamese health descriptions and warnings for all 14 classes
- [ ] T021 [Dev4] Create `backend/src/utils/class_mapping.py` to load and access class mappings
- [ ] T022 [Dev4] Create `backend/src/utils/health_info.py` to load and access health information

**Checkpoint**: Foundation ready - User Story 1 and 2 can now proceed in parallel

---

## Phase 3: User Story 1 - Image Filter Processing (Priority: P1) 🎯 MVP

**Goal**: Medical professionals can upload chest X-rays and apply 8 custom image processing filters to enhance visualization

**Independent Test**: Upload X-ray → select filters (single or multiple) → receive processed images within performance targets (<5s single, <15s multiple)

**Team**: Developer 1 (Backend - Filters) + Developer 2 (Frontend - UI) + Developer 4 (Integration - API)

### Backend Implementation - Image Filters (Developer 1)

**⚠️ REQUIREMENT**: All filters implemented FROM SCRATCH using NumPy primitives only - NO OpenCV high-level functions

- [ ] T023 [P] [US1] [Dev1] Implement Sobel edge detection in `backend/src/filters/sobel.py` (3x3 Sobel kernels, gradient magnitude calculation using numpy.convolve)
- [ ] T024 [P] [US1] [Dev1] Implement Canny edge detection in `backend/src/filters/canny.py` (Gaussian smoothing, Sobel gradients, non-maximum suppression, double thresholding 100/200, edge tracking)
- [ ] T025 [P] [US1] [Dev1] Implement Gaussian blur in `backend/src/filters/gaussian.py` (2D Gaussian kernel generation sigma=1.4, convolution)
- [ ] T026 [P] [US1] [Dev1] Implement Median filter in `backend/src/filters/median.py` (5x5 sliding window, numpy.median for each window)
- [ ] T027 [P] [US1] [Dev1] Implement Histogram equalization in `backend/src/filters/histogram.py` (histogram calculation, CDF normalization, intensity mapping)
- [ ] T028 [P] [US1] [Dev1] Implement Fourier transform visualization in `backend/src/filters/fourier.py` (numpy.fft.fft2, magnitude spectrum, log transform for display)
- [ ] T029 [P] [US1] [Dev1] Implement Discrete Cosine Transform in `backend/src/filters/dct.py` (numpy.fft-based DCT2, coefficient visualization)
- [ ] T030 [P] [US1] [Dev1] Implement Otsu thresholding in `backend/src/filters/otsu.py` (inter-class variance calculation, optimal threshold search, binary segmentation)
- [ ] T031 [US1] [Dev1] Create `backend/src/filters/__init__.py` with filter registry and metadata (display names, descriptions, fixed parameters)
- [ ] T032 [US1] [Dev1] Add comprehensive logging to all filter implementations (input/output shapes, processing time, parameter values)

### Backend API - Filter Endpoints (Developer 4)

- [ ] T033 [US1] [Dev4] Implement `/upload` endpoint in `backend/src/api/routes/filters.py` (multipart file upload, in-memory storage, return image_id and metadata)
- [ ] T034 [US1] [Dev4] Implement `/filter/list` endpoint in `backend/src/api/routes/filters.py` (return available filters with display names and descriptions)
- [ ] T035 [US1] [Dev4] Implement `/filter/apply` endpoint in `backend/src/api/routes/filters.py` (accept image_id + filter names, apply filters in-memory, return base64-encoded results with timing)
- [ ] T036 [US1] [Dev4] Add error handling for filter processing failures with Vietnamese error messages

### Frontend UI - Filter Processing Tab (Developer 2)

- [ ] T037 [US1] [Dev2] Implement `frontend/src/pages/filter_processing.py` tab with file uploader component
- [ ] T038 [US1] [Dev2] Implement filter selection UI in `frontend/src/components/filter_selector.py` (multi-select for 8 filters)
- [ ] T039 [US1] [Dev2] Implement result display in `frontend/src/components/result_display.py` (original + processed images side-by-side, processing time labels)
- [ ] T040 [US1] [Dev2] Add "Apply Filters" button with st.spinner() progress indicator
- [ ] T041 [US1] [Dev2] Add download buttons for processed images (base64 to file download)
- [ ] T042 [US1] [Dev2] Add Vietnamese error handling UI (st.error with retry option)

**Checkpoint US1**: Filter processing feature complete - verify full workflow (upload → select → apply → view → download)

---

## Phase 4: User Story 2 - Disease Detection (Priority: P2)

**Goal**: Medical professionals can upload chest X-rays to detect abnormalities with bounding boxes, Vietnamese labels, and health information

**Independent Test**: Upload X-ray with/without abnormalities → receive annotated image with bounding boxes (3-tier confidence) and health warnings within 10s

**Team**: Developer 4 (Integration - API) + Developer 2 (Frontend - UI) + Developer 3 (Model - Training provides weights)

**⚠️ DEPENDENCY**: Requires trained YOLOv11s model weights from User Story 3 (can start with base model, improve with fine-tuned)

### Backend Implementation - YOLO Inference (Developer 4)

- [ ] T043 [US2] [Dev4] Implement `backend/src/models/yolo_detector.py` YOLO wrapper class (load model from `backend/models/yolov11s_finetuned.pt`, predict method, confidence filtering ≥0.4)
- [ ] T044 [US2] [Dev4] Implement confidence tier classification in `yolo_detector.py` (>70% high/solid, 40-70% medium/dashed, <40% hidden)
- [ ] T045 [US2] [Dev4] Implement bounding box drawing in `yolo_detector.py` (draw boxes on numpy array in-memory with solid/dashed styles, Vietnamese labels from class_mapping)
- [ ] T046 [US2] [Dev4] Add health information lookup in `yolo_detector.py` (map detected classes to Vietnamese descriptions + warnings)
- [ ] T047 [US2] [Dev4] Add comprehensive logging to YOLO inference (model load time, inference time, detected classes with confidence scores)

### Backend API - Detection Endpoints (Developer 4)

- [ ] T048 [US2] [Dev4] Implement `/detect/analyze` endpoint in `backend/src/api/routes/detection.py` (accept image_id, run YOLO inference, return detections + annotated image base64)
- [ ] T049 [US2] [Dev4] Add "Bình thường" handling for healthy images (is_normal flag when no detections ≥0.4 confidence)
- [ ] T050 [US2] [Dev4] Add error handling for detection failures with Vietnamese error messages

### Frontend UI - Detection Tab (Developer 2)

- [ ] T051 [US2] [Dev2] Implement `frontend/src/pages/detection.py` tab with file uploader component
- [ ] T052 [US2] [Dev2] Implement detection result display showing annotated image with bounding boxes
- [ ] T053 [US2] [Dev2] Implement health information cards in `frontend/src/components/health_card.py` (display condition descriptions + warnings in Vietnamese with icons)
- [ ] T054 [US2] [Dev2] Add "Analyze Image" button with st.spinner() progress indicator
- [ ] T055 [US2] [Dev2] Add download button for annotated image
- [ ] T056 [US2] [Dev2] Add "Bình thường" display for healthy images (no bounding boxes, positive message)
- [ ] T057 [US2] [Dev2] Add Vietnamese error handling UI for detection failures

**Checkpoint US2**: Disease detection feature complete - verify with healthy and abnormal X-ray test images

---

## Phase 5: User Story 3 - Model Training (Priority: P3)

**Goal**: Researchers can fine-tune YOLOv11s offline in Jupyter notebook with preprocessing, auto-labeling, and experiment tracking

**Independent Test**: Run notebook → download dataset from Roboflow → preprocess with filters → auto-label normal images → train with tqdm + WandB → export weights → verify improved detection accuracy

**Team**: Developer 3 (Model - Training) + Developer 1 (provides filter implementations for preprocessing)

**⚠️ NOTE**: This is an OFFLINE task, not part of web application UI

### Dataset Preparation (Developer 3)

- [ ] T058 [US3] [Dev3] Create `notebooks/finetune_yolo.ipynb` notebook with markdown documentation
- [ ] T059 [US3] [Dev3] Add dataset download cell using Roboflow API (API key: wQ9S049DhK8xjIhNy6zv, project: chest-xray-symptom-detection, version 3, format: YOLOv11)
- [ ] T060 [US3] [Dev3] Add auto-labeling cell for images without bounding boxes (scan labels directory, assign "Bình thường" class to images with empty/missing .txt files)
- [ ] T061 [US3] [Dev3] Add class mapping verification cell (confirm all 14 English classes map to Vietnamese, update YOLO dataset.yaml with Vietnamese names)

### Preprocessing and Augmentation (Developer 3 with Developer 1's filters)

- [ ] T062 [US3] [Dev3] Import filter implementations from `backend/src/filters/` into notebook
- [ ] T063 [US3] [Dev3] Add preprocessing cell applying selected filters to training images (Histogram Equalization + Gaussian Blur for contrast enhancement)
- [ ] T064 [US3] [Dev3] Add data augmentation cell with filter-based augmentation (random filter combinations, geometric transforms, brightness/contrast adjustments)
- [ ] T065 [US3] [Dev3] Add augmented dataset statistics visualization (class distribution, image dimensions, normal vs abnormal ratio)

### Model Training (Developer 3)

- [ ] T066 [US3] [Dev3] Add WandB initialization cell (project name: "chest-xray-detection", log hyperparameters)
- [ ] T067 [US3] [Dev3] Add YOLOv11s training cell with ultralytics (load base yolov11s.pt, set hyperparameters: epochs=50, batch=16, imgsz=640, patience=10)
- [ ] T068 [US3] [Dev3] Add tqdm progress tracking integration (epoch progress, batch progress, loss/mAP display)
- [ ] T069 [US3] [Dev3] Add WandB logging integration (log loss curves, mAP, precision, recall per epoch)
- [ ] T070 [US3] [Dev3] Add model export cell (save best weights to `backend/models/yolov11s_finetuned.pt`)

### Validation and Analysis (Developer 3)

- [ ] T071 [US3] [Dev3] Add validation cell testing model on test set (calculate mAP, confusion matrix, per-class accuracy)
- [ ] T072 [US3] [Dev3] Add Vietnamese label verification cell (ensure predictions use Vietnamese class names from mapping)
- [ ] T073 [US3] [Dev3] Add sample prediction visualization cell (show test images with bounding boxes + Vietnamese labels + confidence scores)
- [ ] T074 [US3] [Dev3] Add model comparison cell (base YOLOv11s vs fine-tuned accuracy on test set)

**Checkpoint US3**: Training notebook complete - run end-to-end and verify model weights exported to `backend/models/`

---

## Phase 6: Integration and Polish

**Purpose**: Connect all components, comprehensive logging, final validation  
**Team**: All developers collaborate

### Cross-Component Integration (Developer 4)

- [ ] T075 [Dev4] Verify frontend-backend API communication for both User Stories 1 and 2
- [ ] T076 [Dev4] Test trained model integration with detection API (load weights from `backend/models/yolov11s_finetuned.pt`)
- [ ] T077 [Dev4] Add `/health` endpoint in `backend/src/api/main.py` for API health check
- [ ] T078 [Dev4] Test CORS configuration for Streamlit-FastAPI communication (backend port 8000, frontend port 8501)

### Logging Enhancement (All Developers)

- [ ] T079 [P] [Dev1] Add detailed timing logs to all filter implementations (per-filter processing time, total time for multiple filters)
- [ ] T080 [P] [Dev4] Add request/response logging for all API endpoints (request ID, parameters, response time, status codes)
- [ ] T081 [P] [Dev2] Add user interaction logging in frontend (image upload, filter selections, button clicks)
- [ ] T082 [P] [Dev3] Add training progress logging in notebook (epoch times, best model metrics, final validation results)

### Performance Validation (Developer 1 + 4)

- [ ] T083 [Dev1] Verify single filter processing time <5s for 1024x1024 images (log timing for each filter)
- [ ] T084 [Dev1] Verify multiple filter processing time <15s for 8 filters on 1024x1024 image (optimize hot loops if needed)
- [ ] T085 [Dev4] Verify detection inference time <10s for 1024x1024 images (profile model loading + inference + postprocessing)
- [ ] T086 [Dev4] Optimize memory usage for in-memory image processing (ensure no memory leaks, clear arrays after processing)

### Error Handling and Edge Cases (Developer 2 + 4)

- [ ] T087 [P] [Dev2] Add Vietnamese error messages for all failure scenarios (file too large, invalid format, corrupted image, network error)
- [ ] T088 [P] [Dev4] Add input validation for all API endpoints (image_id existence, filter name validation, file format checks)
- [ ] T089 [Dev4] Add graceful handling for missing model weights (display helpful error message with setup instructions)
- [ ] T090 [Dev2] Add user guidance for edge cases (image too small, no abnormalities detected, processing timeout)

### Documentation and Verification (All Developers)

- [ ] T091 [P] [Dev1] Document filter implementation details in `backend/src/filters/README.md` (algorithms, parameters, performance notes)
- [ ] T092 [P] [Dev2] Document frontend setup in `frontend/README.md` (dependencies, startup command, usage guide)
- [ ] T093 [P] [Dev4] Document backend setup in `backend/README.md` (dependencies, startup command, API endpoints)
- [ ] T094 [P] [Dev3] Document training notebook in `notebooks/README.md` (dataset download, training steps, model export)
- [ ] T095 [Dev4] Follow `specs/001-xray-abnormality-detection/quickstart.md` validation steps (verify all success criteria)

**Final Checkpoint**: Complete system validated - all user stories functional, performance targets met, logging comprehensive

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← CRITICAL BLOCKER
    ↓
    ├─→ Phase 3 (US1 - Filter Processing) ← MVP
    ├─→ Phase 4 (US2 - Disease Detection) ← depends on US3 model weights (can use base model initially)
    └─→ Phase 5 (US3 - Model Training) ← offline task, runs in parallel
    ↓
Phase 6 (Integration & Polish)
```

### User Story Dependencies

- **US1 (P1 - Filters)**: Independent - can complete fully after Phase 2
- **US2 (P2 - Detection)**: Requires Phase 2 + optionally US3 weights (can start with base YOLOv11s)
- **US3 (P3 - Training)**: Requires Dev1's filter implementations for preprocessing (can run in parallel with US2 development)

### Developer Workflows (Parallel Execution)

**Week 1: Foundation**
- All Devs: Phase 1 (Setup) together
- All Devs: Phase 2 (Foundational) together
- **Blocker**: Must complete Phase 2 before user stories

**Week 2-3: Parallel User Story Development**
- **Dev1**: T023-T032 (implement 8 filters) → US1 complete
- **Dev2**: T037-T042 (filter UI) → US1 complete, then T051-T057 (detection UI) → US2 complete
- **Dev3**: T058-T074 (training notebook) → US3 complete (runs overnight)
- **Dev4**: T033-T036 (filter API) → US1 complete, then T043-T050 (detection API) → US2 complete

**Week 4: Integration & Polish**
- All Devs: Phase 6 (Integration, logging, validation)

### Critical Path

```
Setup (T001-T008)
    ↓
Foundational (T009-T022) ← MUST COMPLETE FIRST
    ↓
    ├─→ US1: T023-T042 (filters + filter UI + filter API) ← MVP delivery point
    │   ↓
    │   US2: T043-T057 (detection + detection UI + detection API) ← enhanced with US3 weights
    │
    └─→ US3: T058-T074 (training notebook) ← runs in parallel, provides weights to US2
    ↓
Integration: T075-T095 (connect + log + validate)
```

### Parallel Opportunities by Phase

**Phase 2 (Foundational)**:
- T009, T010, T011 (backend utils) - Dev1
- T012, T013, T014 (API setup) - Dev4
- T015, T016, T017, T018 (frontend setup) - Dev2
- T019, T020, T021, T022 (config files) - Dev4

**Phase 3 (US1)**:
- T023-T030 (all 8 filters) - Dev1 can work on multiple filters in parallel
- T037-T042 (frontend UI) - Dev2 works in parallel with Dev1
- T033-T036 (backend API) - Dev4 works in parallel with Dev1

**Phase 4 (US2)**:
- T043-T047 (YOLO wrapper) - Dev4
- T051-T057 (detection UI) - Dev2 works in parallel with Dev4

**Phase 5 (US3)**:
- T058-T074 (entire training notebook) - Dev3 works independently, can run overnight

**Phase 6 (Integration)**:
- T079-T082 (logging) - all devs in parallel on their domains
- T087-T088 (error handling) - Dev2 + Dev4 in parallel
- T091-T094 (documentation) - all devs in parallel

---

## Implementation Strategy

### MVP First (US1 Only - 2 weeks)

1. ✅ Complete Phase 1: Setup (1 day)
2. ✅ Complete Phase 2: Foundational (2-3 days) ← CRITICAL BLOCKER
3. ✅ Complete Phase 3: User Story 1 - Filter Processing (1 week)
   - Dev1: Implement all 8 filters from scratch
   - Dev2: Build filter UI
   - Dev4: Create filter API endpoints
4. **STOP and VALIDATE**: Test filter processing independently (quickstart.md Part 4-5)
5. **DEMO READY**: Working filter processing feature

### Incremental Delivery (US1 → US2 → US3)

**Week 1**: Setup + Foundational → Foundation ready  
**Week 2**: Add User Story 1 → Test → **Deploy MVP!**  
**Week 3**: Add User Story 2 (with base YOLO) → Test → Deploy enhanced version  
**Week 3-4**: Run User Story 3 training overnight → Export weights → Update US2 with fine-tuned model  
**Week 4**: Integration & Polish → Final validation

### Parallel Team Strategy (4 Developers)

**Week 1 (Together)**:
- Mon-Tue: Phase 1 (Setup) - all devs collaborate
- Wed-Fri: Phase 2 (Foundational) - parallel tasks within phase

**Week 2-3 (Parallel)**:
- **Dev1 (Backend-Filters)**: T023-T032 (8 filters from scratch) → US1 backend done
- **Dev2 (Frontend-UI)**: T037-T042 (filter UI) → US1 frontend done, then T051-T057 (detection UI) → US2 frontend done
- **Dev3 (Model-Training)**: T058-T074 (training notebook) → US3 done, provides weights for US2
- **Dev4 (Integration-API)**: T033-T036 (filter API) → US1 API done, then T043-T050 (detection API) → US2 API done

**Week 4 (Together)**:
- All: Phase 6 (Integration, logging, validation, documentation)

---

## Task Summary

### Total Tasks: 95

**By Phase**:
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 14 tasks
- Phase 3 (US1 - Filters): 20 tasks
- Phase 4 (US2 - Detection): 15 tasks
- Phase 5 (US3 - Training): 17 tasks
- Phase 6 (Integration & Polish): 21 tasks

**By Developer**:
- Developer 1 (Backend-Filters): ~25 tasks (filters + utils)
- Developer 2 (Frontend-UI): ~20 tasks (Streamlit UI + components)
- Developer 3 (Model-Training): ~17 tasks (Jupyter notebook)
- Developer 4 (Integration-API): ~25 tasks (FastAPI + integration)
- Shared/All: ~8 tasks (setup, documentation)

**By User Story**:
- Setup/Foundational: 22 tasks (prerequisites)
- User Story 1 (P1 - Filters): 20 tasks (MVP)
- User Story 2 (P2 - Detection): 15 tasks
- User Story 3 (P3 - Training): 17 tasks (offline)
- Integration/Polish: 21 tasks (cross-cutting)

**Parallel Opportunities**: 45+ tasks marked [P] can run in parallel within their phase/developer

**MVP Scope (Recommended)**: Phase 1 + Phase 2 + Phase 3 (US1) = 42 tasks → ~2 weeks with 4 developers

---

## Notes

- All filters MUST be implemented from scratch using NumPy primitives - NO OpenCV high-level functions (cv2.Canny, cv2.GaussianBlur, etc.)
- No automated tests per constitution - validation through manual testing following quickstart.md
- Comprehensive logging with loguru required for all major operations (upload, processing, detection, training)
- All error messages in Vietnamese for user-facing components
- Images processed entirely in-memory - no file storage except model weights
- Training notebook is OFFLINE task separate from web application
- Performance targets: <5s single filter, <15s multiple filters, <10s detection
- Each user story should be independently testable and deployable
- Commit after logical task groups, stop at checkpoints to validate
- Use Vietnamese labels from `configs/class_mapping.json` consistently
