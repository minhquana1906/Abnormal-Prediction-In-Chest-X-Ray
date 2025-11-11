"""
Disease Detection page - Detect abnormalities in chest X-ray images with AI.

This page allows medical professionals to upload chest X-ray images and
detect potential abnormalities using YOLOv11s object detection model.
"""

import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import sys
from pathlib import Path

# Add parent directory to path for imports
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
    """Initialize session state variables."""
    if "detection_uploaded_image" not in st.session_state:
        st.session_state.detection_uploaded_image = None
    if "detection_image_id" not in st.session_state:
        st.session_state.detection_image_id = None
    if "detection_uploaded_filename" not in st.session_state:
        st.session_state.detection_uploaded_filename = None
    if "detection_result" not in st.session_state:
        st.session_state.detection_result = None


def render_page_header():
    """Render the page header with title and description."""
    st.title("🔬 Phát Hiện Bệnh Lý X-Quang")

    st.markdown(
        """
    Tải lên ảnh X-quang ngực và phát hiện các bất thường với công nghệ AI tiên tiến.
    """
    )


def check_backend_connection():
    """Check backend connection and display status."""
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
    """
    Handle image upload and store in session state.

    Args:
        uploaded_file: Streamlit UploadedFile object
    """
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
    """
    Handle detection analysis and store results.

    Args:
        image_id: Uploaded image ID
        draw_low_confidence: Whether to draw low confidence detections
    """
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
                st.balloons()
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
    """Render the main disease detection page with single-page layout."""
    # Initialize session state
    initialize_session_state()

    # Render header
    render_page_header()

    # Check backend connection
    check_backend_connection()

    # ============================================================
    # SECTION 1: UPLOAD IMAGE
    # ============================================================
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
        # Check if this is a new upload
        if st.session_state.detection_uploaded_filename != uploaded_file.name:
            handle_image_upload(uploaded_file)

        # Display uploaded image with size constraint
        if st.session_state.detection_uploaded_image is not None:
            st.markdown("#### Ảnh đã tải lên:")
            display_xray_image(
                st.session_state.detection_uploaded_image,
                f"📷 {st.session_state.detection_uploaded_filename}",
                max_width=300,
                enable_fullscreen=False,  # No fullscreen for upload preview
            )
            st.info(
                f"ℹ️ {format_image_info(st.session_state.detection_uploaded_image)}"
            )
    else:
        st.info("ℹ️ Vui lòng tải lên ảnh X-quang để tiếp tục")

    st.markdown("---")

    # ============================================================
    # SECTION 2: ANALYZE IMAGE
    # ============================================================
    st.header("🔬 2. Phân Tích Phát Hiện Bệnh Lý")

    if st.session_state.detection_image_id is None:
        st.warning("⚠️ Vui lòng tải ảnh lên trước khi phân tích (Phần 1 phía trên)")
    else:
        st.success(
            f"✅ Ảnh đã sẵn sàng - ID: `{st.session_state.detection_image_id}`"
        )

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
            use_container_width=True,
            key="analyze_detection_btn",
        ):
            handle_detection_analysis(
                st.session_state.detection_image_id, draw_low_confidence
            )

    st.markdown("---")

    # ============================================================
    # SECTION 3: RESULTS
    # ============================================================
    st.header("✨ 3. Kết Quả Phân Tích")

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
            st.success(
                """
                ## ✅ Kết quả: Bình thường
                
                Không phát hiện bất thường trong ảnh X-quang ngực.
                
                **Lưu ý quan trọng:**
                - Kết quả này chỉ mang tính chất tham khảo từ AI
                - Không thay thế chẩn đoán y khoa chuyên nghiệp
                - Vui lòng tham khảo ý kiến bác sĩ chuyên khoa để được tư vấn chính xác
                """
            )

            # Show original image for normal case
            if st.session_state.detection_uploaded_image:
                st.markdown("#### Ảnh X-quang (Bình thường):")
                display_xray_image(
                    st.session_state.detection_uploaded_image,
                    "Ảnh X-quang bình thường",
                    max_width=300,
                    enable_fullscreen=True,
                )
        else:
            st.warning(
                f"""
                ## ⚠️ Phát hiện {len(detections)} bất thường
                
                Hệ thống đã phát hiện các dấu hiệu bất thường trong ảnh X-quang.
                
                **Khuyến nghị:**
                - Liên hệ bác sĩ chuyên khoa ngay để được thăm khám
                - Xem chi tiết thông tin sức khỏe bên dưới
                """
            )

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
                        max_width=300,
                        enable_fullscreen=True,
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
                        use_container_width=True,
                    )

                except Exception as e:
                    st.error(f"❌ Lỗi hiển thị ảnh: {str(e)}")

            # Show detection details
            if detections:
                st.markdown("---")
                st.markdown("### 📋 Danh sách phát hiện chi tiết:")

                for i, det in enumerate(detections, 1):
                    tier_icon = {"high": "🔴", "medium": "🟠", "low": "⚪"}.get(
                        det.get("confidence_tier", "medium"), "⚪"
                    )

                    confidence = det.get("confidence", 0)
                    class_name_vi = det.get("class_name_vi", "N/A")
                    class_name_en = det.get("class_name_en", "N/A")

                    st.markdown(
                        f"{i}. {tier_icon} **{class_name_vi}** ({class_name_en}) - "
                        f"Độ tin cậy: **{confidence:.1%}**"
                    )

        # Performance info
        st.markdown("---")
        st.caption(f"⏱️ Thời gian xử lý: {processing_time_ms}ms ({processing_time_ms/1000:.2f}s)")

        st.markdown("---")

        # Health information section
        if not is_normal and detections:
            st.header("📊 4. Thông Tin Sức Khỏe Chi Tiết")

            # Show summary
            render_detection_summary(detections, is_normal)

            st.markdown("---")

            # Show health cards for each detection
            render_health_cards(detections)
        elif is_normal:
            st.header("📊 4. Thông Tin Sức Khỏe")
            st.success(
                """
                ### ✅ Không có bất thường
                
                Ảnh X-quang ngực của bạn không có dấu hiệu bất thường theo kết quả phân tích AI.
                
                **Tuy nhiên, xin lưu ý:**
                - Kết quả này chỉ mang tính chất tham khảo
                - Không thay thế việc khám và tư vấn y tế chuyên nghiệp
                - Nếu có triệu chứng bất thường, vui lòng đến cơ sở y tế để được thăm khám
                """
            )

        st.markdown("---")

        # Reset button
        if st.button("🔄 Phân Tích Ảnh Mới", use_container_width=True):
            # Clear session state
            st.session_state.detection_uploaded_image = None
            st.session_state.detection_image_id = None
            st.session_state.detection_uploaded_filename = None
            st.session_state.detection_result = None
            st.rerun()


__all__ = ["render_detection_page"]
