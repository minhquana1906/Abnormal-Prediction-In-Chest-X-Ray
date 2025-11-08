"""
Image processing utilities for in-memory operations.

This module provides functions for loading, validating, converting, and
processing images entirely in memory without saving to disk.
Uses PIL for I/O and NumPy for array operations.
"""

import io
from typing import Tuple, Optional
import numpy as np
from PIL import Image

from backend.src.config.settings import (
    MAX_IMAGE_DIMENSION,
    MIN_IMAGE_DIMENSION,
    ERROR_CORRUPTED_IMAGE,
    ERROR_IMAGE_TOO_SMALL,
    ERROR_IMAGE_TOO_LARGE,
)


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Load an image from bytes into a PIL Image object.

    Args:
        image_bytes: Raw image file bytes

    Returns:
        PIL Image object

    Raises:
        ValueError: If image cannot be opened or is corrupted
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Verify image can be loaded
        image.verify()
        # Reopen after verify (verify closes the file)
        image = Image.open(io.BytesIO(image_bytes))
        return image
    except Exception as e:
        raise ValueError(f"{ERROR_CORRUPTED_IMAGE}: {str(e)}")


def validate_image_dimensions(image: Image.Image) -> None:
    """
    Validate image dimensions are within acceptable range.

    Args:
        image: PIL Image object

    Raises:
        ValueError: If dimensions are too small or too large
    """
    width, height = image.size

    if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
        raise ValueError(f"{ERROR_IMAGE_TOO_SMALL} (Got: {width}x{height})")

    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        raise ValueError(f"{ERROR_IMAGE_TOO_LARGE} (Got: {width}x{height})")


def pil_to_numpy(image: Image.Image, grayscale: bool = True) -> np.ndarray:
    """
    Convert PIL Image to NumPy array.

    Args:
        image: PIL Image object
        grayscale: If True, convert to grayscale (default for X-rays)

    Returns:
        NumPy array with shape (height, width) for grayscale or
        (height, width, channels) for color
    """
    if grayscale and image.mode != "L":
        image = image.convert("L")
    elif not grayscale and image.mode != "RGB":
        image = image.convert("RGB")

    return np.array(image)


def numpy_to_pil(array: np.ndarray) -> Image.Image:
    """
    Convert NumPy array to PIL Image.

    Args:
        array: NumPy array (uint8 or will be converted to uint8)

    Returns:
        PIL Image object
    """
    # Normalize to 0-255 range if needed
    if array.dtype != np.uint8:
        array = normalize_to_uint8(array)

    # Handle different array shapes
    if len(array.shape) == 2:
        # Grayscale image
        return Image.fromarray(array, mode="L")
    elif len(array.shape) == 3:
        # Color image
        return Image.fromarray(array, mode="RGB")
    else:
        raise ValueError(f"Invalid array shape: {array.shape}")


def normalize_to_uint8(array: np.ndarray) -> np.ndarray:
    """
    Normalize array to uint8 range [0, 255].

    Args:
        array: NumPy array with any dtype and range

    Returns:
        NumPy array with dtype uint8
    """
    # Normalize to 0-1 range
    array_min = array.min()
    array_max = array.max()

    if array_max - array_min == 0:
        # Avoid division by zero
        return np.zeros_like(array, dtype=np.uint8)

    normalized = (array - array_min) / (array_max - array_min)

    # Scale to 0-255 and convert to uint8
    return (normalized * 255).astype(np.uint8)


def pil_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    Convert PIL Image to base64 encoded string.

    Args:
        image: PIL Image object
        format: Output format (PNG, JPEG)

    Returns:
        Base64 encoded string
    """
    import base64

    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def numpy_to_base64(array: np.ndarray, format: str = "PNG") -> str:
    """
    Convert NumPy array to base64 encoded string.

    Args:
        array: NumPy array (will be converted to PIL Image)
        format: Output format (PNG, JPEG)

    Returns:
        Base64 encoded string
    """
    image = numpy_to_pil(array)
    return pil_to_base64(image, format)


def base64_to_pil(base64_string: str) -> Image.Image:
    """
    Convert base64 encoded string to PIL Image.

    Args:
        base64_string: Base64 encoded image string

    Returns:
        PIL Image object
    """
    import base64

    image_bytes = base64.b64decode(base64_string)
    return load_image_from_bytes(image_bytes)


def resize_image(image: Image.Image, max_dimension: int) -> Image.Image:
    """
    Resize image maintaining aspect ratio if larger than max_dimension.

    Args:
        image: PIL Image object
        max_dimension: Maximum width or height

    Returns:
        Resized PIL Image object (or original if already smaller)
    """
    width, height = image.size

    if width <= max_dimension and height <= max_dimension:
        return image

    # Calculate scaling factor
    scale = max_dimension / max(width, height)
    new_width = int(width * scale)
    new_height = int(height * scale)

    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def get_image_info(image: Image.Image) -> dict:
    """
    Extract metadata from PIL Image.

    Args:
        image: PIL Image object

    Returns:
        Dictionary with image information
    """
    width, height = image.size

    return {
        "width": width,
        "height": height,
        "format": image.format,
        "mode": image.mode,
        "size_pixels": width * height,
    }


def ensure_grayscale(array: np.ndarray) -> np.ndarray:
    """
    Ensure array is grayscale (2D). If color (3D), convert to grayscale.

    Args:
        array: NumPy array (either 2D or 3D)

    Returns:
        2D NumPy array (grayscale)
    """
    if len(array.shape) == 2:
        return array
    elif len(array.shape) == 3:
        # Convert RGB to grayscale using luminosity method
        # Y = 0.299*R + 0.587*G + 0.114*B
        if array.shape[2] == 3:
            return np.dot(array[..., :3], [0.299, 0.587, 0.114])
        elif array.shape[2] == 4:  # RGBA
            return np.dot(array[..., :3], [0.299, 0.587, 0.114])
        else:
            raise ValueError(f"Unexpected number of channels: {array.shape[2]}")
    else:
        raise ValueError(f"Invalid array shape: {array.shape}")


def pad_array(array: np.ndarray, kernel_size: int) -> np.ndarray:
    """
    Pad array with zeros for convolution operations.

    Args:
        array: NumPy array
        kernel_size: Size of convolution kernel (must be odd)

    Returns:
        Padded NumPy array
    """
    padding = kernel_size // 2
    return np.pad(array, padding, mode="constant", constant_values=0)


def clip_array(
    array: np.ndarray, min_val: float = 0, max_val: float = 255
) -> np.ndarray:
    """
    Clip array values to specified range.

    Args:
        array: NumPy array
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clipped NumPy array
    """
    return np.clip(array, min_val, max_val)
