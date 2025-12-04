from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase

from . import (
    ai,
    board,
    chapters,
    committees,
    community,
    contact,
    contribute,
    donate,
    events,
    gsoc,
    jobs,
    leaders,
    news,
    owasp,
    policies,
    projects,
    sponsor,
    sponsors,
    staff,
    users,
)

if SlackConfig.app:
    CommandBase.configure_commands()
