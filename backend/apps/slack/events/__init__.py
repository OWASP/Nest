from apps.slack.apps import SlackConfig
from apps.slack.events import app_home_opened, team_join, url_verification
from apps.slack.events.event import EventBase
from apps.slack.events.member_joined_channel import catch_all, contribute, gsoc

if SlackConfig.app:
    EventBase.configure_events()
