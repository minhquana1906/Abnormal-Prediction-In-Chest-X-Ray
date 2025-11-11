import json
from typing import Dict, Optional, Tuple
from pathlib import Path

from backend.src.config.settings import HEALTH_INFO_PATH
from backend.src.utils.logging_config import logger


_health_info_cache: Optional[Dict[str, Dict[str, str]]] = None


def load_health_info() -> Dict[str, Dict[str, str]]:

    global _health_info_cache

    # Return cached info if available
    if _health_info_cache is not None:
        return _health_info_cache

    # Load from file
    try:
        with open(HEALTH_INFO_PATH, "r", encoding="utf-8") as f:
            health_info = json.load(f)

        logger.info(
            f"Loaded health information for {len(health_info)} classes from {HEALTH_INFO_PATH}"
        )

        # Cache the health info
        _health_info_cache = health_info

        return health_info

    except FileNotFoundError:
        logger.error(f"Health info file not found: {HEALTH_INFO_PATH}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in health info file: {e}")
        raise


def get_health_info(class_name: str) -> Optional[Dict[str, str]]:

    health_info = load_health_info()

    info = health_info.get(class_name)

    if info is None:
        logger.warning(f"No health information found for class: {class_name}")

    return info


def get_description(class_name: str) -> str:

    info = get_health_info(class_name)

    if info is None:
        return ""

    return info.get("description", "")


def get_warning(class_name: str) -> str:

    info = get_health_info(class_name)

    if info is None:
        return ""

    return info.get("warning", "")


def get_description_and_warning(class_name: str) -> Tuple[str, str]:

    info = get_health_info(class_name)

    if info is None:
        return ("", "")

    description = info.get("description", "")
    warning = info.get("warning", "")

    return (description, warning)


def get_all_health_info() -> Dict[str, Dict[str, str]]:

    return load_health_info()


def has_health_info(class_name: str) -> bool:

    health_info = load_health_info()
    return class_name in health_info


def reload_health_info() -> Dict[str, Dict[str, str]]:

    global _health_info_cache

    # Clear cache
    _health_info_cache = None

    logger.info("Reloading health information from file")

    return load_health_info()


def format_health_info_for_display(class_name: str) -> str:

    description, warning = get_description_and_warning(class_name)

    if not description and not warning:
        return "Không có thông tin sức khỏe cho tình trạng này."

    formatted = ""

    if description:
        formatted += description + "\n\n"

    if warning:
        formatted += warning

    return formatted.strip()


def get_severity_emoji(class_name: str) -> str:

    warning = get_warning(class_name)

    # Check warning severity
    if "KHẨN CẤP" in warning:
        return "🚨"  # Emergency
    elif "quan trọng" in warning.lower():
        return "⚠️"  # Important warning
    else:
        return "ℹ️"  # Info


def is_emergency_condition(class_name: str) -> bool:

    warning = get_warning(class_name)
    return "KHẨN CẤP" in warning


def get_recommended_action(class_name: str) -> str:

    warning = get_warning(class_name)

    # Emergency conditions
    if is_emergency_condition(class_name):
        return "ĐẾN PHÒNG CẤP CỨU NGAY hoặc gọi 115"

    # Other conditions - extract action from warning
    if "đến bệnh viện ngay" in warning.lower():
        return "Đến bệnh viện ngay"
    elif "liên hệ bác sĩ" in warning.lower():
        return "Liên hệ bác sĩ để được tư vấn"
    elif "thăm khám" in warning.lower():
        return "Đặt lịch khám với bác sĩ"
    else:
        return "Tham khảo ý kiến bác sĩ"


def get_health_info_summary(class_name: str) -> Dict[str, str]:

    description, warning = get_description_and_warning(class_name)

    return {
        "class_name": class_name,
        "description": description,
        "warning": warning,
        "severity_emoji": get_severity_emoji(class_name),
        "is_emergency": is_emergency_condition(class_name),
        "recommended_action": get_recommended_action(class_name),
    }
