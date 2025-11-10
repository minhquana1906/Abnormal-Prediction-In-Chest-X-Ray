import streamlit as st
from PIL import Image
import numpy as np
from typing import Optional, Union


def display_xray_image(
    image: Union[Image.Image, np.ndarray],
    caption: str = "",
    width: str = "content",
    max_width: int = 600,
) -> None:
    # Convert numpy array to PIL if needed
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    # Use custom CSS for image sizing
    if not width == "content":
        # Apply max-width constraint with CSS
        st.markdown(
            f"""
            <style>
            .stImage img {{
                max-width: {max_width}px !important;
                width: 100% !important;
                height: auto !important;
                display: block !important;
                margin-left: auto !important;
                margin-right: auto !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    # Display image
    st.image(image, caption=caption, width=width)


def display_xray_comparison(
    image1: Union[Image.Image, np.ndarray],
    image2: Union[Image.Image, np.ndarray],
    caption1: str = "Ảnh gốc",
    caption2: str = "Ảnh đã xử lý",
    max_width: int = 500,
) -> None:
    """
    Display two X-ray images side by side for comparison.

    Args:
        image1: First image (original)
        image2: Second image (processed)
        caption1: Caption for first image
        caption2: Caption for second image
        max_width: Maximum width per image in pixels

    Example:
        >>> display_xray_comparison(original_img, processed_img)
    """
    col1, col2 = st.columns(2)

    with col1:
        display_xray_image(image1, caption1, max_width=max_width)

    with col2:
        display_xray_image(image2, caption2, max_width=max_width)


def display_xray_grid(
    images: list,
    captions: list,
    columns: int = 3,
    max_width: int = 400,
) -> None:
    """
    Display multiple X-ray images in a grid layout.

    Args:
        images: List of PIL Images or numpy arrays
        captions: List of captions (same length as images)
        columns: Number of columns in grid
        max_width: Maximum width per image in pixels

    Example:
        >>> images = [img1, img2, img3, img4]
        >>> captions = ["Filter 1", "Filter 2", "Filter 3", "Filter 4"]
        >>> display_xray_grid(images, captions, columns=2)
    """
    if len(images) != len(captions):
        st.error("❌ Số lượng ảnh và caption phải bằng nhau")
        return

    # Create grid layout
    rows = (len(images) + columns - 1) // columns

    idx = 0
    for row in range(rows):
        cols = st.columns(columns)
        for col_idx in range(columns):
            if idx < len(images):
                with cols[col_idx]:
                    display_xray_image(images[idx], captions[idx], max_width=max_width)
                idx += 1


def get_image_dimensions(image: Union[Image.Image, np.ndarray]) -> tuple:
    """
    Get image dimensions (width, height).

    Args:
        image: PIL Image or numpy array

    Returns:
        Tuple of (width, height)
    """
    if isinstance(image, np.ndarray):
        if len(image.shape) == 2:
            height, width = image.shape
        else:
            height, width = image.shape[:2]
        return (width, height)
    else:
        return image.size


def format_image_info(image: Union[Image.Image, np.ndarray]) -> str:
    """
    Format image information for display.

    Args:
        image: PIL Image or numpy array

    Returns:
        Formatted string with image dimensions and channels
    """
    width, height = get_image_dimensions(image)

    if isinstance(image, np.ndarray):
        if len(image.shape) == 2:
            channels = 1
            mode = "Grayscale"
        elif image.shape[2] == 3:
            channels = 3
            mode = "RGB"
        elif image.shape[2] == 4:
            channels = 4
            mode = "RGBA"
        else:
            channels = image.shape[2]
            mode = f"{channels} channels"
    else:
        mode = image.mode
        channels = len(image.getbands())

    return f"{width}×{height} px | {mode} ({channels} channel{'s' if channels > 1 else ''})"


__all__ = [
    "display_xray_image",
    "display_xray_comparison",
    "display_xray_grid",
    "get_image_dimensions",
    "format_image_info",
]
