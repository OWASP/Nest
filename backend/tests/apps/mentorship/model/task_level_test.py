from unittest.mock import MagicMock

from apps.mentorship.models import Module, TaskLevel


class TestTaskLevelUnit:
    def test_str_returns_module_name_and_task_name(self):
        module = MagicMock(spec=Module)
        module.name = "Test Module"

        task_level = MagicMock(spec=TaskLevel)
        task_level.module = module
        task_level.name = "Beginner Task"

        assert TaskLevel.__str__(task_level) == "Test Module - Beginner Task"

    def test_str_handles_module_with_custom_str(self):
        module = MagicMock(spec=Module)
        module.name = "Custom Module"
        module.__str__.return_value = "ignored-str"

        task_level = MagicMock(spec=TaskLevel)
        task_level.module = module
        task_level.name = "Advanced Task"

        assert TaskLevel.__str__(task_level) == "Custom Module - Advanced Task"
