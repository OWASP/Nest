"""OWASP admin mixins for common functionality."""

from django.contrib import messages
from django.utils.safestring import mark_safe


class BaseOwaspAdminMixin:
    """Base mixin for OWASP admin classes providing common patterns."""

    # Common configuration patterns
    list_display_field_names = (
        "created_at",
        "updated_at",
    )
    list_filter_field_names = ("is_active",)
    search_field_names = (
        "name",
        "key",
    )

    def get_base_list_display(self, *additional_fields):
        """Get base list display with additional fields."""
        return tuple(
            ("name",) if hasattr(self.model, "name") else (),
            *additional_fields,
            *self.list_display_field_names,
        )

    def get_base_search_fields(self, *additional_fields):
        """Get base search fields with additional fields."""
        return self.search_field_names + additional_fields


class GenericEntityAdminMixin(BaseOwaspAdminMixin):
    """Mixin for generic entity admin with common entity functionality."""

    def get_queryset(self, request):
        """Get queryset with optimized relations."""
        return super().get_queryset(request).prefetch_related("repositories")

    def custom_field_github_urls(self, obj):
        """Entity GitHub URLs with uniform formatting."""
        if not hasattr(obj, "repositories"):
            if not hasattr(obj, "owasp_repository") or not obj.owasp_repository:
                return ""
            return self._format_github_link(obj.owasp_repository)

        return mark_safe(  # noqa: S308
            " ".join(
                [self._format_github_link(repository) for repository in obj.repositories.all()]
            )
        )

    def custom_field_owasp_url(self, obj):
        """Entity OWASP URL with uniform formatting."""
        if not hasattr(obj, "key") or not obj.key:
            return ""

        return mark_safe(  # noqa: S308
            f"<a href='https://owasp.org/{obj.key}' target='_blank'>↗️</a>"
        )

    def _format_github_link(self, repository):
        """Format a single GitHub repository link."""
        if not repository or not hasattr(repository, "owner") or not repository.owner:
            return ""
        if not hasattr(repository.owner, "login") or not repository.owner.login:
            return ""
        if not hasattr(repository, "key") or not repository.key:
            return ""

        return mark_safe(  # noqa: S308
            f"<a href='https://github.com/{repository.owner.login}/"
            f"{repository.key}' target='_blank'>↗️</a>"
        )

    custom_field_github_urls.short_description = "GitHub 🔗"
    custom_field_owasp_url.short_description = "OWASP 🔗"


class LeaderAdminMixin(BaseOwaspAdminMixin):
    """Admin mixin for entities that can have leaders."""

    actions = ("approve_suggested_leaders",)
    filter_horizontal = (
        "leaders",
        "suggested_leaders",
    )

    def approve_suggested_leaders(self, request, queryset):
        """Approve suggested leaders for selected entities."""
        total_approved = 0
        for entity in queryset:
            suggestions = entity.suggested_leaders.all()
            if count := suggestions.count():
                entity.leaders.add(*suggestions)
                total_approved += count
                entity_name = entity.name if hasattr(entity, "name") else str(entity)
                self.message_user(
                    request,
                    f"Approved {count} leader suggestions for {entity_name}",
                    messages.SUCCESS,
                )

        if total_approved:
            self.message_user(
                request,
                f"Total approved suggestions: {total_approved}",
                messages.INFO,
            )

    approve_suggested_leaders.short_description = "Approve suggested leaders"


class StandardOwaspAdminMixin(BaseOwaspAdminMixin):
    """Standard mixin for simple OWASP admin classes."""

    def get_common_config(
        self, extra_list_display=None, extra_search_fields=None, extra_list_filters=None
    ):
        """Get common admin configuration to reduce boilerplate."""
        config = {}

        if extra_list_display:
            config["list_display"] = self.get_base_list_display(*extra_list_display)

        if extra_search_fields:
            config["search_fields"] = self.get_base_search_fields(*extra_search_fields)

        if extra_list_filters:
            config["list_filter"] = self.list_filter_field_names + extra_list_filters

        return config
