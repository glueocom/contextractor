"""Utility functions for contextractor-engine."""

import re
from typing import Any


def normalize_config_keys(config: dict[str, Any]) -> dict[str, Any]:
    """Normalize config dictionary keys to snake_case.

    Accepts both camelCase (JSON/API convention) and snake_case (Python convention).
    Auto-detects the format and converts camelCase to snake_case.
    Keys already in snake_case are left unchanged.

    Examples:
        {"favorPrecision": True} -> {"favor_precision": True}
        {"favor_precision": True} -> {"favor_precision": True}
        {"includeLinks": True, "fast": False} -> {"include_links": True, "fast": False}

    Args:
        config: Dictionary with config keys in either camelCase or snake_case.

    Returns:
        Dictionary with all keys normalized to snake_case.
    """
    if not config:
        return {}

    def to_snake_case(key: str) -> str:
        """Convert camelCase to snake_case. Leave snake_case unchanged."""
        # If already contains underscore, assume it's snake_case
        if "_" in key:
            return key
        # Convert camelCase to snake_case
        # Insert underscore before uppercase letters and lowercase them
        return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()

    return {to_snake_case(k): v for k, v in config.items()}
