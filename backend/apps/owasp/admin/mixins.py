"""OWASP admin mixins for common functionality."""

from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
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
        """Get base list display with additional fields."""
        return tuple(
            ("name",) if hasattr(self.model, "name") else (),
            *additional_fields,
            *self.list_display_field_names,
        )

    def get_base_search_fields(self, *additional_fields):
        """Get base search fields with additional fields."""
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
        """Override to add custom widget for channel_id field and limit channel_type options."""
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
        """Get queryset with optimized relations."""
        return super().get_queryset(request).prefetch_related("repositories")

    def custom_field_github_urls(self, obj):
        """Entity GitHub URLs with uniform formatting."""
        if not hasattr(obj, "repositories"):
            if not hasattr(obj, "owasp_repository") or not obj.owasp_repository:
                return ""
            return self._format_github_link(obj.owasp_repository)

        links = [self._format_github_link(repository) for repository in obj.repositories.all()]
        # Use mark_safe since links are already safely formatted HTML from format_html
        return mark_safe(  # noqa: S308  # NOSEMGREP: python.django.security.audit.avoid-mark-safe.avoid-mark-safe
            " ".join(links)
        )

    def custom_field_owasp_url(self, obj):
        """Entity OWASP URL with uniform formatting."""
        if not hasattr(obj, "key") or not obj.key:
            return ""

        return format_html("<a href='https://owasp.org/{}' target='_blank'>↗️</a>", obj.key)

    def _format_github_link(self, repository):
        """Format a single GitHub repository link."""
        if not repository or not hasattr(repository, "owner") or not repository.owner:
            return ""
        if not hasattr(repository.owner, "login") or not repository.owner.login:
            return ""
        if not hasattr(repository, "key") or not repository.key:
            return ""

        return format_html(
            "<a href='https://github.com/{}/{}' target='_blank'>↗️</a>",
            repository.owner.login,
            repository.key,
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
