import numpy as np
from loguru import logger
import time


def apply_dct(image: np.ndarray) -> np.ndarray:
    """
    Apply 2D Discrete Cosine Transform and visualize coefficients.

    DCT is widely used in image compression (JPEG). This implementation
    uses scipy.fftpack-based DCT or a custom NumPy implementation.

    Steps:
    1. Apply 2D DCT to the image
    2. Compute absolute values of coefficients
    3. Apply log transform for visualization
    4. Normalize to 0-255 range

    Args:
        image: Input grayscale image as numpy array (H, W) with values 0-255

    Returns:
        DCT coefficient visualization as numpy array (H, W) with values 0-255
    """
    start_time = time.time()

    # Log input
    logger.info(f"DCT - Input shape: {image.shape}, dtype: {image.dtype}")

    # Convert to float for DCT computation
    img_float = image.astype(np.float64)

    # Step 1: Apply 2D DCT using custom implementation
    dct_coeffs = _dct2d(img_float)

    # Step 2: Compute absolute values
    dct_abs = np.abs(dct_coeffs)

    logger.info(f"DCT - Coefficient range: [{dct_abs.min():.2f}, {dct_abs.max():.2f}]")

    # Step 3: Apply log transform for better visualization
    dct_log = np.log1p(dct_abs)

    # Step 4: Normalize to 0-255 range
    dct_min = dct_log.min()
    dct_max = dct_log.max()

    if dct_max - dct_min > 0:
        normalized = (dct_log - dct_min) / (dct_max - dct_min) * 255
    else:
        logger.warning("DCT: uniform coefficients, returning zeros")
        normalized = np.zeros_like(dct_log)

    result = normalized.astype(np.uint8)

    elapsed_time = time.time() - start_time
    logger.info(
        f"DCT - Output shape: {result.shape}, "
        f"Coefficient range (raw): [{dct_abs.min():.2f}, {dct_abs.max():.2e}], "
        f"After log+normalize: [0, 255], "
        f"Processing time: {elapsed_time:.4f}s"
    )

    return result


def _dct2d(image: np.ndarray) -> np.ndarray:
    """
    Compute 2D Discrete Cosine Transform using NumPy.

    Uses separable property: DCT2D(image) = DCT(DCT(image)^T)^T

    Args:
        image: Input image array (H, W)

    Returns:
        DCT coefficients (H, W)
    """
    # Apply 1D DCT to rows, then to columns
    dct_rows = _dct1d_matrix(image.shape[0]) @ image
    dct_2d = dct_rows @ _dct1d_matrix(image.shape[1]).T

    return dct_2d


def _dct1d_matrix(n: int) -> np.ndarray:
    """
    Generate DCT-II transformation matrix for 1D DCT.

    DCT-II formula:
    X[k] = sum_{n=0}^{N-1} x[n] * cos(pi * k * (2n + 1) / (2N))

    Args:
        n: Size of the transform

    Returns:
        DCT transformation matrix (n, n)
    """
    matrix = np.zeros((n, n), dtype=np.float64)

    for k in range(n):
        for i in range(n):
            if k == 0:
                # DC component normalization
                matrix[k, i] = np.sqrt(1.0 / n)
            else:
                # AC components
                matrix[k, i] = np.sqrt(2.0 / n) * np.cos(
                    np.pi * k * (2 * i + 1) / (2 * n)
                )

    return matrix
