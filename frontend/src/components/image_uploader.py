"""
Reusable image uploader component with Vietnamese error messages.

This module provides a Streamlit file uploader widget configured for
chest X-ray images with validation and error handling.
"""

import streamlit as st
from typing import Optional, Tuple
from PIL import Image
import io

# Constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_TYPES = ["png", "jpg", "jpeg"]


def render_image_uploader(
    key: str = "image_uploader",
) -> Optional[Tuple[bytes, str, Image.Image]]:
    """
    Render an image uploader widget with validation.

    Args:
        key: Unique key for the uploader widget

    Returns:
        Tuple of (image_bytes, filename, PIL_image) if valid upload,
        None if no file or invalid file
    """
    uploaded_file = st.file_uploader(
        label="📁 Chọn ảnh X-quang ngực",
        type=ALLOWED_TYPES,
        key=key,
        help=f"Định dạng hỗ trợ: {', '.join([t.upper() for t in ALLOWED_TYPES])}. Kích thước tối đa: {MAX_FILE_SIZE_MB}MB",
    )

    if uploaded_file is None:
        return None

    # Validate file size
    file_size = uploaded_file.size
    if file_size > MAX_FILE_SIZE_BYTES:
        st.error(
            f"❌ **Lỗi: Kích thước tệp quá lớn**\n\n"
            f"Kích thước tệp: {file_size / (1024 * 1024):.2f}MB\n"
            f"Kích thước tối đa cho phép: {MAX_FILE_SIZE_MB}MB\n\n"
            f"**Giải pháp:** Vui lòng nén hoặc chọn ảnh có kích thước nhỏ hơn."
        )
        return None

    # Read file bytes
    try:
        image_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer
    except Exception as e:
        st.error(
            f"❌ **Lỗi: Không thể đọc tệp**\n\n"
            f"Chi tiết: {str(e)}\n\n"
            f"**Giải pháp:** Vui lòng thử tải lại tệp hoặc chọn tệp khác."
        )
        return None

    # Validate image can be opened
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Verify image integrity
        image.verify()
        # Reopen after verify
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        st.error(
            f"❌ **Lỗi: Tệp ảnh bị hỏng hoặc không hợp lệ**\n\n"
            f"Chi tiết: {str(e)}\n\n"
            f"**Giải pháp:** Vui lòng kiểm tra tệp và thử lại với ảnh hợp lệ."
        )
        return None

    # Validate image dimensions
    width, height = image.size
    if width < 1 or height < 1:
        st.error(
            f"❌ **Lỗi: Kích thước ảnh không hợp lệ**\n\n"
            f"Kích thước: {width}x{height} pixels\n\n"
            f"**Giải pháp:** Vui lòng chọn ảnh có kích thước hợp lệ."
        )
        return None

    if width > 2048 or height > 2048:
        st.warning(
            f"⚠️ **Cảnh báo: Ảnh có độ phân giải cao**\n\n"
            f"Kích thước: {width}x{height} pixels\n\n"
            f"Ảnh sẽ được xử lý, nhưng có thể mất nhiều thời gian hơn."
        )

    # Display success message
    st.success(
        f"✅ **Tải ảnh thành công**\n\n"
        f"Tên tệp: {uploaded_file.name}\n"
        f"Kích thước: {file_size / 1024:.2f}KB\n"
        f"Độ phân giải: {width}x{height} pixels"
    )

    return image_bytes, uploaded_file.name, image


def display_image_with_caption(
    image: Image.Image, caption: str = "Ảnh X-quang ngực", use_column_width: bool = True
):
    """
    Display an image with Vietnamese caption.

    Args:
        image: PIL Image to display
        caption: Caption text in Vietnamese
        use_column_width: Whether to use full column width
    """
    st.image(image, caption=caption, use_column_width=use_column_width)


def display_image_info(image: Image.Image) -> None:
    """
    Display image metadata information.

    Args:
        image: PIL Image to show info for
    """
    width, height = image.size
    mode = image.mode
    format_name = image.format if image.format else "Unknown"

    st.info(
        f"ℹ️ **Thông tin ảnh**\n\n"
        f"- Độ phân giải: {width}x{height} pixels\n"
        f"- Định dạng: {format_name}\n"
        f"- Chế độ màu: {mode}\n"
        f"- Tổng số pixel: {width * height:,}"
    )


def render_upload_instructions() -> None:
    """
    Render instructions for uploading images.
    """
    st.markdown(
        """
    ### 📋 Hướng dẫn tải ảnh
    
    **Yêu cầu:**
    - ✅ Định dạng: PNG, JPG, hoặc JPEG
    - ✅ Kích thước tối đa: 10MB
    - ✅ Độ phân giải đề xuất: 512x512 đến 2048x2048 pixels
    
    **Lưu ý:**
    - ⚠️ Chỉ tải ảnh X-quang ngực để có kết quả chính xác
    - ⚠️ Ảnh nên có độ tương phản tốt và rõ nét
    - ⚠️ Tránh ảnh bị mờ, nhiễu hoặc có watermark
    """
    )


def show_upload_error(error_message: str) -> None:
    """
    Display an upload error message in Vietnamese.

    Args:
        error_message: Error message to display
    """
    st.error(
        f"❌ **Lỗi tải ảnh**\n\n"
        f"{error_message}\n\n"
        f"**Giải pháp:** Vui lòng kiểm tra tệp và thử lại."
    )


def show_upload_success(filename: str, size_kb: float) -> None:
    """
    Display an upload success message in Vietnamese.

    Args:
        filename: Name of uploaded file
        size_kb: File size in kilobytes
    """
    st.success(
        f"✅ **Tải ảnh thành công**\n\n"
        f"Tên tệp: {filename}\n"
        f"Kích thước: {size_kb:.2f}KB"
    )
