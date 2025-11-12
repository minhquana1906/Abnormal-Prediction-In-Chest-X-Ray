import io
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

    width, height = image.size

    if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
        raise ValueError(f"{ERROR_IMAGE_TOO_SMALL} (Got: {width}x{height})")

    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        raise ValueError(f"{ERROR_IMAGE_TOO_LARGE} (Got: {width}x{height})")


def pil_to_numpy(image: Image.Image, grayscale: bool = True) -> np.ndarray:

    if grayscale and image.mode != "L":
        image = image.convert("L")
    elif not grayscale and image.mode != "RGB":
        image = image.convert("RGB")

    return np.array(image)


def numpy_to_pil(array: np.ndarray) -> Image.Image:

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

    array_min = array.min()
    array_max = array.max()

    if array_max - array_min == 0:
        # Avoid division by zero
        return np.zeros_like(array, dtype=np.uint8)

    normalized = (array - array_min) / (array_max - array_min)

    # Scale to 0-255 and convert to uint8
    return (normalized * 255).astype(np.uint8)


def pil_to_base64(image: Image.Image, format: str = "PNG") -> str:

    import base64

    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def numpy_to_base64(array: np.ndarray, format: str = "PNG") -> str:

    image = numpy_to_pil(array)
    return pil_to_base64(image, format)


def get_image_info(image: Image.Image) -> dict:

    width, height = image.size

    return {
        "width": width,
        "height": height,
        "format": image.format,
        "mode": image.mode,
        "size_pixels": width * height,
    }
