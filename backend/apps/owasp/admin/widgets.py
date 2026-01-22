"""Custom widgets for OWASP admin."""

from django import forms
from django.utils.html import format_html


class ChannelIdWidget(forms.TextInput):
    """Custom widget for channel_id with search functionality."""

    def __init__(self, *args, **kwargs):
        """Initialize the widget with custom attributes."""
        super().__init__(*args, **kwargs)
        self.attrs.update({"class": "vForeignKeyRawIdAdminField", "placeholder": "Channel ID"})

    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget with a search button."""
        widget_html = super().render(name, value, attrs, renderer)

        search_button = (
            "<a href='/a/slack/conversation/' class='related-lookup'"
            f"id='lookup_id_{name}' title='Look up related objects'></a>"
        )

        return format_html("{}{}", widget_html, search_button)
