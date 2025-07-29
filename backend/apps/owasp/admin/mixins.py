from django.contrib import admin, messages
from django.utils.safestring import mark_safe


class GenericEntityAdminMixin:
    """Mixin for generic entity admin."""

    def get_queryset(self, request):
        """Get queryset."""
        return super().get_queryset(request).prefetch_related("repositories")

    def custom_field_github_urls(self, obj):
        """Entity GitHub URLs."""
        if not hasattr(obj, "repositories"):
            return mark_safe(  # noqa: S308
                f"<a href='https://github.com/{obj.owasp_repository.owner.login}/"
                f"{obj.owasp_repository.key}' target='_blank'>↗️</a>"
            )

        urls = [
            f"<a href='https://github.com/{repository.owner.login}/"
            f"{repository.key}' target='_blank'>↗️</a>"
            for repository in obj.repositories.all()
        ]

        return mark_safe(" ".join(urls))  # noqa: S308

    def custom_field_owasp_url(self, obj):
        """Entity OWASP URL."""
        return mark_safe(  # noqa: S308
            f"<a href='https://owasp.org/{obj.key}' target='_blank'>↗️</a>"
        )

    custom_field_github_urls.short_description = "GitHub 🔗"
    custom_field_owasp_url.short_description = "OWASP 🔗"


class LeaderAdminMixin:
    """Admin mixin for entities that can have leaders."""

    actions = ("approve_suggested_leaders",)
    filter_horizontal = (
        "leaders",
        "suggested_leaders",
    )

    def approve_suggested_leaders(self, request, queryset):
        """Approve suggested leaders for selected entities."""
        for entity in queryset:
            suggestions = entity.suggested_leaders.all()
            entity.leaders.add(*suggestions)
            self.message_user(
                request,
                f"Approved {suggestions.count()} leader suggestions for {entity.name}",
                messages.SUCCESS,
            )

    approve_suggested_leaders.short_description = "Approve suggested leaders"
