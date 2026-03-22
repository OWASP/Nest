"""Mentorship app config."""

from django.apps import AppConfig


class MentorshipConfig(AppConfig):
    """Mentorship app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.mentorship"

    def ready(self):
        """Ready."""
        import apps.mentorship.signals  # noqa: F401, PLC0415
