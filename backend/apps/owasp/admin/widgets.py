"""Custom widgets for OWASP admin."""

from django import forms
from django.utils.safestring import mark_safe


class ChannelIdWidget(forms.TextInput):
    """Custom widget for channel_id with search functionality."""

    def __init__(self, *args, **kwargs):
        """Initialize the ChannelIdWidget.

        Sets up custom CSS classes and placeholder text for the text input field.

        Args:
            *args: Positional arguments passed to parent TextInput.
            **kwargs: Keyword arguments passed to parent TextInput.

        """
        super().__init__(*args, **kwargs)
        self.attrs.update({"class": "vForeignKeyRawIdAdminField", "placeholder": "Channel ID"})

    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget with a search button.

        Displays the text input field alongside a lookup button for selecting
        related Slack conversation objects.

        Args:
            name: The HTML field name.
            value: The current field value.
            attrs: Optional HTML attributes for the widget.
            renderer: Optional form renderer instance.

        Returns:
            str: HTML markup for the widget and search button.

        """
        widget_html = super().render(name, value, attrs, renderer)

        search_button = (
            "<a href='/a/slack/conversation/' class='related-lookup'"
            f"id='lookup_id_{name}' title='Look up related objects'></a>"
        )

        # Use mark_safe since both widget_html and search_button are already HTML
        return mark_safe(  # noqa: S308  # NOSEMGREP: python.django.security.audit.avoid-mark-safe.avoid-mark-safe
            f"{widget_html} {search_button}"
        )
