from apps.owasp.models.chapter import Chapter
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
