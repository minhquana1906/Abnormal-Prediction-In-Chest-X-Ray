"""
Filter Processing page - Apply image processing filters to chest X-ray images.

This page allows medical professionals to upload chest X-ray images and
apply various image processing filters to enhance visualization.
"""

import streamlit as st
from PIL import Image
import io
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_client import (
    upload_image,
    get_available_filters,
    apply_filters,
    APIError,
    format_api_error,
    check_backend_health,
)
from components.image_uploader import render_image_uploader
from components.filter_selector import (
    render_filter_selector,
    render_filter_info_panel,
    render_quick_select,
)
from components.result_display import (
    render_original_image,
    render_processed_results,
    render_download_all_button,
    render_performance_summary,
)


def initialize_session_state():
    """Initialize session state variables."""
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    if "image_id" not in st.session_state:
        st.session_state.image_id = None
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None
    if "filter_results" not in st.session_state:
        st.session_state.filter_results = None
    if "selected_filters" not in st.session_state:
        st.session_state.selected_filters = []


def render_page_header():
    """Render the page header with title and description."""
    st.title("🎨 Xử Lý Ảnh X-Quang")

    st.markdown(
        """
    Tải lên ảnh X-quang ngực và áp dụng các bộ lọc xử lý ảnh để tăng cường hình ảnh.
    
    **Tính năng:**
    - ✅ Hỗ trợ 8 bộ lọc xử lý ảnh chuyên nghiệp
    - ✅ Xử lý nhiều bộ lọc cùng lúc
    - ✅ So sánh ảnh gốc và ảnh đã xử lý
    - ✅ Tải xuống kết quả đã xử lý
    - ✅ Thống kê hiệu suất xử lý
    """
    )


def check_backend_connection():
    """Check backend connection and display status."""
    with st.spinner("🔍 Kiểm tra kết nối máy chủ..."):
        if not check_backend_health():
            st.error(
                """
            ❌ **Không thể kết nối tới máy chủ backend!**
            
            Vui lòng đảm bảo máy chủ backend đang chạy:
            ```bash
            cd "d:\\Semester_1_2024_2025\\Image processing\\Abnormal-Prediction-In-Chest-X-Ray"
            uvicorn backend.src.api.main:app --reload --port 8000
            ```
            """
            )
            st.stop()


def handle_image_upload(uploaded_file):
    """
    Handle image upload and store in session state.

    Args:
        uploaded_file: Streamlit UploadedFile object
    """
    try:
        # Read image bytes
        image_bytes = uploaded_file.getvalue()

        # Load image for display
        image = Image.open(io.BytesIO(image_bytes))

        # Upload to backend
        with st.spinner("📤 Đang tải ảnh lên máy chủ..."):
            response = upload_image(image_bytes, uploaded_file.name)

        # Store in session state
        st.session_state.uploaded_image = image
        st.session_state.image_id = response["image_id"]
        st.session_state.uploaded_filename = uploaded_file.name
        st.session_state.filter_results = None  # Reset previous results

        st.success(f"✅ Tải ảnh thành công! ID: `{response['image_id']}`")
        st.info(
            f"📊 Kích thước: {response['width']} x {response['height']} pixels | "
            f"Dung lượng: {response['size_bytes'] / 1024:.1f} KB"
        )

    except APIError as e:
        st.error(format_api_error(e))
    except Exception as e:
        st.error(f"❌ Lỗi không xác định: {str(e)}")


def handle_filter_application(image_id: str, selected_filters: list):
    """
    Handle filter application and store results.

    Args:
        image_id: Uploaded image ID
        selected_filters: List of selected filter IDs
    """
    try:
        # Apply filters with progress indicator
        with st.spinner(f"⚙️ Đang áp dụng {len(selected_filters)} bộ lọc..."):
            response = apply_filters(image_id, selected_filters)

        # Store results in session state
        st.session_state.filter_results = response

        st.success(f"✅ Đã xử lý thành công {len(response['results'])} bộ lọc!")
        st.balloons()

    except APIError as e:
        st.error(format_api_error(e))
    except Exception as e:
        st.error(f"❌ Lỗi không xác định: {str(e)}")


