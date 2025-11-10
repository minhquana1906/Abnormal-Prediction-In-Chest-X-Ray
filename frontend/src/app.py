"""
Streamlit main application for Chest X-Ray Abnormality Detection.

This is the entry point for the frontend UI with two main pages:
1. Image Filter Processing
2. Disease Detection

Navigation is done via sidebar with primary buttons.
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Phân tích X-quang ngực",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state for page navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "filters"  # Default page

# Sidebar navigation
with st.sidebar:
    # Navigation buttons
    if st.button(
        "🎨 Xử lý bộ lọc ảnh",
        type="primary" if st.session_state.current_page == "filters" else "secondary",
        use_container_width=True,
    ):
        st.session_state.current_page = "filters"
        st.rerun()

    if st.button(
        "🔍 Phát hiện bệnh lý",
        type="primary" if st.session_state.current_page == "detection" else "secondary",
        use_container_width=True,
    ):
        st.session_state.current_page = "detection"
        st.rerun()

    st.markdown("---")
    st.header("ℹ️ Thông tin")
    st.markdown(
        """
    
    **Hỗ trợ:**
    - Định dạng: PNG, JPG, JPEG
    - Kích thước tối đa: 10MB
    - Độ phân giải: 512x512 đến 2048x2048
    
    **Lưu ý:**
    - Kết quả chỉ mang tính chất tham khảo
    - Không thay thế chẩn đoán y khoa chuyên nghiệp
    - Luôn tham khảo ý kiến bác sĩ
    """
    )


# Main content area - render selected page
st.title("🏥 Hệ thống phân tích X-quang ngực")
st.markdown("---")

if st.session_state.current_page == "detection":
    # Page 1: Disease Detection (T051-T057)
    try:
        from pages.detection import render_detection_page

        render_detection_page()
    except Exception as e:
        st.error(f"❌ Lỗi tải trang phát hiện bệnh lý: {str(e)}")
        st.info(
            "🚧 Vui lòng đảm bảo backend đang chạy và dependencies đã được cài đặt."
        )

elif st.session_state.current_page == "filters":
    # Page 2: Image Filter Processing
    try:
        from pages.filter_processing import render_filter_processing_page

        render_filter_processing_page()
    except Exception as e:
        st.error(f"❌ Lỗi tải trang xử lý bộ lọc: {str(e)}")
        st.info(
            "🚧 Vui lòng đảm bảo backend đang chạy và dependencies đã được cài đặt."
        )

# # Footer
# st.markdown("---")
# st.markdown(
#     """
# <div style='text-align: center; color: gray; font-size: 14px;'>
#     🏥 Hệ thống phân tích X-quang ngực | Phiên bản MVP 1.0.0<br>
#     ⚠️ Chỉ dùng cho mục đích nghiên cứu và giáo dục
# </div>
# """,
#     unsafe_allow_html=True,
# )
