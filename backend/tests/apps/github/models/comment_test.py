from django.contrib.contenttypes.models import ContentType

from apps.github.models.comment import Comment
from apps.github.models.user import User


class TestComment:
    def test_from_github_populates_fields(self, mocker):
        comment = Comment()
        gh_comment = mocker.Mock()
        gh_comment.body = "Test body"
        gh_comment.created_at = "2023-01-01T00:00:00Z"
        gh_comment.updated_at = "2023-01-02T00:00:00Z"

        mock_author = mocker.Mock(spec=User)
        mock_author._state = mocker.Mock()

        comment.from_github(gh_comment, author=mock_author)

        assert comment.body == "Test body"
        assert comment.created_at == "2023-01-01T00:00:00Z"
        assert comment.updated_at == "2023-01-02T00:00:00Z"
        assert comment.author == mock_author

    def test_update_data_creates_new(self, mocker):
        mocker.patch(
            "apps.github.models.comment.Comment.objects.get", side_effect=Comment.DoesNotExist
        )
        mock_ct = ContentType(app_label="fake", model="fake")
        mock_ct.id = 1
        mocker.patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model",
            return_value=mock_ct,
        )

        gh_comment = mocker.Mock()
        gh_comment.id = 12345
        gh_comment.body = "New comment"

        mock_save = mocker.patch.object(Comment, "save")

        mock_content_object = mocker.Mock()
        mock_content_object.pk = 999

        comment = Comment.update_data(
            gh_comment, author=None, content_object=mock_content_object, save=True
        )

        assert comment.github_id == 12345
        assert comment.object_id == 999
        assert comment.content_type == mock_ct
        mock_save.assert_called_once()

    def test_update_data_updates_existing(self, mocker):
        existing_comment = Comment(github_id=12345, body="Old body")
        mocker.patch(
            "apps.github.models.comment.Comment.objects.get", return_value=existing_comment
        )
        mock_save = mocker.patch.object(Comment, "save")

        gh_comment = mocker.Mock()
        gh_comment.id = 12345
        gh_comment.body = "Updated body"

        comment = Comment.update_data(gh_comment, save=True)

        assert comment.body == "Updated body"
        assert comment.github_id == 12345
        mock_save.assert_called_once()

    def test_str_representation(self):
        comment = Comment(body="A very long comment body that should be truncated", author=None)
        long_body = "A" * 60
        comment.body = long_body

        assert str(comment).startswith("None - AAAAA")
        assert len(str(comment)) <= 60
