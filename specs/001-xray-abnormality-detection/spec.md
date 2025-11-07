# Feature Specification: Chest X-Ray Abnormality Detection Web Application

**Feature Branch**: `001-xray-abnormality-detection`  
**Created**: 2025-11-08  
**Status**: Draft  
**Input**: User description: "Xây dựng web application cho việc nhận diện các điểm bất thường trong ảnh X-ray ngực với 2 chức năng chính: (1) Áp dụng các bộ lọc xử lý ảnh và (2) Finetune YOLOv11s để phát hiện 14 class bệnh với mapping tiếng Việt"

## Clarifications

### Session 2025-11-08

- Q: When the AI model detects abnormalities, how should the system handle low-confidence detections to balance sensitivity with specificity? → A: Use three-tier display: high confidence (>70%) solid boxes, medium (40-70%) dashed boxes, low (<40%) hidden
- Q: What is the maximum file size for uploaded chest X-ray images to prevent system overload while accommodating high-resolution medical images? → A: 10MB maximum, accept only .png, .jpg, .jpeg files
- Q: Should users be able to adjust parameters for image filters or use fixed default values optimized for chest X-rays? → A: Use fixed default parameters optimized for chest X-ray analysis
- Q: When image processing fails, how should the system communicate this to users? → A: Show user-friendly Vietnamese error message explaining the issue with retry/upload new image option
- Q: For model training (offline task), how should progress be tracked? → A: Training in separate Jupyter notebook with tqdm progress bars per epoch and basic WandB tracking

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Image Filter Processing (Priority: P1)

A medical professional or radiologist uploads a chest X-ray image and wants to apply various image processing filters to enhance visualization and analyze different aspects of the image. They can select one or multiple filters (Sobel, Canny Edge Detection, Gaussian Blur, Median Filter, Histogram Equalization, Fourier Transform, Discrete Cosine Transform, Otsu thresholding) and immediately see the processed results.

**Why this priority**: This is the foundational feature that provides immediate value for image analysis and enhancement. It can be used independently without the AI detection model, making it the perfect MVP starting point. Medical professionals need image enhancement tools to better visualize anatomical structures.

**Independent Test**: Can be fully tested by uploading a chest X-ray image, selecting any combination of filters, and receiving processed images showing the applied transformations. Success is verified when all 8 filter types produce correct visual outputs.

**Acceptance Scenarios**:

1. **Given** the user is on the Image Filter Processing tab, **When** they upload a chest X-ray image, **Then** the system displays the original image ready for processing
2. **Given** an image is uploaded, **When** the user selects a single filter (e.g., Gaussian Blur), **Then** the system displays the processed result image with the applied filter
3. **Given** an image is uploaded, **When** the user selects multiple filters (e.g., Histogram Equalization + Sobel), **Then** the system displays all processed result images, one for each selected filter
4. **Given** processed images are displayed, **When** the user wants to download results, **Then** the system allows downloading the processed images
5. **Given** processed images are displayed, **When** the user wants to try different filters, **Then** the system allows selecting new filters without re-uploading the image

---

### User Story 2 - Disease Detection with Bounding Boxes (Priority: P2)

A medical professional uploads a chest X-ray image to detect potential abnormalities. The system analyzes the image and returns results showing detected conditions with bounding boxes highlighting the affected areas. Each detected condition is labeled in Vietnamese with accompanying health information and warnings.

**Why this priority**: This is the core AI-powered diagnostic assistance feature. While valuable, it depends on model training being complete and is more complex than filter processing. It provides critical diagnostic support but can be developed after the filter processing foundation is established.

**Independent Test**: Can be fully tested by uploading various chest X-ray images (both healthy and with abnormalities) and verifying that the system correctly identifies conditions, draws accurate bounding boxes, displays Vietnamese labels, and shows appropriate health warnings for detected conditions. Healthy images should return results with no bounding boxes and a "Bình thường" (normal) indication.

**Acceptance Scenarios**:

