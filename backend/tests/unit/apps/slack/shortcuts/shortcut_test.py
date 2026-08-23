"""Tests for Slack ShortcutBase registration."""

from unittest.mock import Mock

from apps.slack.modals.report import (
    REPORT_CONTENT_CALLBACK_ID,
    REPORT_CONTENT_VIEW_CALLBACK_ID,
)
from apps.slack.shortcuts.report_content import ReportContent
from apps.slack.shortcuts.shortcut import ShortcutBase


class TestShortcutBase:
    def test_get_shortcuts_includes_report_content(self):
        """Test ReportContent is discovered as a ShortcutBase subclass."""
        assert ReportContent in ShortcutBase.get_shortcuts()

    def test_register_binds_shortcut_and_view(self, mocker):
        """Test register wires both the shortcut and modal view callbacks."""
        app = Mock()
        shortcut_decorator = Mock(side_effect=lambda handler: handler)
        view_decorator = Mock(side_effect=lambda handler: handler)
        app.shortcut.return_value = shortcut_decorator
        app.view.return_value = view_decorator
        mocker.patch("apps.slack.shortcuts.shortcut.SlackConfig.app", app)

        shortcut = ReportContent()
        shortcut.register()

        app.shortcut.assert_called_once_with(REPORT_CONTENT_CALLBACK_ID)
        shortcut_decorator.assert_called_once_with(shortcut.handle)
        app.view.assert_called_once_with(REPORT_CONTENT_VIEW_CALLBACK_ID)
        view_decorator.assert_called_once_with(shortcut.handle_view)
