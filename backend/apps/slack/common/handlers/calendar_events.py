"""Google Calendar Events Handlers."""

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from httplib2.error import ServerNotFoundError

from apps.common.constants import NL
from apps.slack.blocks import get_pagination_buttons, markdown


def get_cancel_reminder_blocks(reminder_schedule_id: int, slack_user_id: str) -> list[dict]:
    """Get the blocks for canceling a reminder."""
    from apps.nest.models.reminder_schedule import ReminderSchedule
    from apps.nest.schedulers.calendar_events.slack import SlackScheduler

    try:
        reminder_schedule = ReminderSchedule.objects.get(pk=reminder_schedule_id)
    except ReminderSchedule.DoesNotExist:
        return [markdown("*Please provide a valid reminder number.*")]
    if reminder_schedule.reminder.member.slack_user_id != slack_user_id:
        return [markdown("*You can only cancel your own reminders.*")]
    SlackScheduler(reminder_schedule).cancel()
    return [
        markdown(
            f"*Canceled the reminder for event '{reminder_schedule.reminder.event.name}'*"
            f" in #{reminder_schedule.reminder.entity_channel.channel.name}"
        )
    ]


def get_events_blocks(slack_user_id: str, presentation, page: int = 1) -> list[dict]:
    """Get Google Calendar events blocks for Slack home view."""
    from apps.nest.clients.google_calendar import GoogleCalendarClient
    from apps.nest.models.google_account_authorization import GoogleAccountAuthorization
    from apps.owasp.models.event import Event

    auth = GoogleAccountAuthorization.authorize(slack_user_id)
    if not isinstance(auth, GoogleAccountAuthorization):
        return [markdown(f"*Please sign in with Google first through this <{auth[0]}|link>*")]
    try:
        client = GoogleCalendarClient(auth)
        min_time = timezone.now() + timezone.timedelta(days=(page - 1))
        max_time = min_time + timezone.timedelta(days=1)
        events = client.get_events(min_time=min_time, max_time=max_time)
    except ServerNotFoundError:
        return [markdown("*Please check your internet connection.*")]
    parsed_events = Event.parse_google_calendar_events(events)
    if not (events or parsed_events):
        return [markdown("*No upcoming calendar events found.*")]
    blocks = [
        markdown(
            f"*Your upcoming calendar events from {min_time.strftime('%Y-%m-%d %H:%M')}"
            f" to {max_time.strftime('%Y-%m-%d %H:%M %Z')}*"
            f"{NL}You can set a reminder for an event with `/nestbot reminder set "
            "--channel [channel] --event_number [event number] --minutes_before [minutes before]"
            " --message [optional message] --recurrence [recurrence]`"
        )
    ]
    for i, event in enumerate(parsed_events):
        event_number = (i + 1) + 1000 * (page - 1)
        cache.set(f"{slack_user_id}_{event_number}", event.google_calendar_id, timeout=3600)
        blocks.append(
            markdown(
                f"*Name: {event.name}*"
                f"{NL}*Number: {event_number}*"
                f"{NL}- Starts at: {event.start_date.strftime('%Y-%m-%d %H:%M %Z')}"
                f"{NL}- Ends at: {event.end_date.strftime('%Y-%m-%d %H:%M %Z')}"
            )
        )
    if presentation.include_pagination and (
        pagination_block := get_pagination_buttons("calendar_events", page, page + 1)
    ):
        blocks.append(
            {
                "type": "actions",
                "elements": pagination_block,
            }
        )
    return blocks


