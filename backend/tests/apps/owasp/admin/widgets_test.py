"""Tests for OWASP admin widgets."""

from apps.owasp.admin.widgets import ChannelIdWidget


class TestChannelIdWidget:
    def test_init_sets_custom_attributes(self):
        widget = ChannelIdWidget()

        assert widget.attrs["class"] == "vForeignKeyRawIdAdminField"
        assert widget.attrs["placeholder"] == "Channel ID"

    def test_render_includes_input_field(self):
        widget = ChannelIdWidget()

        result = widget.render("channel_id", "C123456", attrs=None)

        assert "channel_id" in result
        assert "C123456" in result

    def test_render_includes_search_button(self):
        widget = ChannelIdWidget()

        result = widget.render("channel_id", "C123456", attrs=None)

        assert "related-lookup" in result
        assert "/a/slack/conversation/" in result
        assert "lookup_id_channel_id" in result
        assert "Look up related objects" in result

    def test_render_with_none_value(self):
        widget = ChannelIdWidget()

        result = widget.render("channel_id", None, attrs=None)

        assert "channel_id" in result
        assert "related-lookup" in result

    def test_render_with_custom_attrs(self):
        widget = ChannelIdWidget()

        result = widget.render("channel_id", "C123", attrs={"data-test": "value"})

        assert "channel_id" in result
        assert "related-lookup" in result
