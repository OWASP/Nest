"""Utilities for mapping OWASP official project levels to Nest ProjectLevel enum."""

from decimal import Decimal
from typing import Optional

from apps.owasp.models.enums.project import ProjectLevel

# OWASP numeric level -> Nest ProjectLevel
LEVEL_MAP = {
    Decimal("4"): ProjectLevel.FLAGSHIP,
    Decimal("3.5"): ProjectLevel.FLAGSHIP,
    Decimal("3"): ProjectLevel.PRODUCTION,
    Decimal("2"): ProjectLevel.INCUBATOR,
    Decimal("1"): ProjectLevel.LAB,
    Decimal("0"): ProjectLevel.OTHER,
}

def map_level(level: Decimal) -> Optional[ProjectLevel]:
    """Map OWASP official numeric level to Nest ProjectLevel."""

    try:
        level = Decimal(level)
    except Exception:
        return None

    if level < 0:
        return None
    
    return LEVEL_MAP.get(level)