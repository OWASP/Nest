"""Common schemas and filters for the API."""

from ninja import Field, FilterSchema, Schema


class Leader(Schema):
    """Schema for Leader."""

    key: str | None = None
    name: str


class ValidationErrorSchema(Schema):
    """Schema for validation error."""

    message: str
    errors: list[dict] | dict | None = None


class LocationFilter(FilterSchema):
    """Filter for Location."""

    latitude_gte: float | None = Field(
        None, description="Latitude greater than or equal to", q="latitude__gte"
    )
    latitude_lte: float | None = Field(
        None, description="Latitude less than or equal to", q="latitude__lte"
    )
    longitude_gte: float | None = Field(
        None, description="Longitude greater than or equal to", q="longitude__gte"
    )
    longitude_lte: float | None = Field(
        None, description="Longitude less than or equal to", q="longitude__lte"
    )
