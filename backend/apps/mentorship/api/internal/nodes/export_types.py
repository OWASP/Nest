"""GraphQL types for export functionality."""

import strawberry


@strawberry.enum
class ExportFormatEnum(strawberry.Enum):
    """Supported export formats for issue data."""

    CSV = "csv"
    JSON = "json"


@strawberry.type
class ExportResult:
    """Result of an export operation containing the file content and metadata."""

    content: str
    filename: str
    mime_type: str
    count: int
