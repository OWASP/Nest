"""OWASP admin mixins for common functionality."""

from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape
from django.utils.safestring import mark_safe

from apps.owasp.admin.widgets import ChannelIdWidget
from apps.owasp.models.entity_channel import EntityChannel
from apps.owasp.models.entity_member import EntityMember
from apps.slack.models.conversation import Conversation


class BaseOwaspAdminMixin:
    """Base mixin for OWASP admin classes providing common patterns."""

    # Common configuration patterns.
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
        """Build the standard list display configuration for OWASP entities.

        Args:
            *additional_fields: Field names to add to base list display.

        Returns:
            tuple: Complete list_display configuration.

        """
        base = ("name",) if hasattr(self.model, "name") else ()
        return base + tuple(additional_fields) + self.list_display_field_names

    def get_base_search_fields(self, *additional_fields):
        """Build the standard search configuration for OWASP entities.

        Args:
            *additional_fields: Field names to add to base search fields.

        Returns:
            tuple: Complete search_fields configuration.

        """
        return self.search_field_names + additional_fields


class EntityMemberInline(GenericTabularInline):
    """EntityMember inline for admin."""

    ct_field = "entity_type"
    ct_fk_field = "entity_id"
    extra = 1
    fields = (
        "member_name",
        "member_email",
        "member",
        "role",
        "description",
        "order",
        "is_active",
        "is_reviewed",
    )
    model = EntityMember
    ordering = (
        "order",
        "member__login",
    )
    raw_id_fields = ("member",)


class EntityChannelInline(GenericTabularInline):
    """EntityChannel inline for admin."""

    ct_field = "entity_type"
    ct_fk_field = "entity_id"
    extra = 1
    fields = (
        "channel_type",
        "channel_id",
        "platform",
        "is_default",
        "is_active",
        "is_reviewed",
    )
    model = EntityChannel
    ordering = ("platform", "channel_id")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Customize form fields for EntityChannel inline entries.

        Args:
            db_field (Field): The database field being rendered.
            request (HttpRequest): The current admin request.
            **kwargs: Additional keyword arguments.

        Returns:
            FormField: The customized form field.

        """
        if db_field.name == "channel_id":
            kwargs["widget"] = ChannelIdWidget()
        elif db_field.name == "channel_type":
            # Limit channel_type to only Conversation (Slack channels)
            conversation_ct = ContentType.objects.get_for_model(Conversation)
            kwargs["queryset"] = ContentType.objects.filter(id=conversation_ct.id)
            kwargs["initial"] = conversation_ct

        return super().formfield_for_dbfield(db_field, request, **kwargs)


class GenericEntityAdminMixin(BaseOwaspAdminMixin):
    """Mixin for generic entity admin with common entity functionality."""

    def get_queryset(self, request):
        """Return the queryset for entities with repository relationships.

        Args:
            request (HttpRequest): The current admin request.

        Returns:
            QuerySet: QuerySet with related repositories prefetched.

        """
        return super().get_queryset(request).prefetch_related("repositories")

    def custom_field_github_urls(self, obj):
        """Display GitHub repository links for the entity."""
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
        """Display the entity's OWASP website."""
        if not hasattr(obj, "key") or not obj.key:
            return ""

        return mark_safe(  # noqa: S308
            f"<a href='https://owasp.org/{escape(obj.key)}' target='_blank'>↗️</a>"
        )

    def _format_github_link(self, repository):
        """Return a formatted HTML link to a GitHub repository.

        Args:
            repository (Repository): The repository instance.

        Returns:
            str: HTML link or empty string if repository data is incomplete.

        """
        if not repository or not hasattr(repository, "owner") or not repository.owner:
            return ""
        if not hasattr(repository.owner, "login") or not repository.owner.login:
            return ""
        if not hasattr(repository, "key") or not repository.key:
            return ""

        return mark_safe(  # noqa: S308
            f"<a href='https://github.com/{escape(repository.owner.login)}/"
            f"{escape(repository.key)}' target='_blank'>↗️</a>"
        )

    custom_field_github_urls.short_description = "GitHub 🔗"
    custom_field_owasp_url.short_description = "OWASP 🔗"


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
