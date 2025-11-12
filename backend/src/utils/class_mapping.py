import json
from typing import Dict, List, Optional
from pathlib import Path

from backend.src.config.settings import CLASS_MAPPING_PATH
from backend.src.utils.logging_config import logger


_class_mapping_cache: Optional[Dict[str, str]] = None
_reverse_mapping_cache: Optional[Dict[str, str]] = None


def load_class_mapping() -> Dict[str, str]:

    global _class_mapping_cache

    # Return cached mapping if available
    if _class_mapping_cache is not None:
        return _class_mapping_cache

    # Load from file
    try:
        with open(CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
            mapping = json.load(f)

        logger.info(
            f"Loaded class mapping with {len(mapping)} classes from {CLASS_MAPPING_PATH}"
        )

        # Cache the mapping
        _class_mapping_cache = mapping

        return mapping

    except FileNotFoundError:
        logger.error(f"Class mapping file not found: {CLASS_MAPPING_PATH}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in class mapping file: {e}")
        raise


def get_vietnamese_name(english_name: str) -> str:

    mapping = load_class_mapping()

    vietnamese_name = mapping.get(english_name)

    if vietnamese_name is None:
        logger.warning(f"No Vietnamese translation found for: {english_name}")
        return english_name

    return vietnamese_name
