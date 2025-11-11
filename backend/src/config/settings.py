from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Model paths
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_WEIGHTS_PATH = MODEL_DIR / "best.pt"

# Configuration file paths
CONFIG_DIR = PROJECT_ROOT / "configs"
CLASS_MAPPING_PATH = CONFIG_DIR / "class_mapping_2classes.json"
HEALTH_INFO_PATH = CONFIG_DIR / "health_info_vi.json"

# File upload constraints
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 10MB = 10,485,760 bytes
ALLOWED_IMAGE_FORMATS = ["PNG", "JPEG", "JPG"]
ALLOWED_MIME_TYPES = ["image/png", "image/jpeg", "image/jpg"]

# Image processing constraints
MAX_IMAGE_DIMENSION = 2048  # Maximum width or height in pixels
MIN_IMAGE_DIMENSION = 1  # Minimum width or height in pixels

# Performance targets (in seconds)
PERFORMANCE_TARGET_SINGLE_FILTER = 5.0  # Single filter processing target
PERFORMANCE_TARGET_MULTIPLE_FILTERS = 15.0  # Multiple filters processing target
PERFORMANCE_TARGET_DETECTION = 10.0  # Disease detection inference target

# YOLO model configuration
YOLO_CONFIDENCE_THRESHOLD = 0.4  # Minimum confidence for detection display
YOLO_CONFIDENCE_HIGH = 0.7  # High confidence threshold (solid box)
YOLO_CONFIDENCE_MEDIUM = 0.4  # Medium confidence threshold (dashed box)
YOLO_INPUT_SIZE = 640  # YOLO model input size

# Confidence tier display rules
CONFIDENCE_TIER_HIGH = "high"  # >70% - solid bounding box
CONFIDENCE_TIER_MEDIUM = "medium"  # 40-70% - dashed bounding box
CONFIDENCE_TIER_LOW = "low"  # <40% - hidden (filtered out)

# API configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True  # Enable auto-reload for development

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:8501",  # Streamlit default port
    "http://127.0.0.1:8501",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Logging configuration
LOG_DIR = PROJECT_ROOT / "backend" / "logs"
LOG_ROTATION = "10 MB"  # Rotate log files at 10MB
LOG_RETENTION = "7 days"  # Keep logs for 7 days
LOG_LEVEL = "DEBUG"  # Log level for development
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Filter configuration
AVAILABLE_FILTERS = [
    "sobel",
    "canny",
    "gaussian_blur",
    "median_filter",
    "histogram_equalization",
    "fourier_transform",
    "dct",
    "otsu_thresholding",
]

# Filter display names (English)
FILTER_DISPLAY_NAMES = {
    "sobel": "Sobel Edge Detection",
    "canny": "Canny Edge Detection",
    "gaussian_blur": "Gaussian Blur",
    "median_filter": "Median Filter",
    "histogram_equalization": "Histogram Equalization",
    "fourier_transform": "Fourier Transform",
    "dct": "Discrete Cosine Transform (DCT)",
    "otsu_thresholding": "Otsu Thresholding",
}

# Filter descriptions
FILTER_DESCRIPTIONS = {
    "sobel": "Detects edges using Sobel operators (3x3 kernels)",
    "canny": "Multi-stage edge detection with gradient analysis",
    "gaussian_blur": "Smooths image using Gaussian kernel (sigma=1.4)",
    "median_filter": "Reduces noise using median of 5x5 window",
    "histogram_equalization": "Enhances contrast by redistributing intensity values",
    "fourier_transform": "Visualizes frequency domain representation",
    "dct": "Shows DCT coefficients for compression analysis",
    "otsu_thresholding": "Automatic binary segmentation using optimal threshold",
}

# Fixed filter parameters (from research.md - optimized for chest X-rays)
FILTER_PARAMETERS = {
    "sobel": {
        "kernel_size": 3,
    },
    "canny": {
        "low_threshold": 100,
        "high_threshold": 200,
        "sigma": 1.4,
    },
    "gaussian_blur": {
        "sigma": 1.4,
        "kernel_size": 5,
    },
    "median_filter": {
        "kernel_size": 5,
    },
    "histogram_equalization": {},
    "fourier_transform": {},
    "dct": {},
    "otsu_thresholding": {},
}

# Session management
SESSION_TIMEOUT_MINUTES = 30  # Clear in-memory data after 30 minutes of inactivity

ERROR_FILE_TOO_LARGE = f"File size exceeds maximum limit of {MAX_FILE_SIZE_MB}MB"
ERROR_INVALID_FORMAT = (
    f"Invalid file format. Allowed formats: {', '.join(ALLOWED_IMAGE_FORMATS)}"
)
ERROR_CORRUPTED_IMAGE = "Image file is corrupted or cannot be opened"
ERROR_IMAGE_TOO_SMALL = f"Image dimensions too small. Minimum: {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION} pixels"
ERROR_IMAGE_TOO_LARGE = f"Image dimensions too large. Maximum: {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION} pixels"
ERROR_INVALID_IMAGE_ID = "Invalid or expired image ID"
ERROR_FILTER_NOT_FOUND = "Filter not found"
ERROR_MODEL_NOT_LOADED = (
    "Detection model not loaded. Please ensure model weights are available."
)
ERROR_PROCESSING_FAILED = "Image processing failed"
ERROR_DETECTION_FAILED = "Disease detection failed"
