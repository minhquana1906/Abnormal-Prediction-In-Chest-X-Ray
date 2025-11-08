"""
Streamlit main application for Chest X-Ray Abnormality Detection.

This is the entry point for the frontend UI with two main tabs:
1. Image Filter Processing
2. Disease Detection
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Phân tích X-quang ngực",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Application title
st.title("🏥 Hệ thống phân tích X-quang ngực")
st.markdown("---")

# Create tabs for different features
tab1, tab2 = st.tabs(
    [
        "🎨 Xử lý bộ lọc ảnh",  # Image Filter Processing
        "🔍 Phát hiện bệnh lý",  # Disease Detection
    ]
)

# Tab 1: Image Filter Processing
with tab1:
    # Import and render filter processing page
    try:
        from pages.filter_processing import render_filter_processing_page
        render_filter_processing_page()
    except Exception as e:
        st.error(f"❌ Lỗi tải trang xử lý bộ lọc: {str(e)}")
        st.info("🚧 Vui lòng đảm bảo backend đang chạy và dependencies đã được cài đặt.")

# Tab 2: Disease Detection (T051-T057)
with tab2:
    # Import and render detection page
    try:
        from pages.detection import render_detection_page
        render_detection_page()
    except Exception as e:
        st.error(f"❌ Lỗi tải trang phát hiện bệnh lý: {str(e)}")
        st.info("🚧 Vui lòng đảm bảo backend đang chạy và dependencies đã được cài đặt.")

# Sidebar information
with st.sidebar:
    st.header("ℹ️ Thông tin")
    st.markdown(
        """
    **Phiên bản:** 1.0.0
    
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

    st.markdown("---")
    st.caption("© 2025 Chest X-Ray Abnormality Detection")

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: gray; font-size: 14px;'>
    🏥 Hệ thống phân tích X-quang ngực | Phiên bản MVP 1.0.0<br>
    ⚠️ Chỉ dùng cho mục đích nghiên cứu và giáo dục
</div>
""",
    unsafe_allow_html=True,
)
