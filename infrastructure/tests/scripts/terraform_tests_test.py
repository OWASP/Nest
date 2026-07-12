"""Tests for ``scripts.terraform_tests``."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from scripts.commands import CommandRunner
from scripts.errors import TestRunnerError
from scripts.terraform_tests import TerraformTests


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
            fake_file("storage.tftest.hcl"),
        ]

        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        TerraformTests(commands).discover_and_run("unit")

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
            "-filter=tests/storage.tftest.hcl",
            check=False,
            capture_output=True,
        )

    @patch("pathlib.Path.iterdir")
    def test_find_test_files_error(self, mock_iterdir: MagicMock) -> None:
        mock_iterdir.side_effect = OSError("Permission denied")
        with pytest.raises(TestRunnerError, match="could not read /dummy/dir"):
            TerraformTests().find_test_files("/dummy/dir", "unit")

    def test_run_module_tests_init_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: Failed to query available provider packages",
        )
        with pytest.raises(
            TestRunnerError, match="terraform init failed in dummy_dir"
        ) as exc_info:
            TerraformTests(commands).run_module_tests("dummy_dir", ["test.tftest.hcl"])
        assert "Failed to query available provider packages" in str(exc_info.value)

    def test_run_module_tests_test_failure(self) -> None:
        commands = MagicMock(spec=CommandRunner)
        commands.run.side_effect = [
            MagicMock(returncode=0, stdout="Terraform initialized!\n", stderr=""),
            MagicMock(
                returncode=1,
                stdout="tests/test.tftest.hcl... fail\n",
                stderr="Error: test failed\n",
            ),
        ]
        with pytest.raises(
            TestRunnerError, match="terraform test failed in dummy_dir"
        ) as exc_info:
            TerraformTests(commands).run_module_tests("dummy_dir", ["test.tftest.hcl"])
        assert "tests/test.tftest.hcl... fail" in str(exc_info.value)
        assert "Error: test failed" in str(exc_info.value)
