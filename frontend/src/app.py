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
    st.header("Xử lý bộ lọc ảnh X-quang")
    st.markdown(
        """
    Tải lên ảnh X-quang ngực và áp dụng các bộ lọc xử lý ảnh để nâng cao khả năng quan sát.
    
    **Các bộ lọc khả dụng:**
    - Phát hiện cạnh Sobel
    - Phát hiện cạnh Canny
    - Làm mờ Gaussian
    - Bộ lọc trung vị
    - Cân bằng histogram
    - Biến đổi Fourier
    - Biến đổi Cosine rời rạc (DCT)
    - Phân ngưỡng Otsu
    """
    )

    # Placeholder for filter processing page
    st.info("🚧 Giao diện xử lý bộ lọc sẽ được tích hợp ở đây (Task T037-T042)")

    # Import filter processing page (will be available after T037-T042)
    # from frontend.src.pages.filter_processing import render_filter_processing_page
    # render_filter_processing_page()

# Tab 2: Disease Detection
with tab2:
    st.header("Phát hiện bệnh lý X-quang ngực")
    st.markdown(
        """
    Tải lên ảnh X-quang ngực để phát hiện các bất thường với công nghệ AI.
    
    **Tính năng:**
    - Phát hiện 14 loại bệnh lý ngực
    - Hiển thị khung giới hạn với độ tin cậy
    - Thông tin sức khỏe bằng tiếng Việt
    - Cảnh báo y tế quan trọng
    """
    )

    # Placeholder for detection page
    st.info("🚧 Giao diện phát hiện bệnh lý sẽ được tích hợp ở đây (Task T051-T057)")

    # Import detection page (will be available after T051-T057)
    # from frontend.src.pages.detection import render_detection_page
    # render_detection_page()

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
