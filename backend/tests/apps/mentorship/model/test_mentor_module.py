from unittest.mock import MagicMock

from apps.mentorship.models import MentorModule
from apps.mentorship.models import Mentor, Module


class TestMentorModule:
    def test_str_returns_readable_identifier(self):
        mentor = MagicMock(spec=Mentor)
        mentor.__str__.return_value = "testmentor"

        module = MagicMock(spec=Module)
        module.__str__.return_value = "Test Module"

        mentor_module = MagicMock(spec=MentorModule)
        mentor_module.mentor = mentor
        mentor_module.module = module

        assert MentorModule.__str__(mentor_module) == "testmentor of Test Module"
