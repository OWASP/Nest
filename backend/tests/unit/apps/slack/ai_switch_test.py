"""Verify AI can be disabled without disabling ordinary Slack behavior."""

from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from apps.slack.commands.ai import Ai
from apps.slack.commands.staff import Staff
from apps.slack.common.handlers.ai import get_blocks, process_ai_query
from apps.slack.events.app_mention import AppMention
from apps.slack.events.message_posted import MessagePosted


def test_disabled_slash_command(settings):
    settings.NESTBOT_AI_ASSISTANT_ENABLED = False
    with patch("apps.slack.common.handlers.ai.get_blocks") as provider:
        blocks = Ai().render_blocks({"text": "What is OWASP?"})
    assert blocks[0]["text"]["text"] == "NestBot AI assistant is currently disabled."
    provider.assert_not_called()


def test_disabled_mentions_have_no_ai_side_effects(settings):
    settings.NESTBOT_AI_ASSISTANT_ENABLED = False
    client = Mock()
    with (
        patch("apps.slack.events.app_mention.Conversation") as conversation,
        patch("apps.slack.events.app_mention.download_file") as download,
        patch("apps.slack.events.app_mention.get_blocks") as provider,
    ):
        AppMention().handle_event(
            {"channel": "C123", "text": "help", "files": [{"mimetype": "image/png"}]}, client
        )
    conversation.objects.filter.assert_not_called()
    download.assert_not_called()
    provider.assert_not_called()
    assert client.mock_calls == []


def test_disabled_detection_never_initializes_provider_or_queue(settings):
    settings.NESTBOT_AI_ASSISTANT_ENABLED = False
    client = Mock()
    with (
        patch("apps.slack.events.message_posted.QuestionDetector") as detector,
        patch("apps.slack.events.message_posted.Conversation") as conversation,
        patch("apps.slack.events.message_posted.django_rq.get_queue") as queue,
    ):
        handler = MessagePosted()
        handler.handle_event({"channel": "C123", "text": "What is OWASP?"}, client)
    detector.assert_not_called()
    conversation.objects.get.assert_not_called()
    queue.assert_not_called()
    assert client.mock_calls == []


def test_disabled_ai_keeps_thread_reply_bookkeeping(settings):
    """Record thread replies with AI disabled without contacting providers."""
    settings.NESTBOT_AI_ASSISTANT_ENABLED = False
    client = Mock()
    with (
        patch("apps.slack.events.message_posted.Message") as message,
        patch("apps.slack.events.message_posted.QuestionDetector") as detector,
        patch("apps.slack.events.message_posted.Conversation") as conversation,
        patch("apps.slack.events.message_posted.django_rq.get_queue") as queue,
    ):
        MessagePosted().handle_event(
            {"channel": "C123", "thread_ts": "123.000", "text": "I can help"}, client
        )
    message.objects.filter.assert_called_once_with(
        slack_message_id="123.000", conversation__slack_channel_id="C123"
    )
    message.objects.filter.return_value.update.assert_called_once_with(has_replies=True)
    detector.assert_not_called()
    conversation.objects.get.assert_not_called()
    queue.assert_not_called()
    assert client.mock_calls == []


def test_queued_job_rechecks_switch(settings):
    settings.NESTBOT_AI_ASSISTANT_ENABLED = True
    with (
        patch("apps.slack.events.message_posted.QuestionDetector") as detector,
        patch("apps.slack.events.message_posted.Conversation") as conversation,
        patch("apps.slack.events.message_posted.Member") as member,
        patch("apps.slack.events.message_posted.Message") as message,
        patch("apps.slack.events.message_posted.django_rq.get_queue") as queue,
    ):
        detector.return_value.is_owasp_question.return_value = True
        message.update_data.return_value.id = 42
        MessagePosted().handle_event(
            {"channel": "C123", "user": "U123", "text": "What is OWASP?"}, Mock()
        )
        conversation.objects.get.assert_called_once_with(
            slack_channel_id="C123", is_nest_bot_assistant_enabled=True
        )
        member.objects.get.assert_called_once()
        _, queued_job, message_id = queue.return_value.enqueue_in.call_args.args

    settings.NESTBOT_AI_ASSISTANT_ENABLED = False
    with (
        patch("apps.slack.services.message_auto_reply.Message.objects.get") as lookup,
        patch("apps.slack.services.message_auto_reply.process_ai_query") as provider,
        patch("apps.slack.services.message_auto_reply.SlackConfig.app") as app,
    ):
        queued_job(message_id)
    lookup.assert_not_called()
    provider.assert_not_called()
    assert app.mock_calls == []


def test_direct_ai_handler_rechecks_switch(settings):
    settings.NESTBOT_AI_ASSISTANT_ENABLED = False
    with patch("apps.ai.flows.process_query") as provider:
        assert process_ai_query("help") is None
        assert "disabled" in get_blocks("help")[0]["text"]["text"]
    provider.assert_not_called()


def test_ordinary_slack_command_works_with_ai_disabled(settings):
    settings.NESTBOT_AI_ASSISTANT_ENABLED = False
    with patch("apps.slack.commands.staff.get_staff_data", return_value=[]) as staff:
        Staff().get_context({"user_id": "U123"})
    staff.assert_called_once()


@pytest.mark.parametrize(
    ("age_seconds", "local_host", "healthy"),
    [
        (0, True, True),
        (110, True, True),
        (121, True, False),
        (0, False, False),
        (None, True, False),
    ],
)
def test_worker_healthcheck(age_seconds, local_host, healthy):
    now = timezone.now()
    worker = Mock(
        hostname="worker-host" if local_host else "another-worker",
        last_heartbeat=now - timedelta(seconds=age_seconds) if age_seconds is not None else None,
    )
    with (
        patch(
            "apps.slack.management.commands.slack_ai_worker_healthcheck.Worker.all",
            return_value=[worker],
        ),
        patch("apps.slack.management.commands.slack_ai_worker_healthcheck.django_rq.get_queue"),
        patch(
            "apps.slack.management.commands.slack_ai_worker_healthcheck.socket.gethostname",
            return_value="worker-host",
        ),
        patch(
            "apps.slack.management.commands.slack_ai_worker_healthcheck.timezone.now",
            return_value=now,
        ),
    ):
        if healthy:
            call_command("slack_ai_worker_healthcheck")
        else:
            with pytest.raises(CommandError, match="No healthy local AI queue worker"):
                call_command("slack_ai_worker_healthcheck")
