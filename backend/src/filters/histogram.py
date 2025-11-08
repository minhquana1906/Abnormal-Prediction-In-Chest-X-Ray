"""Histogram equalization filter - custom implementation using NumPy primitives."""

import numpy as np
from loguru import logger
import time


def apply_histogram_equalization(image: np.ndarray) -> np.ndarray:
    """
    Apply histogram equalization to enhance image contrast.
    
    Steps:
    1. Calculate histogram of pixel intensities
    2. Compute cumulative distribution function (CDF)
    3. Normalize CDF to 0-255 range
    4. Map original intensities to equalized values
    
    Args:
        image: Input grayscale image as numpy array (H, W) with values 0-255
        
    Returns:
        Contrast-enhanced image as numpy array (H, W) with values 0-255
    """
    start_time = time.time()
    
    # Log input
    logger.info(f"Histogram equalization - Input shape: {image.shape}, dtype: {image.dtype}")
    
    # Ensure image is uint8
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    
    # Flatten image to 1D array
    flat_image = image.flatten()
    
    # Step 1: Calculate histogram (256 bins for 0-255)
    histogram = np.zeros(256, dtype=np.int64)
    for pixel_value in flat_image:
        histogram[pixel_value] += 1
    
    logger.info(f"Histogram - Min value: {np.min(image)}, Max value: {np.max(image)}, "
                f"Total pixels: {flat_image.size}")
    
    # Step 2: Compute cumulative distribution function (CDF)
    cdf = np.zeros(256, dtype=np.int64)
    cdf[0] = histogram[0]
    for i in range(1, 256):
        cdf[i] = cdf[i - 1] + histogram[i]
    
    # Step 3: Normalize CDF to 0-255 range
    # Formula: cdf_normalized = ((cdf - cdf_min) / (total_pixels - cdf_min)) * 255
    cdf_min = cdf[cdf > 0].min()  # First non-zero value
    total_pixels = flat_image.size
    
    # Avoid division by zero
    if total_pixels - cdf_min == 0:
        logger.warning("CDF normalization: denominator is zero, returning original image")
        return image
    
    cdf_normalized = ((cdf - cdf_min) / (total_pixels - cdf_min) * 255).astype(np.uint8)
    
    # Step 4: Map original pixel values to equalized values
    result = cdf_normalized[image]
    
    elapsed_time = time.time() - start_time
    logger.info(f"Histogram equalization - Output shape: {result.shape}, "
                f"Processing time: {elapsed_time:.4f}s")
    
    return result
