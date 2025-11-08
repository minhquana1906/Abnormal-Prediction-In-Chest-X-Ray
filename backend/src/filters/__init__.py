"""Filter registry - Central module for managing all image processing filters."""

from typing import Dict, Callable, Any
import numpy as np
from loguru import logger

# Import all filter implementations
from .sobel import apply_sobel
from .canny import apply_canny
from .gaussian import apply_gaussian
from .median import apply_median
from .histogram import apply_histogram_equalization
from .fourier import apply_fourier
from .dct import apply_dct
from .otsu import apply_otsu


# Filter metadata registry
FILTER_REGISTRY: Dict[str, Dict[str, Any]] = {
    "sobel": {
        "name": "Sobel Edge Detection",
        "name_vi": "Phát hiện cạnh Sobel",
        "description": "Detects edges using Sobel operator with 3x3 kernels",
        "description_vi": "Phát hiện cạnh bằng toán tử Sobel với nhân 3x3",
        "function": apply_sobel,
        "parameters": {},  # Fixed parameters, no user input
        "output_type": "grayscale",
    },
    "canny": {
        "name": "Canny Edge Detection",
        "name_vi": "Phát hiện cạnh Canny",
        "description": "Advanced edge detection with non-maximum suppression and hysteresis",
        "description_vi": "Phát hiện cạnh nâng cao với triệt tiêu cực đại và trễ",
        "function": apply_canny,
        "parameters": {
            "low_threshold": None,  # None for auto-threshold
            "high_threshold": None,  # None for auto-threshold
            "auto_threshold": True,  # Enable auto-threshold by default
        },
        "output_type": "binary",
    },
    "gaussian": {
        "name": "Gaussian Blur",
        "name_vi": "Làm mờ Gaussian",
        "description": "Smoothing filter using Gaussian kernel (sigma=1.4)",
        "description_vi": "Bộ lọc làm mịn bằng nhân Gaussian (sigma=1.4)",
        "function": apply_gaussian,
        "parameters": {
            "sigma": 1.4,
            "kernel_size": 5,
        },
        "output_type": "grayscale",
    },
    "median": {
        "name": "Median Filter",
        "name_vi": "Bộ lọc trung vị",
        "description": "Noise reduction using 5x5 median filtering",
        "description_vi": "Giảm nhiễu bằng lọc trung vị 5x5",
        "function": apply_median,
        "parameters": {
            "window_size": 5,
        },
        "output_type": "grayscale",
    },
    "histogram": {
        "name": "Histogram Equalization",
        "name_vi": "Cân bằng Histogram",
        "description": "Contrast enhancement using histogram equalization",
        "description_vi": "Tăng cường độ tương phản bằng cân bằng histogram",
        "function": apply_histogram_equalization,
        "parameters": {},
        "output_type": "grayscale",
    },
    "fourier": {
        "name": "Fourier Transform",
        "name_vi": "Biến đổi Fourier",
        "description": "Frequency domain visualization using 2D FFT",
        "description_vi": "Trực quan hóa miền tần số bằng FFT 2D",
        "function": apply_fourier,
        "parameters": {},
        "output_type": "spectrum",
    },
    "dct": {
        "name": "Discrete Cosine Transform",
        "name_vi": "Biến đổi Cosine rời rạc",
        "description": "DCT coefficient visualization (used in JPEG compression)",
        "description_vi": "Trực quan hóa hệ số DCT (dùng trong nén JPEG)",
        "function": apply_dct,
        "parameters": {},
        "output_type": "spectrum",
    },
    "otsu": {
        "name": "Otsu Thresholding",
        "name_vi": "Ngưỡng Otsu",
        "description": "Automatic binary segmentation using Otsu's method",
        "description_vi": "Phân đoạn nhị phân tự động bằng phương pháp Otsu",
        "function": apply_otsu,
        "parameters": {},
        "output_type": "binary",
    },
}


def get_filter_list() -> list:
    """
    Get list of available filters with metadata.
    
    Returns:
        List of filter dictionaries with name, description, and parameters
    """
    filters = []
    for filter_id, metadata in FILTER_REGISTRY.items():
        filters.append({
            "id": filter_id,
            "name": metadata["name"],
            "name_vi": metadata["name_vi"],
            "description": metadata["description"],
            "description_vi": metadata["description_vi"],
            "parameters": metadata["parameters"],
            "output_type": metadata["output_type"],
        })
    
    logger.info(f"Filter registry - {len(filters)} filters available")
    return filters


def apply_filter(filter_id: str, image: np.ndarray, **kwargs) -> np.ndarray:
    """
    Apply a filter to an image by filter ID.
    
    Args:
        filter_id: Filter identifier (e.g., 'sobel', 'canny')
        image: Input grayscale image as numpy array (H, W) with values 0-255
        **kwargs: Optional parameters to override defaults
        
    Returns:
        Filtered image as numpy array
        
    Raises:
        ValueError: If filter_id is not recognized
    """
    if filter_id not in FILTER_REGISTRY:
        available = ", ".join(FILTER_REGISTRY.keys())
        raise ValueError(f"Unknown filter: {filter_id}. Available: {available}")
    
    metadata = FILTER_REGISTRY[filter_id]
    filter_func = metadata["function"]
    
    # Merge default parameters with user overrides
    params = {**metadata["parameters"], **kwargs}
    
    logger.info(f"Applying filter: {filter_id} ({metadata['name']}) with params: {params}")
    
    # Apply filter
    result = filter_func(image, **params) if params else filter_func(image)
    
    return result


def apply_multiple_filters(filter_ids: list, image: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Apply multiple filters to an image.
    
    Args:
        filter_ids: List of filter identifiers
        image: Input grayscale image as numpy array (H, W) with values 0-255
        
    Returns:
        Dictionary mapping filter_id to filtered image
    """
    results = {}
    
    logger.info(f"Applying {len(filter_ids)} filters: {filter_ids}")
    
    for filter_id in filter_ids:
        try:
            results[filter_id] = apply_filter(filter_id, image)
        except Exception as e:
            logger.error(f"Filter {filter_id} failed: {str(e)}")
            # Continue with other filters even if one fails
            results[filter_id] = None
    
    successful = sum(1 for v in results.values() if v is not None)
    logger.info(f"Applied {successful}/{len(filter_ids)} filters successfully")
    
    return results


__all__ = [
    "FILTER_REGISTRY",
    "get_filter_list",
    "apply_filter",
    "apply_multiple_filters",
    "apply_sobel",
    "apply_canny",
    "apply_gaussian",
    "apply_median",
    "apply_histogram_equalization",
    "apply_fourier",
    "apply_dct",
    "apply_otsu",
]
