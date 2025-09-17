from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase

from . import (
    board,
    cancel_reminder,
    chapters,
    committees,
    community,
    contact,
    contribute,
    donate,
    events,
    google_sign_in,
    gsoc,
    jobs,
    leaders,
    news,
    owasp,
    policies,
    projects,
    set_reminder,
    sponsor,
    sponsors,
    staff,
    users,
)

if SlackConfig.app:
    CommandBase.configure_commands()