1. **Given** the user is on the Disease Detection tab, **When** they upload a chest X-ray image with abnormalities, **Then** the system displays the image with bounding boxes around detected abnormalities
2. **Given** abnormalities are detected, **When** the results are displayed, **Then** each bounding box shows the Vietnamese label for the detected condition (e.g., "Tràn dịch màng phổi")
3. **Given** abnormalities are detected, **When** the results are displayed, **Then** the system shows detailed health information and warnings in Vietnamese for each detected condition
4. **Given** the user uploads a healthy chest X-ray with no abnormalities, **When** the detection completes, **Then** the system displays the image without bounding boxes and indicates "Bình thường" (normal/healthy)
5. **Given** multiple conditions are detected in one image, **When** the results are displayed, **Then** all detected conditions are shown with separate bounding boxes and distinct labels
6. **Given** detection results are displayed, **When** the user wants to save the annotated image, **Then** the system allows downloading the image with bounding boxes and labels

---

### User Story 3 - Model Training with Enhanced Preprocessing (Priority: P3)

A researcher or administrator wants to improve the detection model's accuracy by fine-tuning it with preprocessed training data. This is an **offline task** performed outside the web application using a Jupyter notebook. The notebook applies appropriate image processing filters during preprocessing and data augmentation phases, automatically labels images without bounding boxes as "Bình thường" (normal), and maps all 14 disease classes from English to Vietnamese. Training progress is tracked using tqdm progress bars and WandB.

**Why this priority**: This is an offline development/maintenance task, not a web UI feature. It's essential for model improvement but happens outside the user-facing application flow. The web UI only handles inference (User Story 2) using the trained model, not the training process itself.

**Independent Test**: Can be fully tested by running the training notebook, verifying that preprocessing filters are correctly applied to the dataset, confirming that images without bounding boxes receive the "Bình thường" label, validating that all 14 disease class names are mapped to Vietnamese, observing tqdm progress bars showing epoch-by-epoch progress, checking WandB dashboard for training metrics, and confirming the fine-tuned model produces improved detection results when loaded into the web application.

**Acceptance Scenarios**:

1. **Given** a researcher opens the training notebook, **When** they execute the preprocessing cells, **Then** the notebook applies selected image processing filters to enhance training images
2. **Given** the training dataset contains images without bounding boxes, **When** preprocessing occurs, **Then** these images are automatically labeled as "Bình thường" (normal) class
3. **Given** the training dataset has 14 disease classes in English, **When** the notebook processes the dataset, **Then** all class names are mapped to Vietnamese equivalents (e.g., "Pleural effusion" → "Tràn dịch màng phổi")
4. **Given** training begins, **When** each epoch runs, **Then** tqdm displays progress bars showing completion percentage and metrics
5. **Given** WandB is configured, **When** training proceeds, **Then** loss values, accuracy metrics, and training progress are logged to WandB dashboard
6. **Given** model training completes successfully, **When** the trained model file is saved, **Then** the detection feature (User Story 2) can load and use the updated model with improved accuracy
7. **Given** data augmentation is enabled, **When** training proceeds, **Then** the notebook applies appropriate filters to augment the training dataset and improve model robustness

---

### Edge Cases

- What happens when a user uploads a non-X-ray image (e.g., a photo or unrelated medical scan)?
- How does the system handle files that exceed the 10MB size limit or are not in PNG/JPG/JPEG format (display Vietnamese error message with option to upload new file)?
- How does the system handle corrupted or incomplete image files (display Vietnamese error message explaining the issue with retry option)?
- What occurs when the image resolution is too low for meaningful analysis or too high causing processing delays?
- How does the system respond when filter processing fails due to image characteristics (display Vietnamese error message with option to try different filter or upload new image)?
- What happens when the AI model detects conditions with varying confidence levels (system displays high >70% as solid boxes, medium 40-70% as dashed boxes, hides low <40%)?
- How does the system handle multiple overlapping bounding boxes for the same region?
- What occurs when a user tries to apply filters or run detection on extremely large batch of images simultaneously?
- How does the system behave when the training dataset has inconsistent labels or missing annotations?
- What happens when internet connectivity is lost during image upload or processing?

## Requirements *(mandatory)*

### Functional Requirements

#### Image Upload & Management

