from unittest.mock import MagicMock

from apps.mentorship.models import Mentee
from apps.github.models import User as GithubUser


class TestMentee:
    def test_str_returns_github_login(self):
        github_user = MagicMock(spec=GithubUser, login="testmentee")

        mentee = MagicMock(spec=Mentee)
        mentee.github_user = github_user

        assert Mentee.__str__(mentee) == "testmentee"
