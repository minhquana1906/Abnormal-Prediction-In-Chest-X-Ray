"""
Centralized preprocessing pipeline for chest X-ray images.

This module ensures consistent preprocessing across:
- Training/validation/test datasets
- User-uploaded images in production
- Model inference

All images are processed with the same pipeline to maintain data consistency.
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional

from backend.src.filters.histogram import apply_histogram_equalization
from backend.src.filters.gaussian import apply_gaussian


def preprocess_image(
    image: np.ndarray,
    target_size: Optional[Tuple[int, int]] = None,
    apply_normalization: bool = True,
) -> np.ndarray:
    """
    Standard preprocessing pipeline for chest X-ray images.

    Pipeline steps:
    1. Ensure grayscale (convert if needed)
    2. Histogram equalization (enhance contrast)
    3. Resize to target size (if specified)
    4. Normalize to [0, 1] range (if enabled)

    NOTE: Gaussian blur is REMOVED to avoid over-smoothing.
    Blur will be applied as data augmentation during training only.

    This function MUST be applied to:
    - All training/validation/test images before feeding to model
    - All user-uploaded images in the web application

    Args:
        image: Input image as numpy array (H, W) or (H, W, C)
        target_size: Optional (width, height) for resizing
        apply_normalization: If True, normalize pixel values to [0, 1]

    Returns:
        Preprocessed image as numpy array (H, W) with dtype float32

    Example:
        >>> img = np.array(Image.open('xray.jpg'))
        >>> preprocessed = preprocess_image(img, target_size=(1024, 1024))
    """
    # Step 1: Ensure grayscale
    if len(image.shape) == 3:
        # Convert RGB to grayscale
        image = _rgb_to_grayscale(image)

    # Ensure uint8 for filter operations
    if image.dtype != np.uint8:
        image = _normalize_to_uint8(image)

    # Step 2: Histogram equalization (contrast enhancement)
    # This is critical for chest X-rays to highlight subtle abnormalities
    image = apply_histogram_equalization(image)

    # Step 3: Resize if target size specified
    if target_size is not None:
        image = _resize_image(image, target_size)

    # Step 4: Normalize to [0, 1] range for neural network input
    if apply_normalization:
        image = image.astype(np.float32) / 255.0
    else:
        image = image.astype(np.float32)

    return image


def _rgb_to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convert RGB image to grayscale using luminosity method.

    Formula: Y = 0.299*R + 0.587*G + 0.114*B

    Args:
        image: RGB image array (H, W, 3) or (H, W, 4)

    Returns:
        Grayscale image array (H, W)
    """
    if image.shape[2] == 3:
        return np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
    elif image.shape[2] == 4:  # RGBA
        return np.dot(image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
    else:
        raise ValueError(f"Unexpected number of channels: {image.shape[2]}")


def _normalize_to_uint8(image: np.ndarray) -> np.ndarray:
    """
    Normalize array to uint8 range [0, 255].

    Args:
        image: Image array with any dtype

    Returns:
        Image array with dtype uint8
    """
    img_min = image.min()
    img_max = image.max()

    if img_max - img_min == 0:
        return np.zeros_like(image, dtype=np.uint8)

    normalized = (image - img_min) / (img_max - img_min)
    return (normalized * 255).astype(np.uint8)


def _resize_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Resize image to target size using PIL.

    Args:
        image: Image array (H, W)
        target_size: (width, height) tuple

    Returns:
        Resized image array
    """
    pil_img = Image.fromarray(image)
    pil_img_resized = pil_img.resize(target_size, Image.Resampling.LANCZOS)
    return np.array(pil_img_resized)


def preprocess_for_training(image_path: str) -> np.ndarray:
    """
    Load and preprocess image from file path for training.

    Args:
        image_path: Path to image file

    Returns:
        Preprocessed image array
    """
    img = Image.open(image_path).convert("L")
    img_array = np.array(img)
    return preprocess_image(img_array, apply_normalization=True)


def preprocess_user_upload(image_bytes: bytes) -> np.ndarray:
    """
    Preprocess user-uploaded image from bytes.

    Args:
        image_bytes: Raw image bytes from upload

    Returns:
        Preprocessed image array
    """
    import io

    img = Image.open(io.BytesIO(image_bytes)).convert("L")
    img_array = np.array(img)
    return preprocess_image(img_array, apply_normalization=True)
