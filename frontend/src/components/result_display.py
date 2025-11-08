"""
Result display component for showing original and processed images.

This component displays the original image alongside filtered results
in a side-by-side comparison layout with processing time information.
"""

import streamlit as st
import base64
from io import BytesIO
from PIL import Image
from typing import List, Dict, Any, Optional


def decode_base64_image(base64_string: str) -> Image.Image:
    """
    Decode a base64 encoded image string to PIL Image.

    Args:
        base64_string: Base64 encoded image string

    Returns:
        PIL Image object
    """
    image_bytes = base64.b64decode(base64_string)
    return Image.open(BytesIO(image_bytes))


def create_download_link(base64_string: str, filename: str) -> str:
    """
    Create a download link for a base64 encoded image.

    Args:
        base64_string: Base64 encoded image string
        filename: Download filename

    Returns:
        HTML download link
    """
    href = f"data:image/png;base64,{base64_string}"
    return f'<a href="{href}" download="{filename}">📥 Tải xuống {filename}</a>'


def render_original_image(image: Image.Image, filename: str):
    """
    Render the original uploaded image.

    Args:
        image: PIL Image object
        filename: Original filename
    """
    st.subheader("📷 Ảnh Gốc")

    # Display image info
    width, height = image.size
    st.caption(f"**Tên file:** {filename}")
    st.caption(f"**Kích thước:** {width} x {height} pixels")

    # Display image
    st.image(image, width="stretch")


def render_processed_results(results: List[Dict[str, Any]], total_time_ms: int):
    """
    Render processed filter results in a grid layout.

    Args:
        results: List of processed image results from API
        total_time_ms: Total processing time in milliseconds
    """
    st.subheader(f"✨ Kết Quả Xử Lý ({len(results)} bộ lọc)")

    # Display total processing time
    st.metric(
        label="⏱️ Tổng Thời Gian Xử Lý",
        value=f"{total_time_ms} ms",
        delta=f"{total_time_ms / 1000:.2f}s",
    )

    # Display results in a grid (2 columns)
    for idx in range(0, len(results), 2):
        cols = st.columns(2)

        for col_idx, col in enumerate(cols):
            result_idx = idx + col_idx

            if result_idx < len(results):
                result = results[result_idx]

                with col:
                    render_single_result(result, result_idx + 1)


def render_single_result(result: Dict[str, Any], result_number: int):
    """
    Render a single processed result.

    Args:
        result: Single result dictionary with filter info
        result_number: Display number for the result
    """
    filter_name = result["filter_name"]
    display_name = result["display_name"]
    image_base64 = result["image_base64"]
    processing_time_ms = result["processing_time_ms"]

    # Create container for this result
    with st.container(border=True):
        st.markdown(f"### {result_number}. {display_name}")
        st.caption(f"**Bộ lọc:** `{filter_name}`")
        st.caption(
            f"**Thời gian:** {processing_time_ms} ms ({processing_time_ms / 1000:.3f}s)"
        )

        # Decode and display image
        try:
            processed_image = decode_base64_image(image_base64)
            st.image(processed_image, width="stretch")

            # Download button
            download_filename = f"{filter_name}_processed.png"
            st.download_button(
                label=f"📥 Tải xuống",
                data=base64.b64decode(image_base64),
                file_name=download_filename,
                mime="image/png",
                key=f"download_{filter_name}_{result_number}",
                width="stretch",
            )

        except Exception as e:
            st.error(f"❌ Lỗi hiển thị ảnh: {str(e)}")


def render_side_by_side_comparison(
    original_image: Image.Image,
    processed_image: Image.Image,
    filter_name: str,
    processing_time_ms: int,
):
    """
    Render original and processed images side-by-side for comparison.

    Args:
        original_image: Original PIL Image
        processed_image: Processed PIL Image
        filter_name: Name of the filter applied
        processing_time_ms: Processing time in milliseconds
    """
    st.subheader(f"🔍 So Sánh: {filter_name}")
    st.caption(
        f"⏱️ Thời gian xử lý: {processing_time_ms} ms ({processing_time_ms / 1000:.3f}s)"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Ảnh Gốc")
        st.image(original_image, width="stretch")

    with col2:
        st.markdown("#### Ảnh Đã Xử Lý")
        st.image(processed_image, width="stretch")


def render_download_all_button(results: List[Dict[str, Any]], original_filename: str):
    """
    Render a button to download all processed images as a ZIP file.

    Args:
        results: List of processed results
        original_filename: Original filename for naming the ZIP
    """
    import zipfile
    from io import BytesIO

    st.markdown("---")
    st.markdown("### 📦 Tải Xuống Tất Cả")

    if st.button("📥 Tải xuống tất cả ảnh đã xử lý (ZIP)", width="stretch"):
        # Create ZIP file in memory
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for result in results:
                filter_name = result["filter_name"]
                image_base64 = result["image_base64"]

                # Decode image
                image_bytes = base64.b64decode(image_base64)

                # Add to ZIP
                filename = f"{filter_name}_{original_filename}.png"
                zip_file.writestr(filename, image_bytes)

        # Provide download
        zip_buffer.seek(0)
        st.download_button(
            label="💾 Tải xuống ZIP",
            data=zip_buffer.getvalue(),
            file_name=f"filtered_images_{original_filename}.zip",
            mime="application/zip",
            width="stretch",
        )

        st.success(f"✅ Đã tạo file ZIP chứa {len(results)} ảnh đã xử lý!")


def render_performance_summary(results: List[Dict[str, Any]], total_time_ms: int):
    """
    Render performance summary with timing breakdown.

    Args:
        results: List of processed results
        total_time_ms: Total processing time in milliseconds
    """
    with st.expander("📊 Thống Kê Hiệu Suất", expanded=False):
        st.markdown("### Phân Tích Thời Gian Xử Lý")

        # Create DataFrame for display
        import pandas as pd

        timing_data = []
        for result in results:
            timing_data.append(
                {
                    "Bộ Lọc": result["display_name"],
                    "Thời Gian (ms)": result["processing_time_ms"],
                    "Thời Gian (s)": f"{result['processing_time_ms'] / 1000:.3f}",
                    "Phần Trăm": f"{(result['processing_time_ms'] / total_time_ms * 100):.1f}%",
                }
            )

        df = pd.DataFrame(timing_data)
        st.dataframe(df, width="stretch", hide_index=True)

        # Summary metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            avg_time = total_time_ms / len(results)
            st.metric("⏱️ Trung Bình", f"{avg_time:.1f} ms")

        with col2:
            min_time = min(r["processing_time_ms"] for r in results)
            st.metric("🏃 Nhanh Nhất", f"{min_time} ms")

        with col3:
            max_time = max(r["processing_time_ms"] for r in results)
            st.metric("🐌 Chậm Nhất", f"{max_time} ms")


__all__ = [
    "decode_base64_image",
    "create_download_link",
    "render_original_image",
    "render_processed_results",
    "render_single_result",
    "render_side_by_side_comparison",
    "render_download_all_button",
    "render_performance_summary",
]
