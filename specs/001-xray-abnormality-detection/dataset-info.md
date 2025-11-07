# Dataset Information

**Feature**: Chest X-Ray Abnormality Detection  
**Date**: 2025-11-08  
**Phase**: Dataset Acquisition & Setup

## Dataset Source

**Provider**: Roboflow Universe  
**Project**: VinBigData Chest X-ray Symptom Detection  
**URL**: <https://universe.roboflow.com/vinbigdataxrayproject/chest-xray-symptom-detection>  
**Version**: 3  
**Format**: YOLOv11

---

## Download Instructions

The dataset can be downloaded directly in a Jupyter notebook using the Roboflow Python SDK.

### Prerequisites

```bash
pip install roboflow
```

### Download Code

```python
from roboflow import Roboflow

# Initialize Roboflow with API key
rf = Roboflow(api_key="wQ9S049DhK8xjIhNy6zv")

# Access the project
project = rf.workspace("vinbigdataxrayproject").project("chest-xray-symptom-detection")

# Get version 3 of the dataset
version = project.version(3)

# Download in YOLOv11 format
dataset = version.download("yolov11")
```

### Usage in Training Notebook

Place this code in the **Data Loading** section of your training notebook:

```python
# Cell 1: Install dependencies
!pip -q install roboflow

# Cell 2: Download dataset
from roboflow import Roboflow

rf = Roboflow(api_key="wQ9S049DhK8xjIhNy6zv")
project = rf.workspace("vinbigdataxrayproject").project("chest-xray-symptom-detection")
version = project.version(3)
dataset = version.download("yolov11")

# Dataset will be downloaded to: ./Chest-Xray-Symptom-Detection-3/
print(f"Dataset location: {dataset.location}")
```

---

## Dataset Structure

After downloading, the dataset follows this structure:

```text
Chest-Xray-Symptom-Detection-3/
├── train/
│   ├── images/           # Training images
│   └── labels/           # YOLO format annotations (.txt files)
├── valid/
│   ├── images/           # Validation images
│   └── labels/           # YOLO format annotations
├── test/
│   ├── images/           # Test images
│   └── labels/           # YOLO format annotations
└── data.yaml             # Dataset configuration file
```

---

## Dataset Configuration

The `data.yaml` file contains:

- **Train/Val/Test paths**: Relative paths to image directories
- **Number of classes**: 14 disease classes
- **Class names**: English names for the 14 chest X-ray abnormalities

Example `data.yaml`:

```yaml
train: ../train/images
val: ../valid/images
test: ../test/images

nc: 14
names: ['Aortic enlargement', 'Atelectasis', 'Calcification', 'Cardiomegaly', 
        'Consolidation', 'ILD', 'Infiltration', 'Lung Opacity', 'Nodule-Mass', 
        'Other lesion', 'Pleural effusion', 'Pleural thickening', 
        'Pneumothorax', 'Pulmonary fibrosis']
```

---

## YOLO Format Annotations

Each image has a corresponding `.txt` file in the `labels/` directory.

**Format**: `<class_id> <x_center> <y_center> <width> <height>`

- All coordinates are normalized (0.0 to 1.0)
- `class_id`: Integer index from 0 to 13 (maps to class names in data.yaml)
- `x_center, y_center`: Center point of bounding box
- `width, height`: Width and height of bounding box

**Example** (`train/labels/image_001.txt`):

```text
0 0.512 0.487 0.312 0.234
10 0.723 0.345 0.156 0.189
```

This represents:
- Box 1: Class 0 (Aortic enlargement), center at (0.512, 0.487), size 0.312×0.234
- Box 2: Class 10 (Pleural effusion), center at (0.723, 0.345), size 0.156×0.189

**Images without annotations**: Images with no `.txt` file or an empty `.txt` file should be labeled as "Normal" (Bình thường) during training.

---

## Class Mapping

The dataset uses English class names. For the Vietnamese web application, use this mapping:

