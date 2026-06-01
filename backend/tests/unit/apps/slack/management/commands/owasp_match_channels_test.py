from unittest.mock import Mock

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project
from apps.slack.management.commands.owasp_match_channels import Command
from apps.slack.models import Conversation


class TestOwaspMatchChannels:
    def test_handle_dry_run(self, mocker):
        mock_chapter = mocker.Mock(spec=Chapter, id=1)
        mock_chapter.name = "OWASP Chapter One"
        mock_chapter.__str__ = lambda x: x.name

        mock_conv = mocker.Mock(spec=Conversation, id=10)
        mock_conv.name = "chapter-one"

        mock_conv_qs = mocker.Mock()
        mock_conv_qs.only.return_value.iterator.return_value = [mock_conv]
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.Conversation.objects",
            mock_conv_qs,
        )

        mock_chapter_qs = mocker.Mock()
        mock_chapter_qs.filter.return_value.only.return_value.iterator.return_value = [
            mock_chapter
        ]
        mocker.patch("apps.owasp.models.chapter.Chapter.objects", mock_chapter_qs)

        mock_committee_qs = mocker.Mock()
        mock_committee_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.committee.Committee.objects", mock_committee_qs)

        mock_project_qs = mocker.Mock()
        mock_project_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.project.Project.objects", mock_project_qs)

        mock_ec_qs = mocker.Mock()
        mock_ec_qs.filter.return_value.exists.return_value = False
        mocker.patch("apps.owasp.models.entity_channel.EntityChannel.objects", mock_ec_qs)
        mock_ec_get_or_create = mock_ec_qs.get_or_create

        mock_ct = mocker.Mock()
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.ContentType.objects.get_for_model",
            return_value=mock_ct,
        )

        command = Command()
        command.stdout = mocker.Mock()
        command.handle(dry_run=True, threshold=80)

        mock_ec_get_or_create.assert_not_called()

    def test_handle_creates_channel(self, mocker):
        mock_project = mocker.Mock(spec=Project, id=2)
        mock_project.name = "OWASP Juice Shop"
        mock_conv = mocker.Mock(spec=Conversation, id=20)
        mock_conv.name = "project-juice-shop"

        mock_conv_qs = mocker.Mock()
        mock_conv_qs.only.return_value.iterator.return_value = [mock_conv]
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.Conversation.objects",
            mock_conv_qs,
        )

        mock_chapter_qs = mocker.Mock()
        mock_chapter_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.chapter.Chapter.objects", mock_chapter_qs)

        mock_committee_qs = mocker.Mock()
        mock_committee_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.committee.Committee.objects", mock_committee_qs)

        mock_project_qs = mocker.Mock()
        mock_project_qs.filter.return_value.only.return_value.iterator.return_value = [
            mock_project
        ]
        mocker.patch("apps.owasp.models.project.Project.objects", mock_project_qs)

        mock_ct = mocker.Mock()
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.ContentType.objects.get_for_model",
            return_value=mock_ct,
        )

        mock_ec_qs = mocker.Mock()
        mock_ec_qs.filter.return_value.exists.return_value = False
        mocker.patch("apps.owasp.models.entity_channel.EntityChannel.objects", mock_ec_qs)
        mock_get_or_create = mock_ec_qs.get_or_create
        mock_get_or_create.return_value = (None, True)

        command = Command()
        command.stdout = mocker.Mock()
        command.handle(dry_run=False, threshold=80)

        mock_get_or_create.assert_called_once()
        _, kwargs = mock_get_or_create.call_args
        assert kwargs["entity_id"] == 2
        assert kwargs["channel_id"] == 20

    def test_strip_owasp_prefix(self):
        cmd = Command()
        assert cmd.strip_owasp_prefix("OWASP Nest") == "Nest"
        assert cmd.strip_owasp_prefix("Current OWASP Project") == "Current OWASP Project"
        assert cmd.strip_owasp_prefix("OWASP - Project") == "Project"
        assert cmd.strip_owasp_prefix("Simple Name") == "Simple Name"

    def test_strip_owasp_prefix_empty_name(self):
        """Test strip_owasp_prefix with empty/None name."""
        cmd = Command()
        assert cmd.strip_owasp_prefix("") == ""
        assert cmd.strip_owasp_prefix(None) is None

    def test_find_fuzzy_matches_skips_empty_conversation_name(self):
        """Test that conversations with empty name are skipped."""
        cmd = Command()
        mock_conv_with_name = type("Conversation", (), {"name": "project-test"})()
        mock_conv_without_name = type("Conversation", (), {"name": None})()
        mock_conv_empty_name = type("Conversation", (), {"name": ""})()

        conversations = [mock_conv_without_name, mock_conv_empty_name, mock_conv_with_name]
        matches = cmd.find_fuzzy_matches("Test Project", conversations, threshold=50)
        assert len(matches) == 1
        assert matches[0][0].name == "project-test"

    def test_find_fuzzy_matches_below_threshold(self):
        """Test that conversations with score below threshold are not matched."""
        cmd = Command()
        mock_conv = type("Conversation", (), {"name": "completely-different-channel"})()

        matches = cmd.find_fuzzy_matches("OWASP Juice Shop", [mock_conv], threshold=95)
        assert not matches

    def test_handle_skips_entity_without_name(self, mocker):
        """Test that entities with empty name are skipped."""
        mock_committee = mocker.Mock(spec=Committee, id=1)
        mock_committee.name = None

        mock_conv = mocker.Mock(spec=Conversation, id=10)
        mock_conv.name = "committee-test"

        mock_conv_qs = mocker.Mock()
        mock_conv_qs.only.return_value.iterator.return_value = [mock_conv]
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.Conversation.objects",
            mock_conv_qs,
        )

        mock_chapter_qs = mocker.Mock()
        mock_chapter_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.chapter.Chapter.objects", mock_chapter_qs)

        mock_committee_qs = mocker.Mock()
        mock_committee_qs.filter.return_value.only.return_value.iterator.return_value = [
            mock_committee
        ]
        mocker.patch("apps.owasp.models.committee.Committee.objects", mock_committee_qs)

        mock_project_qs = mocker.Mock()
        mock_project_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.project.Project.objects", mock_project_qs)

        mock_ec_qs = mocker.Mock()
        mocker.patch("apps.owasp.models.entity_channel.EntityChannel.objects", mock_ec_qs)

        mock_ct = mocker.Mock()
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.ContentType.objects.get_for_model",
            return_value=mock_ct,
        )

        command = Command()
        command.stdout = mocker.Mock()
        command.handle(dry_run=False, threshold=80)
        mock_ec_qs.get_or_create.assert_not_called()

    def test_handle_committee_matches_all_conversations(self, mocker):
        """Test that Committee model uses all_conversations for matching."""
        mock_committee = mocker.Mock(spec=Committee, id=1)
        mock_committee.name = "OWASP Education Committee"
        mock_conv = mocker.Mock(spec=Conversation, id=10)
        mock_conv.name = "education-committee"

        mock_conv_qs = mocker.Mock()
        mock_conv_qs.only.return_value.iterator.return_value = [mock_conv]
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.Conversation.objects",
            mock_conv_qs,
        )

        mock_chapter_qs = mocker.Mock()
        mock_chapter_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.chapter.Chapter.objects", mock_chapter_qs)

        mock_committee_qs = mocker.Mock()
        mock_committee_qs.filter.return_value.only.return_value.iterator.return_value = [
            mock_committee
        ]
        mocker.patch("apps.owasp.models.committee.Committee.objects", mock_committee_qs)

        mock_project_qs = mocker.Mock()
        mock_project_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.project.Project.objects", mock_project_qs)

        mock_ec_qs = mocker.Mock()
        mock_ec_qs.get_or_create.return_value = (mocker.Mock(), True)
        mocker.patch("apps.owasp.models.entity_channel.EntityChannel.objects", mock_ec_qs)

        mock_ct = mocker.Mock()
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.ContentType.objects.get_for_model",
            return_value=mock_ct,
        )

        command = Command()
        command.stdout = mocker.Mock()
        command.handle(dry_run=False, threshold=50)
        assert mock_ec_qs.get_or_create.call_count >= 1

    def test_add_arguments(self):
        """Test add_arguments registers expected parser arguments."""
        command = Command()
        mock_parser = Mock()
        command.add_arguments(mock_parser)
        assert mock_parser.add_argument.call_count == 2

    def test_handle_dry_run_existing_entity_channel(self, mocker):
        """Test dry run when EntityChannel already exists shows EXISTS status."""
        mock_chapter = mocker.Mock(spec=Chapter, id=1)
        mock_chapter.name = "OWASP Test Chapter"

        mock_conv = mocker.Mock(spec=Conversation, id=10)
        mock_conv.name = "chapter-test"

        mock_conv_qs = mocker.Mock()
        mock_conv_qs.only.return_value.iterator.return_value = [mock_conv]
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.Conversation.objects",
            mock_conv_qs,
        )

        mock_chapter_qs = mocker.Mock()
        mock_chapter_qs.filter.return_value.only.return_value.iterator.return_value = [
            mock_chapter
        ]
        mocker.patch("apps.owasp.models.chapter.Chapter.objects", mock_chapter_qs)

        mock_committee_qs = mocker.Mock()
        mock_committee_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.committee.Committee.objects", mock_committee_qs)

        mock_project_qs = mocker.Mock()
        mock_project_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.project.Project.objects", mock_project_qs)

        mock_ec_qs = mocker.Mock()
        mock_ec_qs.filter.return_value.exists.return_value = True
        mocker.patch("apps.owasp.models.entity_channel.EntityChannel.objects", mock_ec_qs)

        mock_ct = mocker.Mock()
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.ContentType.objects.get_for_model",
            return_value=mock_ct,
        )

        command = Command()
        command.stdout = mocker.Mock()
        command.handle(dry_run=True, threshold=50)

        mock_ec_qs.get_or_create.assert_not_called()

    def test_handle_non_dry_run_entity_not_created(self, mocker):
        """Test non-dry-run when EntityChannel already exists (created=False)."""
        mock_project = mocker.Mock(spec=Project, id=2)
        mock_project.name = "OWASP Test Project"

        mock_conv = mocker.Mock(spec=Conversation, id=20)
        mock_conv.name = "project-test"

        mock_conv_qs = mocker.Mock()
        mock_conv_qs.only.return_value.iterator.return_value = [mock_conv]
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.Conversation.objects",
            mock_conv_qs,
        )

        mock_chapter_qs = mocker.Mock()
        mock_chapter_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.chapter.Chapter.objects", mock_chapter_qs)

        mock_committee_qs = mocker.Mock()
        mock_committee_qs.filter.return_value.only.return_value.iterator.return_value = []
        mocker.patch("apps.owasp.models.committee.Committee.objects", mock_committee_qs)

        mock_project_qs = mocker.Mock()
        mock_project_qs.filter.return_value.only.return_value.iterator.return_value = [
            mock_project
        ]
        mocker.patch("apps.owasp.models.project.Project.objects", mock_project_qs)

        mock_ct = mocker.Mock()
        mocker.patch(
            "apps.slack.management.commands.owasp_match_channels.ContentType.objects.get_for_model",
            return_value=mock_ct,
        )

        mock_ec_qs = mocker.Mock()
        mock_ec_qs.get_or_create.return_value = (mocker.Mock(), False)
        mocker.patch("apps.owasp.models.entity_channel.EntityChannel.objects", mock_ec_qs)

        command = Command()
        command.stdout = mocker.Mock()
        command.handle(dry_run=False, threshold=50)

        mock_ec_qs.get_or_create.assert_called_once()
