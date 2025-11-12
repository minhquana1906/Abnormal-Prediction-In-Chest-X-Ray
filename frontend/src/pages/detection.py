import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_client import (
    upload_image,
    analyze_image_for_detection,
    check_backend_health,
    APIError,
    format_api_error,
)
from utils.image_display import display_xray_image, format_image_info
from components.health_card import render_health_cards, render_detection_summary


def initialize_session_state():
    if "detection_uploaded_image" not in st.session_state:
        st.session_state.detection_uploaded_image = None
    if "detection_image_id" not in st.session_state:
        st.session_state.detection_image_id = None
    if "detection_uploaded_filename" not in st.session_state:
        st.session_state.detection_uploaded_filename = None
    if "detection_result" not in st.session_state:
        st.session_state.detection_result = None


def render_page_header():
    st.title("🔬 Phát Hiện Bệnh Lý X-Quang")

    st.markdown(
        """
    Tải lên ảnh X-quang ngực và phát hiện các bất thường với công nghệ AI tiên tiến.
    """
    )


def check_backend_connection():
    with st.spinner("🔍 Kiểm tra kết nối máy chủ..."):
        if not check_backend_health():
            st.error(
                """
            ❌ **Không thể kết nối tới máy chủ backend!**
            
            Vui lòng đảm bảo máy chủ backend đang chạy (port 8000).
            """
            )
            st.stop()


def handle_image_upload(uploaded_file):
    try:
        # Read image bytes
        image_bytes = uploaded_file.getvalue()

        # Load image for display
        image = Image.open(BytesIO(image_bytes))

        # Upload to backend
        with st.spinner("📤 Đang tải ảnh lên máy chủ..."):
            response = upload_image(image_bytes, uploaded_file.name)

        # Store in session state
        st.session_state.detection_uploaded_image = image
        st.session_state.detection_image_id = response["image_id"]
        st.session_state.detection_uploaded_filename = uploaded_file.name
        st.session_state.detection_result = None  # Reset previous results

        st.info(
            f"📊 Kích thước: {response['width']} x {response['height']} pixels | "
            f"Dung lượng: {response['size_bytes'] / 1024:.1f} KB"
        )

    except APIError as e:
        st.error(format_api_error(e))
    except Exception as e:
        st.error(f"❌ Lỗi không xác định: {str(e)}")


def handle_detection_analysis(image_id: str, draw_low_confidence: bool = False):
    try:
        # Analyze image with progress indicator
        with st.spinner("🔬 Đang phân tích ảnh với AI..."):
            result = analyze_image_for_detection(image_id, draw_low_confidence)

        if result and result.get("success"):
            # Store results in session state
            st.session_state.detection_result = result

            is_normal = result.get("is_normal", False)
            detections = result.get("detections", [])

            if is_normal:
                st.success("✅ Phân tích hoàn tất! Không phát hiện bất thường.")
            else:
                st.success(
                    f"✅ Phân tích hoàn tất! Phát hiện {len(detections)} bất thường."
                )
                # st.balloons()
        else:
            # Error handling
            error_msg = (
                result.get("error", "Không xác định")
                if result
                else "Không nhận được phản hồi"
            )
            st.error(
                f"❌ **Phân tích thất bại:**\n\n{error_msg}\n\nVui lòng thử lại sau."
            )

    except APIError as e:
        st.error(format_api_error(e))
    except Exception as e:
        st.error(f"❌ Lỗi không xác định: {str(e)}")


