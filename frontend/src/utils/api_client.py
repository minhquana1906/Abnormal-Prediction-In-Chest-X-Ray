"""
API client for communicating with the backend FastAPI server.

This module provides functions to call backend endpoints from the Streamlit frontend.
"""

import requests
from typing import List, Dict, Optional, Any
import io

# Backend API base URL
API_BASE_URL = "http://localhost:8000"


class APIError(Exception):
    """Custom exception for API errors."""

    pass


def check_backend_health() -> bool:
    """
    Check if backend server is running and healthy.

    Returns:
        True if backend is healthy, False otherwise
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def upload_image(image_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Upload an image to the backend.

    Args:
        image_bytes: Image file content as bytes
        filename: Original filename

    Returns:
        Dictionary with image_id and metadata

    Raises:
        APIError: If upload fails
    """
    try:
        files = {"file": (filename, io.BytesIO(image_bytes), "image/jpeg")}

        response = requests.post(f"{API_BASE_URL}/api/upload", files=files, timeout=30)

        if response.status_code != 200:
            error_detail = response.json().get("detail", "Unknown error")
            raise APIError(f"Tải ảnh thất bại: {error_detail}")

        return response.json()

    except requests.exceptions.RequestException as e:
        raise APIError(f"Không thể kết nối tới máy chủ: {str(e)}")


def get_available_filters() -> List[Dict[str, str]]:
    """
    Get list of available image filters from backend.

    Returns:
        List of filter dictionaries with name, display_name, and description

    Raises:
        APIError: If request fails
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/filters/list", timeout=10)

        if response.status_code != 200:
            error_detail = response.json().get("detail", "Unknown error")
            raise APIError(f"Không thể lấy danh sách bộ lọc: {error_detail}")

        return response.json()["filters"]

    except requests.exceptions.RequestException as e:
        raise APIError(f"Không thể kết nối tới máy chủ: {str(e)}")


def apply_filters(image_id: str, filter_names: List[str]) -> Dict[str, Any]:
    """
    Apply one or more filters to an uploaded image.

    Args:
        image_id: ID of uploaded image
        filter_names: List of filter names to apply

    Returns:
        Dictionary with processed images (base64 encoded) and timing info

    Raises:
        APIError: If processing fails
    """
    try:
        payload = {"image_id": image_id, "filters": filter_names}

        response = requests.post(
            f"{API_BASE_URL}/api/filters/apply",
            json=payload,
            timeout=60,  # Allow up to 60 seconds for filter processing
        )

        if response.status_code != 200:
            error_detail = response.json().get("detail", "Unknown error")
            raise APIError(f"Xử lý bộ lọc thất bại: {error_detail}")

        return response.json()

    except requests.exceptions.Timeout:
        raise APIError("Quá thời gian xử lý. Vui lòng thử lại với ít bộ lọc hơn.")
    except requests.exceptions.RequestException as e:
        raise APIError(f"Không thể kết nối tới máy chủ: {str(e)}")


def detect_abnormalities(image_id: str) -> Dict[str, Any]:
    """
    Detect abnormalities in an uploaded chest X-ray image.

    Args:
        image_id: ID of uploaded image

    Returns:
        Dictionary with detections, annotated image (base64), and timing info

    Raises:
        APIError: If detection fails
    """
    try:
        payload = {"image_id": image_id}

        response = requests.post(
            f"{API_BASE_URL}/api/detection/analyze",
            json=payload,
            timeout=30,  # Allow up to 30 seconds for detection
        )

        if response.status_code != 200:
            error_detail = response.json().get("detail", "Unknown error")
            raise APIError(f"Phát hiện bệnh lý thất bại: {error_detail}")

        return response.json()

    except requests.exceptions.Timeout:
        raise APIError("Quá thời gian phát hiện. Vui lòng thử lại.")
    except requests.exceptions.RequestException as e:
        raise APIError(f"Không thể kết nối tới máy chủ: {str(e)}")


def get_api_info() -> Dict[str, Any]:
    """
    Get API information from root endpoint.

    Returns:
        Dictionary with API version and status

    Raises:
        APIError: If request fails
    """
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)

        if response.status_code != 200:
            raise APIError("Không thể lấy thông tin API")

        return response.json()

    except requests.exceptions.RequestException as e:
        raise APIError(f"Không thể kết nối tới máy chủ: {str(e)}")


def format_api_error(error: APIError) -> str:
    """
    Format API error for user display in Vietnamese.

    Args:
        error: APIError exception

    Returns:
        Formatted error message in Vietnamese
    """
    error_message = str(error)

    # Add helpful context based on error type
    if "kết nối" in error_message.lower():
        return f"""
        ❌ **Lỗi kết nối**
        
        {error_message}
        
        **Giải pháp:**
        - Đảm bảo máy chủ backend đang chạy (port 8000)
        - Kiểm tra kết nối mạng
        - Khởi động lại ứng dụng backend
        """
    elif "quá thời gian" in error_message.lower():
        return f"""
        ⏱️ **Quá thời gian xử lý**
        
        {error_message}
        
        **Giải pháp:**
        - Thử lại với ảnh có kích thước nhỏ hơn
        - Chọn ít bộ lọc hơn
        - Kiểm tra hiệu suất máy chủ
        """
    else:
        return f"""
        ❌ **Lỗi**
        
        {error_message}
        
        Vui lòng thử lại hoặc liên hệ hỗ trợ.
        """
