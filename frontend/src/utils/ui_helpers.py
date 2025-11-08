"""
UI helper functions for Vietnamese message formatting and display utilities.

This module provides reusable functions for consistent UI presentation
in the Streamlit frontend.
"""

import streamlit as st
from typing import List, Dict, Any
import base64
from PIL import Image
import io


def show_loading_spinner(message: str = "Đang xử lý..."):
    """
    Show a loading spinner with Vietnamese message.

    Args:
        message: Loading message to display

    Returns:
        Streamlit spinner context manager
    """
    return st.spinner(message)


def show_success_message(title: str, message: str = "") -> None:
    """
    Display a success message in Vietnamese.

    Args:
        title: Success title
        message: Additional message details
    """
    if message:
        st.success(f"✅ **{title}**\n\n{message}")
    else:
        st.success(f"✅ {title}")


def show_error_message(title: str, message: str = "", show_retry: bool = True) -> None:
    """
    Display an error message in Vietnamese.

    Args:
        title: Error title
        message: Additional error details
        show_retry: Whether to show retry suggestion
    """
    error_text = f"❌ **{title}**\n\n{message}"

    if show_retry:
        error_text += "\n\n**Vui lòng thử lại hoặc liên hệ hỗ trợ.**"

    st.error(error_text)


def show_warning_message(title: str, message: str = "") -> None:
    """
    Display a warning message in Vietnamese.

    Args:
        title: Warning title
        message: Additional warning details
    """
    if message:
        st.warning(f"⚠️ **{title}**\n\n{message}")
    else:
        st.warning(f"⚠️ {title}")


def show_info_message(title: str, message: str = "") -> None:
    """
    Display an info message in Vietnamese.

    Args:
        title: Info title
        message: Additional info details
    """
    if message:
        st.info(f"ℹ️ **{title}**\n\n{message}")
    else:
        st.info(f"ℹ️ {title}")


def format_processing_time(time_ms: float) -> str:
    """
    Format processing time in Vietnamese.

    Args:
        time_ms: Time in milliseconds

    Returns:
        Formatted time string
    """
    if time_ms < 1000:
        return f"{time_ms:.0f}ms"
    else:
        return f"{time_ms / 1000:.2f}s"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in Vietnamese.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f}MB"


def create_download_button(
    data: bytes,
    filename: str,
    button_text: str = "📥 Tải xuống",
    mime_type: str = "image/png",
    key: str = None,
) -> None:
    """
    Create a download button for image data.

    Args:
        data: File data as bytes
        filename: Download filename
        button_text: Button label in Vietnamese
        mime_type: MIME type of the file
        key: Unique key for the button
    """
    st.download_button(
        label=button_text, data=data, file_name=filename, mime=mime_type, key=key
    )


def display_image_comparison(
    image1: Image.Image,
    image2: Image.Image,
    caption1: str = "Ảnh gốc",
    caption2: str = "Ảnh đã xử lý",
) -> None:
    """
    Display two images side by side for comparison.

    Args:
        image1: First image (original)
        image2: Second image (processed)
        caption1: Caption for first image
        caption2: Caption for second image
    """
    col1, col2 = st.columns(2)

    with col1:
        st.image(image1, caption=caption1, use_column_width=True)

    with col2:
        st.image(image2, caption=caption2, use_column_width=True)


def display_image_grid(
    images: List[Image.Image], captions: List[str], columns: int = 2
) -> None:
    """
    Display multiple images in a grid layout.

    Args:
        images: List of PIL images
        captions: List of captions (Vietnamese)
        columns: Number of columns in grid
    """
    rows = (len(images) + columns - 1) // columns

    for row in range(rows):
        cols = st.columns(columns)
        for col_idx in range(columns):
            img_idx = row * columns + col_idx
            if img_idx < len(images):
                with cols[col_idx]:
                    st.image(
                        images[img_idx],
                        caption=captions[img_idx],
                        use_column_width=True,
                    )


def base64_to_image(base64_string: str) -> Image.Image:
    """
    Convert base64 string to PIL Image.

    Args:
        base64_string: Base64 encoded image string

    Returns:
        PIL Image object
    """
    image_bytes = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_bytes))


def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """
    Convert PIL Image to bytes.

    Args:
        image: PIL Image object
        format: Output format (PNG, JPEG)

    Returns:
        Image as bytes
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()


def display_metrics(metrics: Dict[str, Any], columns: int = 3) -> None:
    """
    Display metrics in columns.

    Args:
        metrics: Dictionary of metric_name -> value
        columns: Number of columns for layout
    """
    cols = st.columns(columns)

    for idx, (label, value) in enumerate(metrics.items()):
        with cols[idx % columns]:
            st.metric(label=label, value=value)


def create_expander(title: str, expanded: bool = False):
    """
    Create an expander with Vietnamese title.

    Args:
        title: Expander title
        expanded: Whether expanded by default

    Returns:
        Streamlit expander context manager
    """
    return st.expander(title, expanded=expanded)


def show_backend_status(is_healthy: bool) -> None:
    """
    Display backend server connection status.

    Args:
        is_healthy: Whether backend is healthy
    """
    if is_healthy:
        st.success("✅ Kết nối máy chủ backend thành công")
    else:
        st.error(
            "❌ **Không thể kết nối tới máy chủ backend**\n\n"
            "Vui lòng đảm bảo máy chủ backend đang chạy trên port 8000.\n\n"
            "**Khởi động backend:**\n"
            "```bash\n"
            "cd backend\n"
            "uvicorn src.api.main:app --reload --port 8000\n"
            "```"
        )


def format_confidence_percentage(confidence: float) -> str:
    """
    Format confidence score as percentage.

    Args:
        confidence: Confidence value (0.0 to 1.0)

    Returns:
        Formatted percentage string
    """
    return f"{confidence * 100:.1f}%"


def get_confidence_color(confidence: float) -> str:
    """
    Get color based on confidence level.

    Args:
        confidence: Confidence value (0.0 to 1.0)

    Returns:
        Color name (green, orange, red)
    """
    if confidence >= 0.7:
        return "green"
    elif confidence >= 0.4:
        return "orange"
    else:
        return "red"


def display_progress_bar(progress: float, text: str = "") -> None:
    """
    Display a progress bar with optional text.

    Args:
        progress: Progress value (0.0 to 1.0)
        text: Progress text in Vietnamese
    """
    if text:
        st.progress(progress, text=text)
    else:
        st.progress(progress)


def create_tabs(tab_names: List[str]):
    """
    Create tabs with Vietnamese names.

    Args:
        tab_names: List of tab names

    Returns:
        Tuple of tab objects
    """
    return st.tabs(tab_names)


def show_json_data(data: Dict[str, Any], title: str = "Dữ liệu JSON") -> None:
    """
    Display JSON data in an expander for debugging.

    Args:
        data: Dictionary to display
        title: Expander title
    """
    with st.expander(title):
        st.json(data)
