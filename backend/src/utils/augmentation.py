"""
Simplified data augmentation for chest X-ray images.

Only Gaussian blur with dynamic kernel selection is applied as augmentation.
This should be used during training time, not for creating new image files.
"""

import numpy as np
import random
from typing import Tuple

from backend.src.filters.gaussian import apply_gaussian


def augment_image(
    img_array: np.ndarray,
    augmentation_probability: float = 0.5,
) -> np.ndarray:
    """
    Apply Gaussian blur augmentation to chest X-ray image.

    CRITICAL: This function applies augmentation ON-THE-FLY during training.
    Do NOT use this to create and save augmented images.

    Augmentation pipeline:
    - Gaussian blur with dynamic kernel selection (50% chance)
      * 70% chance: 3x3 kernel (light blur)
      * 25% chance: 5x5 kernel (medium blur)
      * 5% chance: 7x7 kernel (strong blur)
      * Fixed sigma=0.5 for all kernels

    Args:
        img_array: Input grayscale image as numpy array (H, W)
        augmentation_probability: Probability to apply blur (default 0.5)

    Returns:
        Augmented image as numpy array (H, W)
    """
    # Apply Gaussian blur with dynamic kernel selection (50% chance)
    if random.random() < augmentation_probability:
        img_array = _apply_dynamic_gaussian_blur(img_array)

    return img_array


def _apply_dynamic_gaussian_blur(img_array: np.ndarray) -> np.ndarray:
    """
    Apply Gaussian blur with dynamically selected kernel size.

    Kernel selection strategy:
    - 80% chance: 3x3 kernel (light blur)
    - 20% chance: 5x5 kernel (medium blur)
    - Removed 7x7 kernel for simplicity

    Fixed sigma=0.5 for all kernels to maintain consistency.
    """
    rand = random.random()

    if rand < 0.80:  # 80% chance
        kernel_size = 3
    else:  # 20% chance (0.80–1.00)
        kernel_size = 5

    sigma = 0.5
    return apply_gaussian(img_array, kernel_size=kernel_size, sigma=sigma)


def augment_batch(
    images: np.ndarray,
    augmentation_probability: float = 0.5,
) -> np.ndarray:
    """
    Apply augmentation to a batch of images.

    Args:
        images: Batch of images (N, H, W) or (N, H, W, C)
        augmentation_probability: Probability for augmentation

    Returns:
        Augmented batch of images with same shape
    """
    augmented = []

    for img in images:
        # Handle both (H, W) and (H, W, C) formats
        if len(img.shape) == 3:
            # Convert to grayscale if color
            if img.shape[2] == 3:
                img = np.dot(img[..., :3], [0.299, 0.587, 0.114])
            else:
                img = img[:, :, 0]  # Take first channel

        augmented_img = augment_image(img, augmentation_probability)
        augmented.append(augmented_img)

    return np.array(augmented)


def get_augmentation_summary() -> dict:
    return {
        "gaussian_blur": {
            "probability": 0.5,
            "kernel_distribution": "80% 3x3, 20% 5x5",
            "sigma": 0.5,
            "description": "Dynamic Gaussian blur (fixed sigma=0.5, no 7x7 kernel)",
        },
    }
