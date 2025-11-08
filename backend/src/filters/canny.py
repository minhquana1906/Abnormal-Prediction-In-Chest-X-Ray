"""Canny edge detection filter - custom implementation using NumPy primitives."""

import numpy as np
from loguru import logger
import time


def apply_canny(image: np.ndarray, low_threshold: int = None, high_threshold: int = None, 
                auto_threshold: bool = True) -> np.ndarray:
    """
    Apply Canny edge detection to grayscale image.
    
    Steps:
    1. Gaussian smoothing (sigma=1.4)
    2. Compute gradients using Sobel operator
    3. Non-maximum suppression
    4. Double thresholding (auto or manual)
    5. Edge tracking by hysteresis
    
    Args:
        image: Input grayscale image as numpy array (H, W) with values 0-255
        low_threshold: Low threshold for edge tracking (default None for auto)
        high_threshold: High threshold for strong edges (default None for auto)
        auto_threshold: If True and thresholds are None, compute automatically (default True)
        
    Returns:
        Binary edge map as numpy array (H, W) with values 0 or 255
    """
    start_time = time.time()
    
    # Log input
    logger.info(f"Canny filter - Input shape: {image.shape}, dtype: {image.dtype}, "
                f"auto_threshold={auto_threshold}")
    
    # Step 1: Gaussian smoothing
    smoothed = _gaussian_blur(image, sigma=1.4, kernel_size=5)
    
    # Step 2: Compute gradients using Sobel
    gradient_x, gradient_y, magnitude, direction = _compute_gradients(smoothed)
    
    # Step 3: Non-maximum suppression
    suppressed = _non_maximum_suppression(magnitude, direction)
    
    # Step 4: Determine thresholds (auto or manual)
    if auto_threshold and (low_threshold is None or high_threshold is None):
        low_threshold, high_threshold = _auto_threshold(suppressed)
        logger.info(f"Canny - Auto-computed thresholds: low={low_threshold}, high={high_threshold}")
    else:
        # Use manual thresholds or defaults
        low_threshold = low_threshold if low_threshold is not None else 100
        high_threshold = high_threshold if high_threshold is not None else 200
        logger.info(f"Canny - Manual thresholds: low={low_threshold}, high={high_threshold}")
    
    # Step 5: Double thresholding
    strong_edges, weak_edges = _double_threshold(suppressed, low_threshold, high_threshold)
    
    # Step 6: Edge tracking by hysteresis
    result = _edge_tracking(strong_edges, weak_edges)
    
    elapsed_time = time.time() - start_time
    edge_pixels = np.count_nonzero(result)
    total_pixels = result.size
    edge_percentage = (edge_pixels / total_pixels) * 100
    
    logger.info(f"Canny filter - Output shape: {result.shape}, "
                f"Edge pixels: {edge_pixels}/{total_pixels} ({edge_percentage:.2f}%), "
                f"Processing time: {elapsed_time:.4f}s")
    
    return result


def _gaussian_blur(image: np.ndarray, sigma: float = 1.4, kernel_size: int = 5) -> np.ndarray:
    """Apply Gaussian blur using custom kernel."""
    # Generate Gaussian kernel
    kernel = _gaussian_kernel(kernel_size, sigma)
    
    # Apply convolution
    return _convolve2d(image.astype(np.float64), kernel)


def _gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    """Generate 2D Gaussian kernel."""
    center = size // 2
    kernel = np.zeros((size, size), dtype=np.float64)
    
    for i in range(size):
        for j in range(size):
            x = i - center
            y = j - center
            kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
    
    # Normalize
    kernel /= kernel.sum()
    return kernel


def _compute_gradients(image: np.ndarray) -> tuple:
    """Compute gradients using Sobel operator."""
    # Sobel kernels
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)
    
    # Compute gradients
    gradient_x = _convolve2d(image, sobel_x)
    gradient_y = _convolve2d(image, sobel_y)
    
    # Magnitude and direction
    magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
    direction = np.arctan2(gradient_y, gradient_x)  # in radians
    
    return gradient_x, gradient_y, magnitude, direction


