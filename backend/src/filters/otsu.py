import numpy as np
from loguru import logger
import time


def apply_otsu(image: np.ndarray) -> np.ndarray:
    """
    Apply Otsu's thresholding method for automatic binary segmentation.

    Otsu's method finds the optimal threshold by maximizing the inter-class
    variance (or equivalently, minimizing intra-class variance).

    Steps:
    1. Calculate histogram of pixel intensities
    2. For each possible threshold (0-255):
        - Compute inter-class variance
    3. Select threshold with maximum inter-class variance
    4. Apply binary thresholding

    Args:
        image: Input grayscale image as numpy array (H, W) with values 0-255

    Returns:
        Binary segmented image as numpy array (H, W) with values 0 or 255
    """
    start_time = time.time()

    # Log input
    logger.info(f"Otsu thresholding - Input shape: {image.shape}, dtype: {image.dtype}")

    # Ensure image is uint8
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)

    # Step 1: Calculate histogram
    histogram = np.zeros(256, dtype=np.int64)
    flat_image = image.flatten()

    for pixel_value in flat_image:
        histogram[pixel_value] += 1

    # Total number of pixels
    total_pixels = flat_image.size

    # Normalize histogram to get probabilities
    prob = histogram / total_pixels

    # Step 2: Find optimal threshold by maximizing inter-class variance
    optimal_threshold = 0
    max_variance = 0.0

    # Cumulative sums and means
    cumsum_0 = 0.0  # Cumulative sum for background class
    cumsum_1 = np.sum(np.arange(256) * prob)  # Initial cumulative sum for foreground

    weight_0 = 0.0  # Weight (probability) of background class
    weight_1 = 1.0  # Weight (probability) of foreground class

    for threshold in range(256):
        # Update weights
        weight_0 += prob[threshold]
        weight_1 -= prob[threshold]

        # Avoid division by zero
        if weight_0 == 0 or weight_1 == 0:
            continue

        # Update cumulative sums
        cumsum_0 += threshold * prob[threshold]
        cumsum_1 -= threshold * prob[threshold]

        # Compute means
        mean_0 = cumsum_0 / weight_0
        mean_1 = cumsum_1 / weight_1

        # Compute inter-class variance
        # Variance = weight_0 * weight_1 * (mean_0 - mean_1)^2
        inter_class_variance = weight_0 * weight_1 * (mean_0 - mean_1) ** 2

        # Update optimal threshold
        if inter_class_variance > max_variance:
            max_variance = inter_class_variance
            optimal_threshold = threshold

    logger.info(
        f"Otsu - Optimal threshold: {optimal_threshold}, "
        f"Inter-class variance: {max_variance:.4f}"
    )

    # Step 3: Apply binary thresholding
    result = np.where(image > optimal_threshold, 255, 0).astype(np.uint8)

    elapsed_time = time.time() - start_time
    logger.info(
        f"Otsu thresholding - Output shape: {result.shape}, "
        f"Processing time: {elapsed_time:.4f}s"
    )

    return result
