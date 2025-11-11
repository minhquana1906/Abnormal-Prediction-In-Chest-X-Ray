import numpy as np
import random
from typing import Tuple

from backend.src.filters.gaussian import apply_gaussian


def augment_image(
    img_array: np.ndarray,
    augmentation_probability: float = 0.5,
) -> np.ndarray:

    if random.random() < augmentation_probability:
        img_array = _apply_dynamic_gaussian_blur(img_array)

    return img_array


def _apply_dynamic_gaussian_blur(img_array: np.ndarray) -> np.ndarray:

    rand = random.random()

    if rand < 0.80:  # 80% chance
        kernel_size = 3
    else:  # 20% chance (0.80–1.00)
        kernel_size = 5

    sigma = 0.5
    return apply_gaussian(img_array, kernel_size=kernel_size, sigma=sigma)
