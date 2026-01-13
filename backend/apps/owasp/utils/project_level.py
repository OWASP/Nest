"""Utilities for mapping OWASP official project levels to Nest ProjectLevel enum."""

from decimal import Decimal, InvalidOperation
from typing import cast

from apps.owasp.models.enums.project import ProjectLevel

LEVEL_MAP = {
    Decimal(4): ProjectLevel.FLAGSHIP,
    Decimal("3.5"): ProjectLevel.FLAGSHIP,
    Decimal(3): ProjectLevel.PRODUCTION,
    Decimal(2): ProjectLevel.INCUBATOR,
    Decimal(1): ProjectLevel.LAB,
    Decimal(0): ProjectLevel.OTHER,
}


def map_level(level: Decimal) -> ProjectLevel | None:
    """Map OWASP official numeric level to Nest ProjectLevel."""
    try:
        parsed_level = Decimal(str(level))
    except (InvalidOperation, TypeError, ValueError):
        return None

    if parsed_level < 0:
        return None

    return cast("ProjectLevel | None", LEVEL_MAP.get(parsed_level))
