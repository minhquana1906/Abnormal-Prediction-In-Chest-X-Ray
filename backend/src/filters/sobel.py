"""Sobel edge detection filter - custom implementation using NumPy primitives."""

import numpy as np
from loguru import logger
import time


def apply_sobel(image: np.ndarray) -> np.ndarray:
    """
    Apply Sobel edge detection to grayscale image.
    
    Uses 3x3 Sobel kernels to compute gradients in x and y directions,
    then calculates gradient magnitude for edge detection.
    
    Args:
        image: Input grayscale image as numpy array (H, W) with values 0-255
        
    Returns:
        Edge-detected image as numpy array (H, W) with values 0-255
    """
    start_time = time.time()
    
    # Log input
    logger.info(f"Sobel filter - Input shape: {image.shape}, dtype: {image.dtype}")
    
    # Convert to float for computation
    img_float = image.astype(np.float64)
    
    # Define 3x3 Sobel kernels
    sobel_x = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ], dtype=np.float64)
    
    sobel_y = np.array([
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ], dtype=np.float64)
    
    # Apply convolution manually (without scipy or cv2)
    gradient_x = _convolve2d(img_float, sobel_x)
    gradient_y = _convolve2d(img_float, sobel_y)
    
    # Calculate gradient magnitude
    magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
    
    # Normalize to 0-255 range for better visualization
    mag_min = magnitude.min()
    mag_max = magnitude.max()
    
    if mag_max - mag_min > 0:
        magnitude = ((magnitude - mag_min) / (mag_max - mag_min)) * 255
    else:
        magnitude = np.zeros_like(magnitude)
    
    result = magnitude.astype(np.uint8)
    
    elapsed_time = time.time() - start_time
    logger.info(f"Sobel filter - Output shape: {result.shape}, "
                f"Gradient range: [{mag_min:.2f}, {mag_max:.2f}], "
                f"Processing time: {elapsed_time:.4f}s")
    
    return result


def _convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Perform 2D convolution using NumPy vectorized operations.
    
    Optimized version using sliding window views (as_strided) for better performance.
    
    Args:
        image: Input image array (H, W)
        kernel: Convolution kernel (K, K) - must be odd-sized
        
    Returns:
        Convolved image array (H, W)
        
    Raises:
        ValueError: If kernel dimensions are not odd-sized
    """
    # Get dimensions
    img_h, img_w = image.shape
    ker_h, ker_w = kernel.shape
    
    # Validate kernel is odd-sized
    if ker_h % 2 == 0 or ker_w % 2 == 0:
        raise ValueError(f"Kernel must have odd dimensions, got {ker_h}x{ker_w}")
    
    # Calculate padding
    pad_h = ker_h // 2
    pad_w = ker_w // 2
    
    # Pad image with reflection for better edge handling
    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect')
    
    # Flip kernel for convolution (correlation vs convolution)
    kernel_flipped = np.flip(kernel)
    
    # Create sliding window view using as_strided for vectorization
    # This avoids nested loops and is much faster
    from numpy.lib.stride_tricks import as_strided
    
    shape = (img_h, img_w, ker_h, ker_w)
    strides = (padded.strides[0], padded.strides[1], padded.strides[0], padded.strides[1])
    windows = as_strided(padded, shape=shape, strides=strides)
    
    # Vectorized convolution: element-wise multiply and sum over kernel dimensions
    output = np.einsum('ijkl,kl->ij', windows, kernel_flipped)
    
    return output