def render_detection_page():
    # Initialize session state
    initialize_session_state()

    # Render header
    render_page_header()

    # Check backend connection
    check_backend_connection()

    st.header("📤 1. Tải Ảnh X-Quang")

    # File uploader
    uploaded_file = st.file_uploader(
        "Chọn ảnh X-quang ngực (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
        help="Tải lên ảnh X-quang ngực để phát hiện bệnh lý. Kích thước tối đa: 10MB",
        key="detection_uploader",
    )

    if uploaded_file is not None:
        # Check if this is a new upload (different file or name)
        if st.session_state.detection_uploaded_filename != uploaded_file.name:
            handle_image_upload(uploaded_file)
            # Reset previous analysis results when new image is uploaded
            st.session_state.detection_result = None

        # Display uploaded image with size constraint
        if st.session_state.detection_uploaded_image is not None:
            st.markdown("#### Ảnh đã tải lên:")
            display_xray_image(
                st.session_state.detection_uploaded_image,
                f"📷 {st.session_state.detection_uploaded_filename}",
                max_width=600,
                enable_fullscreen=False,  # No fullscreen for upload preview
            )
            st.info(f"ℹ️ {format_image_info(st.session_state.detection_uploaded_image)}")
    else:
        st.info("ℹ️ Vui lòng tải lên ảnh X-quang để tiếp tục")

    st.markdown("---")

    st.header("🔬 2. Phân Tích Phát Hiện Bệnh Lý")

    if st.session_state.detection_image_id is None:
        st.warning("⚠️ Vui lòng tải ảnh lên trước khi phân tích (Phần 1 phía trên)")
    else:
        st.success(f"✅ Ảnh đã sẵn sàng - ID: `{st.session_state.detection_image_id}`")

        # Option to draw low confidence detections
        draw_low_confidence = st.checkbox(
            "Hiển thị phát hiện độ tin cậy thấp (<40%)",
            value=False,
            help="Bật tùy chọn này để hiển thị cả các phát hiện có độ tin cậy thấp",
        )

        st.markdown("---")

        # Analyze button
        if st.button(
            "🔬 Phân Tích Ảnh",
            type="primary",
            width="stretch",
            key="analyze_detection_btn",
        ):
            handle_detection_analysis(
                st.session_state.detection_image_id, draw_low_confidence
            )

    st.markdown("---")

    st.header("✨ 3. Kết Quả Phân Tích & Thông Tin Sức Khỏe")

    if st.session_state.detection_result is None:
        st.info("ℹ️ Chưa có kết quả. Vui lòng phân tích ảnh ở Phần 2 phía trên")
    else:
        result = st.session_state.detection_result
        is_normal = result.get("is_normal", False)
        detections = result.get("detections", [])
        annotated_image_b64 = result.get("annotated_image", "")
        processing_time_ms = result.get("processing_time_ms", 0)

        # Display result summary
        if is_normal:
            # Show original image for normal case
            if st.session_state.detection_uploaded_image:
                st.markdown("#### Ảnh X-quang:")
                display_xray_image(
                    st.session_state.detection_uploaded_image,
                    "Ảnh X-quang - Không phát hiện bệnh lý",
                    max_width=600,
                    enable_fullscreen=False,
                )

            st.info(
                """
                #### ℹ️ Kết quả: Không phát hiện bệnh lý
                
                Cơ thể bình thường hoặc có thể ẩn chứa một số bệnh lý khác nằm ngoài 2 bệnh trên, 
                bạn nên liên hệ bác sĩ chuyên khoa ngay để được thăm khám và tư vấn điều trị.
                
                **Lưu ý quan trọng:**
                - Kết quả này chỉ phát hiện 2 bệnh: "Tim to bất thường" và "Phình động mạch chủ"
                - AI chỉ được huấn luyện trên những bệnh này, có thể bỏ sót các bệnh lý khác
                - Không thay thế chẩn đoán y khoa chuyên nghiệp
                - Vui lòng tham khảo ý kiến bác sĩ chuyên khoa để được tư vấn chính xác
                """
            )

        else:
            # Display annotated image
            if annotated_image_b64:
                try:
                    # Decode base64 image
                    image_bytes = base64.b64decode(annotated_image_b64)
                    annotated_image = Image.open(BytesIO(image_bytes))

                    # Display annotated image
                    st.markdown("#### Ảnh đã phân tích:")
                    display_xray_image(
                        annotated_image,
                        f"Phát hiện {len(detections)} bất thường",
                        max_width=600,
                        enable_fullscreen=False,
                    )

                    # Download button for annotated image
                    st.markdown("#### 💾 Tải xuống kết quả:")
                    img_buffer = BytesIO()
                    annotated_image.save(img_buffer, format="PNG")
                    img_bytes = img_buffer.getvalue()

                    st.download_button(
                        label="📥 Tải ảnh đã phân tích (PNG)",
                        data=img_bytes,
                        file_name=f"detection_{st.session_state.detection_uploaded_filename}.png",
                        mime="image/png",
                        help="Tải xuống ảnh với khung đánh dấu bệnh lý",
                        width="stretch",
                    )

                except Exception as e:
                    st.error(f"❌ Lỗi hiển thị ảnh: {str(e)}")

            st.markdown("---")
            # Show health cards for each detection
            render_health_cards(detections)

        st.markdown("---")

        # Reset button
        if st.button("🔄 Làm Mới", width="stretch"):
            # Clear session state
            st.session_state.detection_uploaded_image = None
            st.session_state.detection_image_id = None
            st.session_state.detection_uploaded_filename = None
            st.session_state.detection_result = None
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()


__all__ = ["render_detection_page"]
