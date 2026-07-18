"""Tests for ``scripts.terraform_tests``."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from scripts.commands import CommandRunner
from scripts.errors import TestRunnerError
from scripts.terraform_tests import ExecutionMode, TerraformTests


class TestExecutionMode:
    """Tests for ``ExecutionMode``."""

    def test_execution_mode_members(self) -> None:
        """Verify the ExecutionMode enum only contains the expected execution modes."""
        expected = {ExecutionMode.UNIT, ExecutionMode.INTEGRATION}
        actual = set(ExecutionMode)
        assert actual == expected


class TestTerraformTests:
    """Tests for ``TerraformTests``."""

    @patch("pathlib.Path.exists")
    @patch("os.walk")
    @patch("pathlib.Path.iterdir")
    def test_discover_and_run_unit(
        self,
        mock_iterdir: MagicMock,
        mock_walk: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        mock_exists.return_value = True
        mock_walk.return_value = [
            ("infrastructure/modules/storage", ["tests"], []),
            ("infrastructure/modules/storage/tests", [], []),
        ]

        def fake_file(name: str) -> MagicMock:
            entry = MagicMock()
            entry.name = name
            entry.is_file.return_value = True
            return entry

        mock_iterdir.return_value = [
            fake_file("integration.tftest.hcl"),
            fake_file("unit.tftest.hcl"),
        ]

        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        TerraformTests(commands).discover_and_run(ExecutionMode.UNIT)

        commands.run.assert_any_call(
            "terraform",
            "-chdir=infrastructure/modules/storage",
            "init",
            "-backend=false",
            "-input=false",
            check=False,
            capture_output=True,
        )
        commands.run.assert_any_call(
            "terraform",
            "-chdir=infrastructure/modules/storage",
            "test",
            "-filter=tests/unit.tftest.hcl",
            check=False,
            capture_output=True,
        )

    @patch("pathlib.Path.iterdir")
    def test_find_test_files_error(self, mock_iterdir: MagicMock) -> None:
        mock_iterdir.side_effect = OSError("Permission denied")
        terraform_tests = TerraformTests()
        with pytest.raises(TestRunnerError, match="could not read /dummy/dir"):
            terraform_tests.find_test_files("/dummy/dir", ExecutionMode.UNIT)

    @pytest.mark.parametrize(
        ("filename", "mode", "expected"),
        [
            ("unit.tftest.hcl", ExecutionMode.UNIT, True),
            ("foo.unit.tftest.hcl", ExecutionMode.UNIT, True),
            ("integration.tftest.hcl", ExecutionMode.UNIT, False),
            ("foo.integration.tftest.hcl", ExecutionMode.UNIT, False),
            ("random.tftest.hcl", ExecutionMode.UNIT, False),
            ("integration.tftest.hcl", ExecutionMode.INTEGRATION, True),
            ("foo.integration.tftest.hcl", ExecutionMode.INTEGRATION, True),
            ("unit.tftest.hcl", ExecutionMode.INTEGRATION, False),
            ("foo.unit.tftest.hcl", ExecutionMode.INTEGRATION, False),
            ("random.tftest.hcl", ExecutionMode.INTEGRATION, False),
            ("not_a_test.hcl", ExecutionMode.UNIT, False),
            ("unit.tftest.json", ExecutionMode.UNIT, False),
        ],
    )
    def test_match_test_mode(self, filename: str, mode: ExecutionMode, expected: bool) -> None:
        assert TerraformTests.match_test_mode(filename, mode) is expected

    def test_run_module_tests_init_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: Failed to query available provider packages",
        )
        terraform_tests = TerraformTests(commands)
        with pytest.raises(
            TestRunnerError, match="terraform init failed in dummy_dir"
        ) as exc_info:
            terraform_tests.run_module_tests("dummy_dir", ["unit.tftest.hcl"])
        assert "Failed to query available provider packages" in str(exc_info.value)

    def test_run_module_tests_test_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout="Terraform initialized!\n", stderr=""),
            MagicMock(
                returncode=1,
                stdout="tests/unit.tftest.hcl... fail\n",
                stderr="Error: test failed\n",
            ),
        ]
        terraform_tests = TerraformTests(commands)
        with pytest.raises(
            TestRunnerError, match="terraform test failed in dummy_dir"
        ) as exc_info:
            terraform_tests.run_module_tests("dummy_dir", ["unit.tftest.hcl"])
        assert "tests/unit.tftest.hcl... fail" in str(exc_info.value)
        assert "Error: test failed" in str(exc_info.value)
