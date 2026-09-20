from apps.slack.apps import SlackConfig
from apps.slack.shortcuts.shortcut import ShortcutBase

from . import report_content

if SlackConfig.app:
    ShortcutBase.configure_shortcuts()
