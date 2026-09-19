"""Tests for Slack ShortcutBase registration."""

from unittest.mock import Mock

import pytest

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

    def test_configure_shortcuts_when_app_none(self, mocker):
        """Test configure_shortcuts is a no-op when SlackConfig.app is unset."""
        mocker.patch("apps.slack.shortcuts.shortcut.SlackConfig.app", None)
        warning = mocker.patch("apps.slack.shortcuts.shortcut.logger.warning")
        register = mocker.patch.object(ReportContent, "register")

        ShortcutBase.configure_shortcuts()

        warning.assert_called_once()
        register.assert_not_called()

    def test_configure_shortcuts_registers_discovered(self, mocker):
        """Test configure_shortcuts registers each discovered shortcut class."""
        mocker.patch("apps.slack.shortcuts.shortcut.SlackConfig.app", Mock())
        instance = Mock()
        shortcut_cls = Mock(return_value=instance)
        mocker.patch.object(ShortcutBase, "get_shortcuts", return_value=[shortcut_cls])

        ShortcutBase.configure_shortcuts()

        shortcut_cls.assert_called_once_with()
        instance.register.assert_called_once_with()

    def test_handle_not_implemented(self):
        """Test base handle must be overridden by subclasses."""
        with pytest.raises(NotImplementedError):
            ShortcutBase().handle(Mock(), {}, Mock(), Mock())

    def test_handle_view_not_implemented(self):
        """Test base handle_view must be overridden by subclasses."""
        with pytest.raises(NotImplementedError):
            ShortcutBase().handle_view(Mock(), {}, Mock())

    def test_register_when_app_none(self, mocker):
        """Test register is a no-op when SlackConfig.app is unset."""
        mocker.patch("apps.slack.shortcuts.shortcut.SlackConfig.app", None)

        ReportContent().register()

    def test_register_without_view_callback(self, mocker):
        """Test register skips view binding when view_callback_id is unset."""

        class PlainShortcut(ShortcutBase):
            callback_id = "plain_shortcut"

        app = Mock()
        shortcut_decorator = Mock(side_effect=lambda handler: handler)
        app.shortcut.return_value = shortcut_decorator
        mocker.patch("apps.slack.shortcuts.shortcut.SlackConfig.app", app)

        shortcut = PlainShortcut()
        shortcut.register()

        app.shortcut.assert_called_once_with("plain_shortcut")
        shortcut_decorator.assert_called_once_with(shortcut.handle)
        app.view.assert_not_called()

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
