import streamlit as st
from typing import Dict, List


def render_health_card(detection: Dict) -> None:
    """
    Render a health information card for a single detection.

    Args:
        detection: Detection dictionary containing class names, confidence, and health info
    """
    class_name_vi = detection.get("class_name_vi", "")
    class_name_en = detection.get("class_name_en", "")
    confidence = detection.get("confidence", 0.0)
    confidence_tier = detection.get("confidence_tier", "medium")
    health_description = detection.get("health_description", "")
    health_warning = detection.get("health_warning", "")

    # Color coding by confidence tier
    tier_colors = {
        "high": "#ff4444",  # Red for high confidence
        "medium": "#ffa500",  # Orange for medium confidence
        "low": "#888888",  # Gray for low confidence
    }

    tier_icons = {"high": "🔴", "medium": "🟠", "low": "⚪"}

    color = tier_colors.get(confidence_tier, "#888888")
    icon = tier_icons.get(confidence_tier, "⚪")

    # Create card with colored border
    st.markdown(
        f"""
        <div style="
            border-left: 4px solid {color};
            padding: 15px;
            margin: 10px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
        ">
            <h4 style="margin: 0 0 10px 0; color: {color};">
                {icon} {class_name_vi}
            </h4>
            <p style="margin: 5px 0; font-size: 0.9em; color: #666;">
                <em>{class_name_en}</em> - Độ tin cậy: {confidence:.1%}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Description section
    if health_description:
        # st.markdown("**📋 Mô tả:**")
        st.write(health_description)

    # Warning section (if exists)
    if health_warning:
        # Check if urgent (Pneumothorax case)
        is_urgent = (
            "CẤP CỨU" in health_warning.upper() or "NGAY" in health_warning.upper()
        )

        if is_urgent:
            st.error(f"🚨 **KHẨN CẤP:** {health_warning}")
        else:
            st.warning(f"⚠️ **Lưu ý:** {health_warning}")

    st.markdown("---")


def render_health_cards(detections: List[Dict]) -> None:
    """
    Render health information cards for all detections.

    Args:
        detections: List of detection dictionaries
    """
    if not detections:
        st.info("ℹ️ Không có thông tin sức khỏe để hiển thị.")
        return

    st.subheader(f"📊 Thông tin sức khỏe ({len(detections)} phát hiện)")

    # Sort by confidence (high to low)
    sorted_detections = sorted(
        detections, key=lambda x: x.get("confidence", 0), reverse=True
    )

    for i, detection in enumerate(sorted_detections, 1):
        with st.expander(
            f"{i}. {detection.get('class_name_vi', 'N/A')} - {detection.get('confidence', 0):.1%}",
            expanded=(i == 1),  # Expand first card by default
        ):
            render_health_card(detection)


def render_detection_summary(detections: List[Dict], is_normal: bool) -> None:
    """
    Render a summary of detection results.

    Args:
        detections: List of detection dictionaries
        is_normal: Whether image is classified as normal
    """
    if is_normal:
        st.success(
            """
            ✅ **Kết quả: Bình thường**
            
            Không phát hiện bất thường trong ảnh X-quang phổi của bạn.
            
            **Lưu ý:** Kết quả này chỉ mang tính chất tham khảo. 
            Vui lòng tham khảo ý kiến bác sĩ chuyên khoa để được tư vấn chính xác.
            """
        )
    else:
        # Count by confidence tier
        high_conf = len([d for d in detections if d.get("confidence_tier") == "high"])
        medium_conf = len(
            [d for d in detections if d.get("confidence_tier") == "medium"]
        )

        st.warning(
            f"""
            ⚠️ **Phát hiện bất thường**
            
            Hệ thống đã phát hiện **{len(detections)} bất thường** trong ảnh X-quang:
            - 🔴 Độ tin cậy cao (>70%): {high_conf} phát hiện
            - 🟠 Độ tin cậy trung bình (40-70%): {medium_conf} phát hiện
            
            **Quan trọng:** Vui lòng liên hệ bác sĩ chuyên khoa ngay để được thăm khám và tư vấn điều trị.
            """
        )


__all__ = ["render_health_card", "render_health_cards", "render_detection_summary"]
