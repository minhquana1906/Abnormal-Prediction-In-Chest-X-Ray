"""Gaussian blur filter - custom implementation using NumPy primitives."""

import numpy as np
from loguru import logger
import time


def apply_gaussian(image: np.ndarray, sigma: float = 1.4, kernel_size: int = 5) -> np.ndarray:
    """
    Apply Gaussian blur to grayscale image.
    
    Generates a 2D Gaussian kernel and applies convolution for smoothing.
    
    Args:
        image: Input grayscale image as numpy array (H, W) with values 0-255
        sigma: Standard deviation of Gaussian distribution (default 1.4)
        kernel_size: Size of Gaussian kernel (default 5x5)
        
    Returns:
        Blurred image as numpy array (H, W) with values 0-255
    """
    start_time = time.time()
    
    # Log input
    logger.info(f"Gaussian blur filter - Input shape: {image.shape}, dtype: {image.dtype}, "
                f"sigma={sigma}, kernel_size={kernel_size}")
    
    # Convert to float for computation
    img_float = image.astype(np.float64)
    
    # Generate 2D Gaussian kernel
    kernel = _generate_gaussian_kernel(kernel_size, sigma)
    logger.info(f"Gaussian blur - Kernel sum: {kernel.sum():.6f} (should be ~1.0)")
    
    # Apply convolution
    blurred = _convolve2d(img_float, kernel)
    
    # Clip and convert back to uint8
    result = np.clip(blurred, 0, 255).astype(np.uint8)
    
    elapsed_time = time.time() - start_time
    logger.info(f"Gaussian blur filter - Output shape: {result.shape}, Processing time: {elapsed_time:.4f}s")
    
    return result


def _generate_gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    """
    Generate 2D Gaussian kernel.
    
    G(x, y) = (1 / (2 * pi * sigma^2)) * exp(-(x^2 + y^2) / (2 * sigma^2))
    
    Args:
        size: Kernel size (must be odd)
        sigma: Standard deviation
        
    Returns:
        Normalized Gaussian kernel (size, size)
    """
    # Ensure odd size
    if size % 2 == 0:
        size += 1
    
    center = size // 2
    kernel = np.zeros((size, size), dtype=np.float64)
    
    # Generate kernel values
    for i in range(size):
        for j in range(size):
            x = i - center
            y = j - center
            # Gaussian formula
            kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
    
    # Normalize so sum equals 1
    kernel /= kernel.sum()
    
    return kernel


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
    from numpy.lib.stride_tricks import as_strided
    
    shape = (img_h, img_w, ker_h, ker_w)
    strides = (padded.strides[0], padded.strides[1], padded.strides[0], padded.strides[1])
    windows = as_strided(padded, shape=shape, strides=strides)
    
    # Vectorized convolution: element-wise multiply and sum over kernel dimensions
    output = np.einsum('ijkl,kl->ij', windows, kernel_flipped)
    
    return output
