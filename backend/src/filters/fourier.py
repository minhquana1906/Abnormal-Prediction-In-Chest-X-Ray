import numpy as np
from loguru import logger
import time


def apply_fourier(image: np.ndarray) -> np.ndarray:
    """
    Apply 2D Fourier Transform and visualize the magnitude spectrum.

    Steps:
    1. Apply 2D FFT using numpy.fft.fft2
    2. Shift zero frequency to center using fftshift
    3. Compute magnitude spectrum
    4. Apply log transform for better visualization
    5. Normalize to 0-255 range

    Args:
        image: Input grayscale image as numpy array (H, W) with values 0-255

    Returns:
        Magnitude spectrum visualization as numpy array (H, W) with values 0-255
    """
    start_time = time.time()

    # Log input
    logger.info(f"Fourier transform - Input shape: {image.shape}, dtype: {image.dtype}")

    # Convert to float for FFT computation
    img_float = image.astype(np.float64)

    # Step 1: Apply 2D FFT
    fft = np.fft.fft2(img_float)

    # Step 2: Shift zero frequency component to center
    fft_shifted = np.fft.fftshift(fft)

    # Step 3: Compute magnitude spectrum
    magnitude = np.abs(fft_shifted)

    logger.info(
        f"Fourier - Magnitude range: [{magnitude.min():.2f}, {magnitude.max():.2f}]"
    )

    # Step 4: Apply log transform for better visualization
    # log(1 + magnitude) to avoid log(0)
    magnitude_log = np.log1p(magnitude)

    # Step 5: Normalize to 0-255 range
    # Avoid division by zero
    mag_min = magnitude_log.min()
    mag_max = magnitude_log.max()

    if mag_max - mag_min > 0:
        normalized = (magnitude_log - mag_min) / (mag_max - mag_min) * 255
    else:
        logger.warning("Fourier transform: uniform magnitude spectrum, returning zeros")
        normalized = np.zeros_like(magnitude_log)

    result = normalized.astype(np.uint8)

    elapsed_time = time.time() - start_time
    logger.info(
        f"Fourier transform - Output shape: {result.shape}, "
        f"Magnitude range (raw): [{magnitude.min():.2f}, {magnitude.max():.2e}], "
        f"After log+normalize: [0, 255], "
        f"Processing time: {elapsed_time:.4f}s"
    )

    return result
