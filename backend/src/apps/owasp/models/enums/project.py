"""Enums for OWASP projects."""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import TextChoices


class AudienceChoices(models.TextChoices):
    """Enum for OWASP project audience."""

    BREAKER = "breaker", "Breaker"
    BUILDER = "builder", "Builder"
    DEFENDER = "defender", "Defender"


class ProjectType(TextChoices):
    """Enum for OWASP project types."""

    # These projects provide tools, libraries, and frameworks that can be leveraged by
    # developers to enhance the security of their applications.
    CODE = "code", "Code"

    # These projects seek to communicate information or raise awareness about a topic in
    # application security. Note that documentation projects should focus on an online-first
    # deliverable, where appropriate, but can take any media form.
    DOCUMENTATION = "documentation", "Documentation"

    # Some projects fall outside the above categories. Most are created to offer OWASP
    # operational support.
    OTHER = "other", "Other"

    # These are typically software or utilities that help developers and security
    # professionals test, secure, or monitor applications.
    TOOL = "tool", "Tool"


class ProjectLevel(TextChoices):
    """Enum for OWASP project levels."""

    OTHER = "other", "Other"
    INCUBATOR = "incubator", "Incubator"
    LAB = "lab", "Lab"
    PRODUCTION = "production", "Production"
    FLAGSHIP = "flagship", "Flagship"


def validate_audience(value):
    """Audience validator."""
    if not isinstance(value, list):
        error_message = "Audience must be a list."
        raise ValidationError(error_message)

    valid_choices = {choice.value for choice in AudienceChoices}
    if invalid_values := [v for v in value if v not in valid_choices]:
        error_message = f"Invalid audience keywords: {invalid_values}"
        raise ValidationError(error_message)