| Class ID | English Name | Vietnamese Name |
|----------|--------------|-----------------|
| 0 | Aortic enlargement | Phình động mạch chủ |
| 1 | Atelectasis | Xẹp phổi |
| 2 | Calcification | Vôi hóa |
| 3 | Cardiomegaly | Tim to |
| 4 | Consolidation | Đông đặc phổi |
| 5 | ILD | Tổn thương phổi kẽ |
| 6 | Infiltration | Vùng thâm nhiễm |
| 7 | Lung Opacity | Mờ phổi |
| 8 | Nodule-Mass | Nốt - Khối bất thường |
| 9 | Other lesion | Tổn thương khác |
| 10 | Pleural effusion | Tràn dịch màng phổi |
| 11 | Pleural thickening | Dày màng phổi |
| 12 | Pneumothorax | Tràn khí màng phổi |
| 13 | Pulmonary fibrosis | Xơ phổi |

**Additional class for normal images**: Add a 15th class "Normal" / "Bình thường" for images without any annotations.

---

## Integration with Training Pipeline

### Step 1: Download Dataset

Use the Roboflow code snippet at the beginning of your training notebook.

### Step 2: Load Data Configuration

```python
import yaml

# Load data.yaml
with open('./Chest-Xray-Symptom-Detection-3/data.yaml', 'r') as f:
    data_config = yaml.safe_load(f)

print(f"Number of classes: {data_config['nc']}")
print(f"Class names: {data_config['names']}")
```

### Step 3: Add Vietnamese Mapping

```python
# Load Vietnamese class mapping
import json

with open('../configs/class_mapping.json', 'r', encoding='utf-8') as f:
    class_mapping_vi = json.load(f)

# Map class IDs to Vietnamese names
class_names_vi = [class_mapping_vi.get(name, name) for name in data_config['names']]
print(f"Vietnamese names: {class_names_vi}")
```

### Step 4: Handle Normal Images

```python
import os

def check_normal_images(split='train'):
    """Count images without annotations (normal images)"""
    images_dir = f'./Chest-Xray-Symptom-Detection-3/{split}/images'
    labels_dir = f'./Chest-Xray-Symptom-Detection-3/{split}/labels'
    
    normal_count = 0
    for img_file in os.listdir(images_dir):
        label_file = os.path.splitext(img_file)[0] + '.txt'
        label_path = os.path.join(labels_dir, label_file)
        
        # Check if label file exists and is non-empty
        if not os.path.exists(label_path) or os.path.getsize(label_path) == 0:
            normal_count += 1
    
    print(f"Normal images in {split}: {normal_count}")
    return normal_count

# Check all splits
normal_train = check_normal_images('train')
normal_val = check_normal_images('valid')
normal_test = check_normal_images('test')
```

### Step 5: Train YOLOv11s

```python
from ultralytics import YOLO

# Load pretrained YOLOv11s model
model = YOLO('yolov11s.pt')

# Train on the downloaded dataset
results = model.train(
    data='./Chest-Xray-Symptom-Detection-3/data.yaml',
    epochs=50,
    imgsz=640,
    batch=16,
    name='chest_xray_yolov11s',
    project='runs/detect',
    # Add augmentation parameters here if needed
)
```

---

## API Key Security

⚠️ **Important**: The API key `wQ9S049DhK8xjIhNy6zv` is currently hardcoded for development purposes.

**Best Practices**:
1. Store the API key in environment variables:
   ```python
   import os
   api_key = os.getenv('ROBOFLOW_API_KEY', 'wQ9S049DhK8xjIhNy6zv')
   rf = Roboflow(api_key=api_key)
   ```

2. Use a `.env` file:
   ```bash
   # .env
   ROBOFLOW_API_KEY=wQ9S049DhK8xjIhNy6zv
   ```

3. Add `.env` to `.gitignore` to prevent committing API keys to version control

---

## Notes

- **Internet connectivity required**: Dataset download requires active internet connection
- **Download size**: Check Roboflow project page for dataset size information
- **Download location**: Dataset downloads to `./Chest-Xray-Symptom-Detection-3/` by default
- **Caching**: Roboflow caches downloaded datasets to avoid re-downloading
- **Dataset version**: Currently using version 3 - update version number if newer versions become available

---

## References

- Roboflow Project: <https://universe.roboflow.com/vinbigdataxrayproject/chest-xray-symptom-detection>
- Roboflow Python SDK: <https://docs.roboflow.com/python>
- YOLOv11 Documentation: <https://docs.ultralytics.com/>