def _non_maximum_suppression(magnitude: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """Suppress non-maximum pixels in gradient direction."""
    h, w = magnitude.shape
    suppressed = np.zeros_like(magnitude)
    
    # Convert angle to 0-180 degrees
    angle = np.degrees(direction) % 180
    
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            q = 255
            r = 255
            
            # Angle 0° (horizontal)
            if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                q = magnitude[i, j + 1]
                r = magnitude[i, j - 1]
            # Angle 45° (diagonal)
            elif 22.5 <= angle[i, j] < 67.5:
                q = magnitude[i + 1, j - 1]
                r = magnitude[i - 1, j + 1]
            # Angle 90° (vertical)
            elif 67.5 <= angle[i, j] < 112.5:
                q = magnitude[i + 1, j]
                r = magnitude[i - 1, j]
            # Angle 135° (diagonal)
            elif 112.5 <= angle[i, j] < 157.5:
                q = magnitude[i - 1, j - 1]
                r = magnitude[i + 1, j + 1]
            
            # Keep only if local maximum
            if magnitude[i, j] >= q and magnitude[i, j] >= r:
                suppressed[i, j] = magnitude[i, j]
    
    return suppressed


def _double_threshold(image: np.ndarray, low: int, high: int) -> tuple:
    """Apply double thresholding to classify edges."""
    strong_edges = (image >= high).astype(np.uint8) * 255
    weak_edges = ((image >= low) & (image < high)).astype(np.uint8) * 255
    
    return strong_edges, weak_edges


def _auto_threshold(magnitude: np.ndarray, low_percentile: float = 50, 
                    high_percentile: float = 85) -> tuple:
    """
    Automatically compute Canny thresholds based on gradient magnitude distribution.
    
    Uses percentile-based approach to adapt to different image contrasts.
    This is particularly useful for medical X-ray images which can have
    varying brightness and contrast levels.
    
    Args:
        magnitude: Gradient magnitude array after non-maximum suppression
        low_percentile: Percentile for low threshold (default 50 = median)
        high_percentile: Percentile for high threshold (default 85)
        
    Returns:
        Tuple of (low_threshold, high_threshold) as integers
    """
    # Get non-zero gradient values (ignore background)
    non_zero_magnitudes = magnitude[magnitude > 0]
    
    # Handle edge case: no gradients found
    if len(non_zero_magnitudes) == 0:
        logger.warning("Auto-threshold: No gradients found, using defaults (100, 200)")
        return 100, 200
    
    # Compute thresholds based on percentiles
    low_threshold = np.percentile(non_zero_magnitudes, low_percentile)
    high_threshold = np.percentile(non_zero_magnitudes, high_percentile)
    
    # Ensure high > low
    if high_threshold <= low_threshold:
        high_threshold = low_threshold * 2
        logger.warning(f"Auto-threshold: high <= low, adjusted high to {high_threshold}")
    
    # Convert to integers
    low_threshold = int(low_threshold)
    high_threshold = int(high_threshold)
    
    # Log statistics
    logger.debug(f"Auto-threshold - Gradient stats: "
                f"min={non_zero_magnitudes.min():.2f}, "
                f"max={non_zero_magnitudes.max():.2f}, "
                f"median={np.median(non_zero_magnitudes):.2f}, "
                f"p{low_percentile}={low_threshold}, "
                f"p{high_percentile}={high_threshold}")
    
    return low_threshold, high_threshold


def _edge_tracking(strong: np.ndarray, weak: np.ndarray) -> np.ndarray:
    """Track edges by hysteresis - connect weak edges to strong edges."""
    h, w = strong.shape
    result = strong.copy()
    
    # 8-connectivity neighbors
    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    # Iteratively connect weak edges to strong edges
    changed = True
    iterations = 0
    max_iterations = 10  # Prevent infinite loops
    
    while changed and iterations < max_iterations:
        changed = False
        iterations += 1
        
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                # If weak edge
                if weak[i, j] == 255 and result[i, j] == 0:
                    # Check if any neighbor is strong
                    for di, dj in neighbors:
                        if result[i + di, j + dj] == 255:
                            result[i, j] = 255
                            changed = True
                            break
    
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
    from numpy.lib.stride_tricks import as_strided
    
    shape = (img_h, img_w, ker_h, ker_w)
    strides = (padded.strides[0], padded.strides[1], padded.strides[0], padded.strides[1])
    windows = as_strided(padded, shape=shape, strides=strides)
    
    # Vectorized convolution: element-wise multiply and sum over kernel dimensions
    output = np.einsum('ijkl,kl->ij', windows, kernel_flipped)
    
    return output
