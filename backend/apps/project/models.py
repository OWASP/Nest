"""Project app models."""

from apps.common.models import TimestampedModel


class Project(TimestampedModel):
    """Project model."""

    # name = models.CharField(name="Name", max_length=100, unique=True)  # noqa: ERA001
    # description = models.TextField(name="Description", max_length=500) # noqa: ERA001
