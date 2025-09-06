def configure_slack_events():
    """Configure Slack events after Django apps are ready."""
    from apps.slack.apps import SlackConfig
    from apps.slack.events import (
        app_home_opened,
        app_mention,
        message_posted,
        team_join,
        url_verification,
    )
    from apps.slack.events.event import EventBase
    from apps.slack.events.member_joined_channel import (
        catch_all,
        contribute,
        gsoc,
        project_nest,
    )

    if SlackConfig.app:
        EventBase.configure_events()