- **FR-001**: System MUST accept chest X-ray images in PNG, JPG, and JPEG formats only
- **FR-001a**: System MUST enforce a maximum file size limit of 10MB per uploaded image
- **FR-002**: System MUST validate uploaded images to ensure they are valid image files in the accepted formats and within size limits
- **FR-003**: System MUST display the uploaded original image before any processing
- **FR-004**: System MUST allow users to upload a new image at any time, replacing the current one

#### Image Filter Processing (Tab 1)

- **FR-005**: System MUST provide 8 distinct image processing filters: Sobel, Canny Edge Detection, Gaussian Blur, Median Filter, Histogram Equalization, Fourier Transform, Discrete Cosine Transform, and Otsu thresholding
- **FR-006**: All image processing filters MUST be implemented from scratch without using pre-built library functions for the core algorithms
- **FR-006a**: All image processing filters MUST use fixed default parameters optimized for chest X-ray analysis (no user parameter adjustment)
- **FR-007**: Users MUST be able to select one or multiple filters to apply to the uploaded image
- **FR-008**: System MUST display processed result images for each selected filter
- **FR-009**: System MUST allow users to download processed images
- **FR-010**: System MUST maintain the original image unchanged while showing processed versions

#### Disease Detection (Tab 2)

- **FR-011**: System MUST analyze chest X-ray images to detect abnormalities across 14 disease classes: Aortic enlargement, Atelectasis, Calcification, Cardiomegaly, Consolidation, ILD, Infiltration, Lung Opacity, Nodule-Mass, Other lesion, Pleural effusion, Pleural thickening, Pneumothorax, Pulmonary fibrosis
- **FR-012**: System MUST display bounding boxes around detected abnormalities on the X-ray image
- **FR-012a**: System MUST use three-tier confidence-based visualization: high confidence detections (>70%) shown with solid bounding boxes, medium confidence (40-70%) shown with dashed bounding boxes, low confidence (<40%) hidden from display
- **FR-013**: System MUST label each bounding box with the Vietnamese translation of the detected condition
- **FR-014**: System MUST map all 14 disease classes from English to Vietnamese using the specified mapping
- **FR-015**: For images with no detected abnormalities, system MUST display the image without bounding boxes and indicate "Bình thường" (normal/healthy status)
- **FR-016**: For each detected abnormality, system MUST display comprehensive health information in Vietnamese including condition description and health warnings
- **FR-017**: Health warnings MUST include a disclaimer advising users to consult with medical professionals for accurate diagnosis
- **FR-018**: System MUST allow users to download the annotated image with bounding boxes and labels

#### Model Training & Dataset Management (Offline Jupyter Notebook)

- **FR-019**: Training notebook MUST support fine-tuning process using the training, validation, and test dataset splits
- **FR-020**: Training notebook MUST automatically assign the "Bình thường" class label to all images in the dataset that have no bounding boxes
- **FR-021**: Training notebook MUST apply appropriate image processing filters during the preprocessing phase to enhance training data quality
- **FR-022**: Training notebook MUST apply appropriate image processing filters during data augmentation to increase dataset diversity
- **FR-023**: Training notebook MUST maintain the English-to-Vietnamese class name mapping throughout the training and inference pipeline
- **FR-023a**: Training notebook MUST display epoch-by-epoch progress using tqdm progress bars
- **FR-023b**: Training notebook MUST log training metrics (loss, accuracy, mAP) to WandB for experiment tracking

#### User Interface (Web Application)

- **FR-024**: Web application MUST organize functionality into 2 distinct tabs: "Image Filter Processing" (apply filters and observe results) and "Disease Detection" (inference on uploaded images)
- **FR-025**: Web application MUST provide a responsive and intuitive interface for image upload, filter selection, and result viewing
- **FR-026**: System MUST display processing status and progress indicators during filter application and disease detection
- **FR-026a**: System MUST display user-friendly error messages in Vietnamese when processing fails, explaining the issue and providing retry or upload new image options

#### Logging & Monitoring

- **FR-027**: System MUST log all major workflow steps including image upload, filter processing, model inference, and training operations
- **FR-028**: System MUST log errors with sufficient context for debugging (file paths, filter names, class labels, error messages)
- **FR-029**: System MUST log key metrics such as processing time, detection confidence scores, and training progress

