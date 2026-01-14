"""
Utilities for mapping OWASP official numeric project levels
to internal ProjectLevel enum values.

This module acts as a translation layer between the OWASP
project level definitions published upstream and the
Nest internal project classification system.
"""

from decimal import Decimal, InvalidOperation
from typing import cast

from apps.owasp.models.enums.project import ProjectLevel


_LEVEL_MAP = {
    Decimal(4): ProjectLevel.FLAGSHIP,
    Decimal("3.5"): ProjectLevel.FLAGSHIP,
    Decimal(3): ProjectLevel.PRODUCTION,
    Decimal(2): ProjectLevel.INCUBATOR,
    Decimal(1): ProjectLevel.LAB,
    Decimal(0): ProjectLevel.OTHER,
}


def map_level(level: Decimal) -> ProjectLevel | None:
    """Map an OWASP official numeric project level to ProjectLevel.

    Args:
        level (Decimal): The numeric project level provided by OWASP.

    Returns:
        ProjectLevel | None: The mapped ProjectLevel value if valid,
        otherwise None for unsupported or invalid levels.
    """
    try:
        parsed_level = Decimal(str(level))
    except (InvalidOperation, TypeError, ValueError):
        return None

    if parsed_level < 0:
        return None

    return cast(ProjectLevel | None, _LEVEL_MAP.get(parsed_level))
