import streamlit as st
from typing import List, Dict, Any


def render_filter_selector(filters: List[Dict[str, Any]]) -> List[str]:
    st.subheader("👉️ Chọn Bộ Lọc")

    st.markdown(
        """
    Chọn một hoặc nhiều bộ lọc để xử lý ảnh X-quang của bạn.  
    Bạn có thể chọn tối đa 8 bộ lọc cùng lúc.
    """
    )

    # Create columns for better layout
    col1, col2 = st.columns(2)

    selected_filters = []

    # Split filters into two columns
    mid_point = len(filters) // 2 + len(filters) % 2

    with col1:
        for filter_info in filters[:mid_point]:
            filter_id = filter_info["id"]
            filter_name_vi = filter_info.get("name_vi", filter_info["name"])
            filter_desc_vi = filter_info.get(
                "description_vi", filter_info["description"]
            )

            # Create checkbox with Vietnamese name and description
            if st.checkbox(
                filter_name_vi, key=f"filter_{filter_id}", help=filter_desc_vi
            ):
                selected_filters.append(filter_id)

    with col2:
        for filter_info in filters[mid_point:]:
            filter_id = filter_info["id"]
            filter_name_vi = filter_info.get("name_vi", filter_info["name"])
            filter_desc_vi = filter_info.get(
                "description_vi", filter_info["description"]
            )

            # Create checkbox with Vietnamese name and description
            if st.checkbox(
                filter_name_vi, key=f"filter_{filter_id}", help=filter_desc_vi
            ):
                selected_filters.append(filter_id)

    # Display selected filters count
    if selected_filters:
        st.success(
            f"✅ Đã chọn {len(selected_filters)} bộ lọc: {', '.join(selected_filters)}"
        )
    else:
        st.info("ℹ️ Vui lòng chọn ít nhất một bộ lọc để tiếp tục")

    return selected_filters


def render_filter_info_panel(filters: List[Dict[str, Any]]):

    with st.expander("📖 Thông Tin Chi Tiết Về Các Bộ Lọc", expanded=False):
        st.markdown("### Các Bộ Lọc Có Sẵn")

        for filter_info in filters:
            filter_name = filter_info["name"]
            filter_name_vi = filter_info.get("name_vi", filter_name)
            filter_desc = filter_info["description"]
            filter_desc_vi = filter_info.get("description_vi", filter_desc)
            filter_params = filter_info.get("parameters", {})
            output_type = filter_info.get("output_type", "grayscale")

            st.markdown(f"#### {filter_name_vi}")
            st.markdown(f"**Mô tả:** {filter_desc_vi}")
            st.markdown(f"**Loại đầu ra:** {output_type}")

            if filter_params:
                st.markdown("**Tham số:**")
                for param_name, param_value in filter_params.items():
                    if param_value is not None:
                        st.markdown(f"- `{param_name}`: {param_value}")
                    else:
                        st.markdown(f"- `{param_name}`: Tự động")

            st.markdown("---")


def get_quick_select_presets() -> Dict[str, List[str]]:

    return {
        "Phát hiện cạnh": ["sobel", "canny"],
        "Tăng cường độ tương phản": ["histogram", "gaussian"],
        "Giảm nhiễu": ["median", "gaussian"],
        "Phân tích tần số": ["fourier", "dct"],
        "Phân đoạn": ["otsu"],
        "Tất cả bộ lọc": [
            "sobel",
            "canny",
            "gaussian",
            "median",
            "histogram",
            "fourier",
            "dct",
            "otsu",
        ],
    }


def render_quick_select(filters: List[Dict[str, Any]]) -> List[str]:

    st.markdown("#### ⚡ Chọn Nhanh")

    presets = get_quick_select_presets()

    cols = st.columns(3)

    selected_filters = []

    for idx, (preset_name, preset_filters) in enumerate(presets.items()):
        with cols[idx % 3]:
            if st.button(preset_name, key=f"preset_{idx}", width="stretch"):
                # Update session state to select these filters
                for filter_info in filters:
                    filter_id = filter_info["id"]
                    st.session_state[f"filter_{filter_id}"] = (
                        filter_id in preset_filters
                    )

                selected_filters = preset_filters
                st.rerun()

    return selected_filters


__all__ = [
    "render_filter_selector",
    "render_filter_info_panel",
    "render_quick_select",
    "get_quick_select_presets",
]
