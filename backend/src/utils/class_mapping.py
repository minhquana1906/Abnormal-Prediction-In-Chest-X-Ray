"""
Utility functions for loading and accessing disease class mappings.

This module provides functions to load the English-Vietnamese class mapping
from the configuration file and translate between languages.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

from backend.src.config.settings import CLASS_MAPPING_PATH
from backend.src.utils.logging_config import logger


# Cache for loaded mappings
_class_mapping_cache: Optional[Dict[str, str]] = None
_reverse_mapping_cache: Optional[Dict[str, str]] = None


def load_class_mapping() -> Dict[str, str]:
    """
    Load disease class mapping from JSON configuration file.

    Returns:
        Dictionary mapping English class names to Vietnamese names

    Raises:
        FileNotFoundError: If mapping file doesn't exist
        json.JSONDecodeError: If mapping file is invalid JSON
    """
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
    """
    Get Vietnamese name for an English disease class name.

    Args:
        english_name: English disease class name

    Returns:
        Vietnamese translation, or the original English name if not found
    """
    mapping = load_class_mapping()

    vietnamese_name = mapping.get(english_name)

    if vietnamese_name is None:
        logger.warning(f"No Vietnamese translation found for: {english_name}")
        return english_name

    return vietnamese_name


def get_english_name(vietnamese_name: str) -> str:
    """
    Get English name for a Vietnamese disease class name.

    Args:
        vietnamese_name: Vietnamese disease class name

    Returns:
        English translation, or the original Vietnamese name if not found
    """
    global _reverse_mapping_cache

    # Build reverse mapping cache if not available
    if _reverse_mapping_cache is None:
        mapping = load_class_mapping()
        _reverse_mapping_cache = {v: k for k, v in mapping.items()}

    english_name = _reverse_mapping_cache.get(vietnamese_name)

    if english_name is None:
        logger.warning(f"No English translation found for: {vietnamese_name}")
        return vietnamese_name

    return english_name


def get_all_class_names() -> Dict[str, str]:
    """
    Get all disease class names (English -> Vietnamese mapping).

    Returns:
        Dictionary of all class mappings
    """
    return load_class_mapping()


def get_class_list_english() -> List[str]:
    """
    Get list of all English disease class names.

    Returns:
        List of English class names
    """
    mapping = load_class_mapping()
    return list(mapping.keys())


def get_class_list_vietnamese() -> List[str]:
    """
    Get list of all Vietnamese disease class names.

    Returns:
        List of Vietnamese class names
    """
    mapping = load_class_mapping()
    return list(mapping.values())


def get_class_count() -> int:
    """
    Get total number of disease classes (abnormality classes only).

    Returns:
        Number of classes
    """
    mapping = load_class_mapping()
    return len(mapping)


def reload_class_mapping() -> Dict[str, str]:
    """
    Force reload of class mapping from file (clears cache).

    Returns:
        Reloaded class mapping dictionary
    """
    global _class_mapping_cache, _reverse_mapping_cache

    # Clear caches
    _class_mapping_cache = None
    _reverse_mapping_cache = None

    logger.info("Reloading class mapping from file")

    return load_class_mapping()


def validate_class_name(class_name: str) -> bool:
    """
    Validate if a class name exists in the mapping (English or Vietnamese).

    Args:
        class_name: Class name to validate

    Returns:
        True if class name is valid
    """
    mapping = load_class_mapping()

    # Check if it's an English name
    if class_name in mapping:
        return True

    # Check if it's a Vietnamese name
    if class_name in mapping.values():
        return True

    return False


def format_class_name_for_display(
    class_name: str, include_english: bool = False
) -> str:
    """
    Format class name for display (Vietnamese primary, optionally include English).

    Args:
        class_name: Class name (English or Vietnamese)
        include_english: Whether to include English name in parentheses

    Returns:
        Formatted display string
    """
    # Check if input is English or Vietnamese
    mapping = load_class_mapping()

    if class_name in mapping:
        # Input is English
        vietnamese = mapping[class_name]
        if include_english:
            return f"{vietnamese} ({class_name})"
        return vietnamese
    elif class_name in mapping.values():
        # Input is Vietnamese
        if include_english:
            english = get_english_name(class_name)
            return f"{class_name} ({english})"
        return class_name
    else:
        # Unknown class
        logger.warning(f"Unknown class name for display: {class_name}")
        return class_name
