import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from apps.mentorship.models import Mentee, MenteeModule, Module, Program
from apps.github.models import User as GithubUser


class MockIntegrityError(Exception):
    pass


class TestMenteeModule:
    def setup_method(self):
        self.github_user = MagicMock(spec=GithubUser, login="testmentee")
        self.mentee = MagicMock(spec=Mentee, github_user=self.github_user, __str__=lambda self: "testmentee")
        self.program = MagicMock(spec=Program, name="Test Program", key="test-program")
        self.module = MagicMock(spec=Module, name="Test Module", key="test-module", program=self.program, __str__=lambda self: "Test Module")

    @patch("apps.mentorship.models.MenteeModule.objects.create")
    def test_create_mentee_module(self, mock_create):
        start_time = datetime(2023, 1, 1, 10, 0, 0)
        end_time = datetime(2023, 1, 1, 11, 0, 0)

        mock_mentee_module_instance = MagicMock(spec=MenteeModule)
        mock_mentee_module_instance.mentee = self.mentee
        mock_mentee_module_instance.module = self.module
        mock_mentee_module_instance.started_at = start_time
        mock_mentee_module_instance.ended_at = end_time
        mock_mentee_module_instance.__str__.return_value = f"{self.mentee} - {self.module}"
        
        mock_create.return_value = mock_mentee_module_instance

        mentee_module = MenteeModule.objects.create(
            mentee=self.mentee,
            module=self.module,
            started_at=start_time,
            ended_at=end_time,
        )
        mock_create.assert_called_once_with(
            mentee=self.mentee,
            module=self.module,
            started_at=start_time,
            ended_at=end_time,
        )
        assert mentee_module.mentee == self.mentee
        assert mentee_module.module == self.module
        assert mentee_module.started_at == start_time
        assert mentee_module.ended_at == end_time
        assert str(mentee_module) == f"{self.mentee} - {self.module}"

    @patch("apps.mentorship.models.MenteeModule.objects.create")
    def test_unique_together_constraint(self, mock_create):
        
        mock_create.side_effect = [
            MagicMock(spec=MenteeModule),
            MockIntegrityError("Mock Integrity Error"),
        ]
        MenteeModule.objects.create(
            mentee=self.mentee,
            module=self.module,
            started_at=datetime(2023, 1, 1, 10, 0, 0),
        )
        with pytest.raises(MockIntegrityError):
            MenteeModule.objects.create(
                mentee=self.mentee,
                module=self.module,
                started_at=datetime(2023, 1, 1, 10, 0, 0),
            )

        assert mock_create.call_count == 2
