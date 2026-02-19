"""Django settings configuration for generating backend model graphs."""

from .local import Local


class Graphs(Local):
    """Settings configuration used for model graph generation."""

    @classmethod
    def setup(cls):
        """Extend INSTALLED_APPS to include django_extensions."""
        super().setup()

        if "django_extensions" not in cls.INSTALLED_APPS:
            cls.INSTALLED_APPS = (*cls.INSTALLED_APPS, "django_extensions")
