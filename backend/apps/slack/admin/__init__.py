"""Slack app admin."""

from .bot_interaction import BotInteractionAdmin  # ← ADD THIS LINE
from .conversation import ConversationAdmin
from .event import EventAdmin
from .member import MemberAdmin
from .message import MessageAdmin
from .workspace import WorkspaceAdmin