### Key Entities

- **Uploaded Image**: A chest X-ray image file provided by the user. Contains pixel data, format information, dimensions, and file path.

- **Processed Image**: The result of applying one or more image processing filters to an uploaded image. Associated with the original image and the specific filter(s) applied.

- **Image Filter**: A processing algorithm (Sobel, Canny, Gaussian Blur, etc.) that transforms the input image. Has a name, algorithm implementation, and fixed default parameters optimized for chest X-ray images.

- **Disease Class**: One of 14 possible abnormality types detectable in chest X-rays. Contains English name, Vietnamese translation, and associated health information text.

- **Detection Result**: Output from the AI model analyzing an X-ray image. Contains bounding box coordinates, detected class labels, confidence scores, and Vietnamese translations.

- **Bounding Box**: A rectangular region highlighting a detected abnormality. Contains coordinates (x, y, width, height), associated disease class, and confidence score.

- **Health Information**: Educational content about a detected condition. Contains Vietnamese description, symptoms, and medical consultation warning text.

- **Training Dataset**: Collection of chest X-ray images with annotations used for model fine-tuning in offline Jupyter notebook. Organized into train/validation/test splits, includes images with and without bounding boxes.

- **Training Notebook**: Jupyter notebook for offline model fine-tuning. Contains code for data preprocessing, augmentation, YOLOv11s training with tqdm progress bars, and WandB experiment tracking.

- **Class Mapping**: Translation dictionary mapping 14 English disease class names to Vietnamese equivalents. Used in both training notebook and web application for labeling and display.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload a chest X-ray image and apply any single filter, receiving the processed result within 5 seconds for standard resolution images (512x512 to 2048x2048 pixels)

- **SC-002**: Users can select and apply multiple filters simultaneously (up to all 8 filters), receiving all processed results within 15 seconds

- **SC-003**: The disease detection feature analyzes uploaded X-ray images and returns annotated results with bounding boxes and Vietnamese labels within 10 seconds

- **SC-004**: All 14 disease classes are correctly mapped from English to Vietnamese and displayed consistently across the application

- **SC-005**: Images without abnormalities are correctly classified as "Bình thường" with no false positive bounding boxes in at least 90% of healthy test images

- **SC-006**: Detected abnormalities display complete health information including Vietnamese condition descriptions and medical consultation warnings for 100% of detected cases

- **SC-007**: Users can successfully complete the full workflow (upload → apply filters → view results → download) for the image processing tab in under 2 minutes

- **SC-008**: Users can successfully complete the full workflow (upload → detect abnormalities → view annotated results → read health info → download) for the disease detection tab in under 3 minutes

- **SC-009**: The offline training notebook successfully completes fine-tuning with dataset preprocessing, automatic normal class labeling, filter-based augmentation, tqdm progress display, and WandB metric logging, producing a model that improves detection accuracy compared to the base YOLOv11s model

- **SC-010**: All major workflow steps in the web application (upload, filter processing, disease detection) and training notebook (preprocessing, training epochs, model saving) produce detailed logs that enable verification and debugging

## Assumptions

- Users have access to chest X-ray images in PNG, JPG, or JPEG formats with file sizes under 10MB
- The fine-tuned model will be based on YOLOv11s architecture with pre-trained weights
- **Training dataset source**: The dataset is obtained from Roboflow Universe (https://universe.roboflow.com/vinbigdataxrayproject/chest-xray-symptom-detection) and can be downloaded in YOLOv11 format directly in Jupyter notebook using the Roboflow API
- The training dataset contains images with annotations for the 14 disease classes, plus unlabeled healthy images
- Vietnamese translations and health information texts are prepared and available as reference data
- The application will run on a local machine with sufficient computational resources for image processing and model inference
- Users have basic computer literacy and can navigate web applications with multiple tabs
- Internet connectivity is available for initial application access but processing can happen locally after page load
- Internet connectivity is required for downloading the training dataset from Roboflow (offline task in Jupyter notebook)
- **No persistent storage**: All image processing happens in memory, results are displayed immediately and not saved to disk (MVP simplicity)
