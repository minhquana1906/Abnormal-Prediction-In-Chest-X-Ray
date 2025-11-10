"""
Detection page for chest X-ray abnormality detection.

Allows users to upload X-ray images and get disease detection results
with bounding boxes, Vietnamese labels, and health information.
"""

import streamlit as st
import base64
from io import BytesIO
from PIL import Image

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

from utils.api_client import (
    upload_image,
    analyze_image_for_detection,
)
from components.health_card import (
    render_health_cards,
    render_detection_summary,
)
from utils.image_display import display_xray_image, format_image_info


def render_detection_page():
    """
    Render the disease detection page with upload, analysis, and results.
    """
    st.title("🔬 Phát hiện bệnh từ X-quang phổi")

    st.markdown(
        """
        Tải lên ảnh X-quang phổi để phát hiện các bất thường với công nghệ AI.
        
        **Hỗ trợ:**
        - Định dạng: PNG, JPG, JPEG
        - Kích thước tối đa: 10MB
        - 14 loại bệnh phổ biến
        """
    )

    # Create tabs for organization
    tab1, tab2, tab3 = st.tabs(
        ["📤 Tải ảnh lên", "🔍 Kết quả phân tích", "📊 Thông tin sức khỏe"]
    )

    # Initialize session state
    if "detection_image_id" not in st.session_state:
        st.session_state.detection_image_id = None
    if "detection_result" not in st.session_state:
        st.session_state.detection_result = None
    if "detection_original_image" not in st.session_state:
        st.session_state.detection_original_image = None

    # Tab 1: Upload (T051)
    with tab1:
        st.subheader("Tải ảnh X-quang lên")

        uploaded_file = st.file_uploader(
            "Chọn ảnh X-quang phổi",
            type=["png", "jpg", "jpeg"],
            help="Tải lên ảnh X-quang phổi để phát hiện bệnh",
            key="detection_uploader",
        )

        if uploaded_file is not None:
            # Display uploaded image with size constraint
            image = Image.open(uploaded_file)
            display_xray_image(image, "Ảnh đã tải lên", max_width=600)

            # Store original image
            st.session_state.detection_original_image = image

            # Show image info
            st.info(
                f"📷 **Thông tin ảnh:**\n"
                f"- Tên file: {uploaded_file.name}\n"
                f"- Thông số: {format_image_info(image)}\n"
                f"- Dung lượng: {uploaded_file.size / 1024:.1f} KB"
            )

            # Upload to backend
            if st.button(
                "⬆️ Tải lên server", type="primary", key="upload_detection_btn"
            ):
                with st.spinner("Đang tải ảnh lên..."):
                    try:
                        # Reset file pointer and read bytes
                        uploaded_file.seek(0)
                        image_bytes = uploaded_file.read()

                        # Upload to backend
                        response = upload_image(image_bytes, uploaded_file.name)

                        if response and response.get("image_id"):
                            st.session_state.detection_image_id = response["image_id"]
                            st.success(
                                f"✅ Tải ảnh lên thành công!\n\n"
                                f"ID: `{response['image_id']}`\n\n"
                                f"Chuyển sang tab **🔍 Kết quả phân tích** để phân tích ảnh."
                            )
                        else:
                            st.error("❌ Lỗi: Không nhận được ID ảnh từ server.")

                    except Exception as e:
                        # T057: Vietnamese error handling
                        st.error(
                            f"❌ **Lỗi tải ảnh:**\n\n{str(e)}\n\n"
                            f"Vui lòng thử lại hoặc chọn ảnh khác."
                        )
                        raise e
        else:
            st.info("👆 Vui lòng chọn ảnh X-quang để bắt đầu.")

    # Tab 2: Analysis Results (T052, T054, T055, T056)
    with tab2:
        st.subheader("Kết quả phân tích")

        if st.session_state.detection_image_id is None:
            st.warning("⚠️ Vui lòng tải ảnh lên ở tab **📤 Tải ảnh lên** trước.")
        else:
            st.success(
                f"✅ Ảnh đã sẵn sàng - ID: `{st.session_state.detection_image_id}`"
            )

            # T054: Analyze button with spinner
            if st.button("🔬 Phân tích ảnh", type="primary", key="analyze_btn"):
                with st.spinner("🔍 Đang phân tích ảnh..."):
                    try:
                        # Call detection API
                        result = analyze_image_for_detection(
                            st.session_state.detection_image_id,
                            draw_low_confidence=False,
                        )

                        if result and result.get("success"):
                            st.session_state.detection_result = result
                            st.success(
                                f"✅ Phân tích hoàn tất trong {result.get('processing_time_ms', 0)}ms!"
                            )
                        else:
                            # T057: Error handling
                            error_msg = (
                                result.get("error", "Không xác định")
                                if result
                                else "Không nhận được phản hồi"
                            )
                            st.error(
                                f"❌ **Phân tích thất bại:**\n\n{error_msg}\n\n"
                                f"Vui lòng thử lại sau."
                            )

                    except Exception as e:
                        # T057: Vietnamese error handling
                        st.error(
                            f"❌ **Lỗi khi phân tích:**\n\n{str(e)}\n\n"
                            f"Vui lòng kiểm tra kết nối mạng và thử lại."
                        )

            # Display results if available (T052, T056)
            if st.session_state.detection_result:
                result = st.session_state.detection_result
                is_normal = result.get("is_normal", False)
                detections = result.get("detections", [])
                annotated_image_b64 = result.get("annotated_image", "")

                st.markdown("---")

                # T056: Normal image display
                if is_normal:
                    st.success(
                        """
                        ## ✅ Kết quả: Bình thường
                        
                        Không phát hiện bất thường trong ảnh X-quang phổi.
                        
                        **Lưu ý quan trọng:**
                        - Kết quả này chỉ mang tính chất tham khảo từ AI
                        - Không thay thế chẩn đoán y khoa chuyên nghiệp
                        - Vui lòng tham khảo ý kiến bác sĩ chuyên khoa để được tư vấn chính xác
                        """
                    )

                    # Show original image for normal case
                    if st.session_state.detection_original_image:
                        display_xray_image(
                            st.session_state.detection_original_image,
                            "Ảnh X-quang (Bình thường)",
                            max_width=600,
                        )

                else:
                    # T052: Show annotated image with bounding boxes
                    st.warning(
                        f"""
                        ## ⚠️ Phát hiện {len(detections)} bất thường
                        
                        Hệ thống đã phát hiện các dấu hiệu bất thường trong ảnh X-quang.
                        
                        **Khuyến nghị:**
                        - Liên hệ bác sĩ chuyên khoa ngay để được thăm khám
                        - Xem chi tiết ở tab **📊 Thông tin sức khỏe**
                        """
                    )

                    if annotated_image_b64:
                        try:
                            # Decode base64 image
                            image_bytes = base64.b64decode(annotated_image_b64)
                            annotated_image = Image.open(BytesIO(image_bytes))

                            # Display annotated image with size constraint
                            display_xray_image(
                                annotated_image,
                                f"Ảnh đã phân tích ({len(detections)} phát hiện)",
                                max_width=600,
                            )

                            # T055: Download button for annotated image
                            st.markdown("### 💾 Tải xuống kết quả")

                            # Convert to PNG bytes for download
                            img_buffer = BytesIO()
                            annotated_image.save(img_buffer, format="PNG")
                            img_bytes = img_buffer.getvalue()

                            st.download_button(
                                label="📥 Tải ảnh đã phân tích (PNG)",
                                data=img_bytes,
                                file_name="xray_detection_result.png",
                                mime="image/png",
                                help="Tải xuống ảnh với khung đánh dấu bệnh",
                            )

                        except Exception as e:
                            st.error(f"❌ Lỗi hiển thị ảnh: {str(e)}")

                    # Show detection details
                    if detections:
                        st.markdown("### 📋 Danh sách phát hiện")

                        for i, det in enumerate(detections, 1):
                            tier_icon = {"high": "🔴", "medium": "🟠", "low": "⚪"}.get(
                                det.get("confidence_tier", "medium"), "⚪"
                            )

                            st.markdown(
                                f"{i}. {tier_icon} **{det.get('class_name_vi', 'N/A')}** "
                                f"({det.get('class_name_en', 'N/A')}) - "
                                f"Độ tin cậy: {det.get('confidence', 0):.1%}"
                            )

                # Performance info
                st.caption(
                    f"⏱️ Thời gian xử lý: {result.get('processing_time_ms', 0)}ms"
                )

    # Tab 3: Health Information (T053)
    with tab3:
        st.subheader("Thông tin sức khỏe chi tiết")

        if st.session_state.detection_result is None:
            st.info("ℹ️ Vui lòng phân tích ảnh ở tab **🔍 Kết quả phân tích** trước.")
        else:
            result = st.session_state.detection_result
            is_normal = result.get("is_normal", False)
            detections = result.get("detections", [])

            # Show summary
            render_detection_summary(detections, is_normal)

            st.markdown("---")

            # Show health cards for each detection
            if not is_normal and detections:
                render_health_cards(detections)
            elif is_normal:
                st.success(
                    """
                    ### ✅ Không có bất thường
                    
                    Ảnh X-quang phổi của bạn không có dấu hiệu bất thường theo kết quả phân tích AI.
                    
                    **Tuy nhiên, xin lưu ý:**
                    - Kết quả này chỉ mang tính chất tham khảo
                    - Không thay thế việc khám và tư vấn y tế chuyên nghiệp
                    - Nếu có triệu chứng bất thường, vui lòng đến cơ sở y tế để được thăm khám
                    """
                )


__all__ = ["render_detection_page"]
