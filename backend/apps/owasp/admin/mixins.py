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
        """Build base list display tuple with additional fields.

        Args:
            *additional_fields: Extra field names to include in list display.

        Returns:
            tuple: Base display fields (name, timestamps) plus additional fields.

        """
        return tuple(
            ("name",) if hasattr(self.model, "name") else (),
            *additional_fields,
            *self.list_display_field_names,
        )

    def get_base_search_fields(self, *additional_fields):
        """Build base search fields tuple with additional fields.

        Args:
            *additional_fields: Extra field names to include in search.

        Returns:
            tuple: Base search fields (name, key) plus additional fields.

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
        """Customize form fields for EntityChannel inline editing.

        Adds a custom widget for channel_id field and limits channel_type options
        to only Conversation (Slack channels).

        Args:
            db_field: The database field being customized.
            request: The HTTP request object.
            **kwargs: Additional keyword arguments passed to parent.

        Returns:
            Field: The customized form field.

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
        """Retrieve optimized queryset with prefetched repositories.

        Args:
            request: The HTTP request object.

        Returns:
            QuerySet: Queryset with prefetched repositories for efficient display.

        """
        return super().get_queryset(request).prefetch_related("repositories")

    def custom_field_github_urls(self, obj):
        """Display entity GitHub repository links in admin list view.

        Args:
            obj: The entity object with repositories.

        Returns:
            str: HTML-formatted links to GitHub repositories.

        """
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
        """Display entity OWASP website link in admin list view.

        Args:
            obj: The entity object with a key attribute.

        Returns:
            str: HTML-formatted link to OWASP website or empty string.

        """
        if not hasattr(obj, "key") or not obj.key:
            return ""

        return format_html("<a href='https://owasp.org/{}' target='_blank'>↗️</a>", obj.key)

    def _format_github_link(self, repository):
        """Format a GitHub repository link as HTML.

        Args:
            repository: The repository object with owner and key attributes.

        Returns:
            str: HTML-formatted link to GitHub repository or empty string if invalid.

        """
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
        """Build common admin configuration dictionary.

        Reduces boilerplate by merging base fields with custom additions.

        Args:
            extra_list_display: Additional fields to display in list view.
            extra_search_fields: Additional fields to include in search.
            extra_list_filters: Additional fields to use for filtering.

        Returns:
            dict: Configuration dictionary with list_display, search_fields, and list_filter.

        """
        config = {}

        if extra_list_display:
            config["list_display"] = self.get_base_list_display(*extra_list_display)

        if extra_search_fields:
            config["search_fields"] = self.get_base_search_fields(*extra_search_fields)

        if extra_list_filters:
            config["list_filter"] = self.list_filter_field_names + extra_list_filters

        return config