def render_filter_processing_page():
    """Render the main filter processing page."""
    # Initialize session state
    initialize_session_state()

    # Render header
    render_page_header()

    # Check backend connection
    check_backend_connection()

    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📤 Tải Ảnh", "🎛️ Chọn Bộ Lọc", "✨ Kết Quả"])

    with tab1:
        st.header("📤 Tải Ảnh X-Quang")

        # File uploader
        uploaded_file = st.file_uploader(
            "Chọn ảnh X-quang ngực (PNG, JPG, JPEG)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=False,
            help="Tải lên ảnh X-quang ngực để xử lý. Kích thước tối đa: 10MB",
        )

        if uploaded_file is not None:
            # Check if this is a new upload
            if st.session_state.uploaded_filename != uploaded_file.name:
                handle_image_upload(uploaded_file)

            # Display uploaded image
            if st.session_state.uploaded_image is not None:
                st.markdown("---")
                render_original_image(
                    st.session_state.uploaded_image, st.session_state.uploaded_filename
                )
        else:
            st.info("ℹ️ Vui lòng tải lên ảnh X-quang để tiếp tục")

    with tab2:
        st.header("🎛️ Chọn Bộ Lọc Xử Lý")

        if st.session_state.image_id is None:
            st.warning("⚠️ Vui lòng tải ảnh lên trước khi chọn bộ lọc (Tab 'Tải Ảnh')")
        else:
            try:
                # Get available filters
                with st.spinner("🔍 Đang tải danh sách bộ lọc..."):
                    filters = get_available_filters()

                # Quick select buttons
                render_quick_select(filters)

                st.markdown("---")

                # Filter selector
                selected_filters = render_filter_selector(filters)

                st.markdown("---")

                # Apply filters button
                if selected_filters:
                    if st.button(
                        f"✨ Áp Dụng {len(selected_filters)} Bộ Lọc",
                        type="primary",
                        width="stretch",
                        key="apply_filters_btn",
                    ):
                        handle_filter_application(
                            st.session_state.image_id, selected_filters
                        )
                else:
                    st.button(
                        "✨ Áp Dụng Bộ Lọc",
                        type="primary",
                        width="stretch",
                        disabled=True,
                        help="Vui lòng chọn ít nhất một bộ lọc",
                    )

                st.markdown("---")

                # Filter information panel
                render_filter_info_panel(filters)

            except APIError as e:
                st.error(format_api_error(e))
            except Exception as e:
                st.error(f"❌ Lỗi không xác định: {str(e)}")

    with tab3:
        st.header("✨ Kết Quả Xử Lý")

        if st.session_state.filter_results is None:
            st.info(
                "ℹ️ Chưa có kết quả. Vui lòng chọn và áp dụng bộ lọc ở Tab 'Chọn Bộ Lọc'"
            )
        else:
            results = st.session_state.filter_results["results"]
            total_time_ms = st.session_state.filter_results["total_time_ms"]

            # Display results
            render_processed_results(results, total_time_ms)

            st.markdown("---")

            # Performance summary
            render_performance_summary(results, total_time_ms)

            st.markdown("---")

            # Download all button
            if len(results) > 1:
                render_download_all_button(results, st.session_state.uploaded_filename)

            # Reset button
            st.markdown("---")
            if st.button("🔄 Xử Lý Ảnh Mới", width="stretch"):
                # Clear session state
                st.session_state.uploaded_image = None
                st.session_state.image_id = None
                st.session_state.uploaded_filename = None
                st.session_state.filter_results = None
                st.session_state.selected_filters = []
                st.rerun()


# Main entry point
if __name__ == "__main__":
    render_filter_processing_page()
