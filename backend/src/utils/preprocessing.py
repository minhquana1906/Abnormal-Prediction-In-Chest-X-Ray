import numpy as np
from PIL import Image

from backend.src.filters.histogram import apply_histogram_equalization


def preprocess_image(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 3:
        image = np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)

    if image.dtype != np.uint8:
        img_min, img_max = image.min(), image.max()
        if img_max > img_min:
            image = ((image - img_min) / (img_max - img_min) * 255).astype(np.uint8)
        else:
            image = np.zeros_like(image, dtype=np.uint8)

    return apply_histogram_equalization(image)