def get_reminders_blocks(slack_user_id: str) -> list[dict]:
    """Get reminders blocks for Slack home view."""
    from apps.nest.models.reminder_schedule import ReminderSchedule

    reminders_schedules = ReminderSchedule.objects.filter(
        reminder__member__slack_user_id=slack_user_id,
    ).order_by("scheduled_time")
    if not reminders_schedules:
        return [markdown("*No reminders found. You can set one with `/nestbot reminder set`*")]
    blocks = [markdown("*Your upcoming reminders:*")]
    blocks.extend(
        markdown(
            f"{NL}- Reminder Number: {reminder_schedule.pk}"
            f"{NL}- Channel: #{reminder_schedule.reminder.entity_channel.channel.name}"
            f"{NL}- Scheduled Time: "
            f"{reminder_schedule.scheduled_time.strftime('%Y-%m-%d, %H:%M %Z')}"
            f"{NL}- Recurrence: {reminder_schedule.recurrence}"
            f"{NL}- Message: {reminder_schedule.reminder.message or 'No message'}"
        )
        for reminder_schedule in reminders_schedules
    )
    return blocks


def get_setting_reminder_blocks(args, slack_user_id: str, workspace_id: str) -> list[dict]:
    """Get the blocks for setting a reminder."""
    from django.contrib.contenttypes.models import ContentType

    from apps.nest.clients.google_calendar import GoogleCalendarClient
    from apps.nest.handlers.calendar_events import get_calendar_id, set_reminder
    from apps.nest.models.google_account_authorization import GoogleAccountAuthorization
    from apps.nest.schedulers.calendar_events.slack import SlackScheduler
    from apps.owasp.models.entity_channel import EntityChannel
    from apps.slack.models.conversation import Conversation
    from apps.slack.models.member import Member

    return_block = None
    try:
        auth = GoogleAccountAuthorization.authorize(slack_user_id)
        if not isinstance(auth, GoogleAccountAuthorization):
            return [markdown(f"*Please sign in with Google first through this <{auth[0]}|link>*")]
        content_type_member = ContentType.objects.get_for_model(Member)
        content_type_conversation = ContentType.objects.get_for_model(Conversation)
        conversation = Conversation.objects.get(
            name=args.channel.lstrip("#"),
            workspace__slack_workspace_id=workspace_id,
        )
        member = Member.objects.get(slack_user_id=slack_user_id)
        channel = EntityChannel.objects.get(
            channel_id=conversation.pk,
            channel_type=content_type_conversation,
            entity_id=member.pk,
            entity_type=content_type_member,
        )
        google_calendar_id = get_calendar_id(slack_user_id, args.event_number)
        client = GoogleCalendarClient(auth)
        reminder_schedule = set_reminder(
            channel=channel,
            client=client,
            member=member,
            google_calendar_id=google_calendar_id,
            minutes_before=args.minutes_before,
            recurrence=args.recurrence,
            message=" ".join(args.message) if args.message else "",
        )
        SlackScheduler(reminder_schedule).schedule()
        SlackScheduler.send_message(
            f"<@{reminder_schedule.reminder.member.slack_user_id}> set a reminder: "
            f"{reminder_schedule.reminder.message}"
            f" at {reminder_schedule.scheduled_time.strftime('%Y-%m-%d %H:%M %Z')}",
            reminder_schedule.reminder.entity_channel.pk,
        )
    except ValidationError as e:
        return_block = [markdown(f"*{e.message}*")]
    except ValueError as e:
        return_block = [markdown(f"*{e!s}*")]
    except ServerNotFoundError:
        return_block = [markdown("*Please check your internet connection.*")]
    except Conversation.DoesNotExist:
        return_block = [markdown(f"*Channel '{args.channel}' does not exist in this workspace.*")]
    except Member.DoesNotExist:
        return_block = [markdown("*Member does not exist.*")]
    except EntityChannel.DoesNotExist:
        return_block = [markdown(f"*{args.channel} is not linked to your account.*")]
    return (
        return_block
        if return_block
        else [
            markdown(
                f"*{args.minutes_before}-minute reminder set for event"
                f" '{reminder_schedule.reminder.event.name}'*"
                f" in {args.channel}"
                f"{NL} Scheduled Time: "
                f"{reminder_schedule.scheduled_time.strftime('%Y-%m-%d %H:%M %Z')}"
                f"{NL} Recurrence: {reminder_schedule.recurrence}"
                f"{NL} Message: {reminder_schedule.reminder.message}"
            )
        ]
    )
