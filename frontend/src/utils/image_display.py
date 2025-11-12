import streamlit as st
from PIL import Image
import numpy as np
import base64
from io import BytesIO
from typing import Optional, Union


def display_xray_image(
    image: Union[Image.Image, np.ndarray],
    caption: str = "",
    width: str = "content",
    max_width: int = 600,
    enable_fullscreen: bool = False,
) -> None:

    # Convert numpy array to PIL if needed
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    # Apply custom CSS for centered image with fixed size
    st.markdown(
        f"""
        <style>
        .stImage {{
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }}
        .stImage img {{
            max-width: {max_width}px !important;
            max-height: {max_width}px !important;
            width: auto !important;
            height: auto !important;
            display: block !important;
            margin-left: auto !important;
            margin-right: auto !important;
            object-fit: contain !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Display image
    st.image(image, caption=caption, width="content")

    # Add fullscreen button
    if enable_fullscreen:
        expander_key = f"fullscreen_{hash(caption)}"
        with st.expander("🔍 Xem ảnh toàn màn hình", expanded=False):
            st.markdown(
                """
                <style>
                .fullscreen-image {{
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                }}
                .fullscreen-image img {{
                    max-width: 100% !important;
                    max-height: 90vh !important;
                    width: auto !important;
                    height: auto !important;
                    display: block !important;
                    margin-left: auto !important;
                    margin-right: auto !important;
                    object-fit: contain !important;
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )
            # Display full-size image
            st.markdown('<div class="fullscreen-image">', unsafe_allow_html=True)
            st.image(image, width="stretch")
            st.markdown("</div>", unsafe_allow_html=True)
            # Download button in fullscreen view
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            st.download_button(
                label="📥 Tải xuống ảnh",
                data=img_bytes,
                file_name=f"xray_image.png",
                mime="image/png",
                width="stretch",
            )


def display_xray_comparison(
    image1: Union[Image.Image, np.ndarray],
    image2: Union[Image.Image, np.ndarray],
    caption1: str = "Ảnh gốc",
    caption2: str = "Ảnh đã xử lý",
    max_width: int = 500,
) -> None:

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
    if isinstance(image, np.ndarray):
        if len(image.shape) == 2:
            height, width = image.shape
        else:
            height, width = image.shape[:2]
        return (width, height)
    else:
        return image.size


def format_image_info(image: Union[Image.Image, np.ndarray]) -> str:
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
