#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Add the script's directory to sys.path to import it
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_tests


class TestRunTests(unittest.TestCase):
    @patch("shutil.which")
    def test_require_cmd_exists(self, mock_which):
        mock_which.return_value = "/usr/bin/terraform"
        # Should not raise SystemExit or TestRunnerError
        run_tests.require_cmd("terraform")

    @patch("shutil.which")
    def test_require_cmd_not_exists(self, mock_which):
        mock_which.return_value = None
        with self.assertRaises(run_tests.TestRunnerError):
            run_tests.require_cmd("nonexistent-cmd")

    @patch("urllib.request.urlopen")
    def test_localstack_healthy_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        self.assertTrue(run_tests.localstack_healthy())

    @patch("urllib.request.urlopen")
    def test_localstack_healthy_failure(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")
        self.assertFalse(run_tests.localstack_healthy())

    @patch("urllib.request.urlopen")
    def test_localstack_license_activated_true(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"is_license_activated": true}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        self.assertTrue(run_tests.localstack_license_activated())

    @patch("urllib.request.urlopen")
    def test_localstack_license_activated_false(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"is_license_activated": false}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        self.assertFalse(run_tests.localstack_license_activated())

    @patch("os.path.exists")
    def test_get_localstack_image_info_pro(self, mock_exists):
        mock_exists.return_value = True
        dockerfile_content = (
            "FROM localstack/localstack-pro:2026.6.0@sha256:123456\nUSER localstack\n"
        )

        with patch("builtins.open", mock_open(read_data=dockerfile_content)):
            full_img, tag = run_tests.get_localstack_image_info("/dummy/root")
            self.assertEqual(
                full_img, "localstack/localstack-pro:2026.6.0@sha256:123456"
            )
            self.assertEqual(tag, "2026.6.0")

    @patch("os.path.exists")
    def test_get_localstack_image_info_standard(self, mock_exists):
        mock_exists.return_value = True
        dockerfile_content = "FROM localstack/localstack:2.3.1\n"

        with patch("builtins.open", mock_open(read_data=dockerfile_content)):
            full_img, tag = run_tests.get_localstack_image_info("/dummy/root")
            self.assertEqual(full_img, "localstack/localstack:2.3.1")
            self.assertEqual(tag, "2.3.1")

    @patch("os.path.exists")
    def test_check_existing_overrides_exist(self, mock_exists):
        mock_exists.return_value = True
        with self.assertRaises(run_tests.TestRunnerError):
            run_tests.check_existing_overrides()

    @patch("os.path.exists")
    def test_check_existing_overrides_none(self, mock_exists):
        mock_exists.return_value = False
        # Should not raise SystemExit or TestRunnerError
        run_tests.check_existing_overrides()

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_override_files(self, mock_file_open, mock_makedirs):
        run_tests.write_override_files()
        self.assertEqual(mock_file_open.call_count, len(run_tests.OVERRIDES))
        mock_makedirs.assert_called()

    @patch("os.path.exists")
    @patch("os.remove")
    @patch("subprocess.run")
    def test_cleanup(self, mock_sub_run, mock_remove, mock_exists):
        mock_exists.return_value = True
        run_tests.cleanup(localstack_started=True)
        self.assertEqual(mock_remove.call_count, len(run_tests.OVERRIDES))
        # Ensure docker stop and docker rm are called
        self.assertEqual(mock_sub_run.call_count, 2)
        mock_sub_run.assert_any_call(
            ["docker", "stop", run_tests.LOCALSTACK_CONTAINER_NAME],
            stdout=-3,
            stderr=-3,
        )
        mock_sub_run.assert_any_call(
            ["docker", "rm", run_tests.LOCALSTACK_CONTAINER_NAME], stdout=-3, stderr=-3
        )

    @patch("os.environ.get")
    @patch("subprocess.run")
    @patch("time.sleep")
    @patch("run_tests.localstack_healthy")
    @patch("run_tests.localstack_license_activated")
    def test_start_localstack_success(
        self, mock_license, mock_healthy, mock_sleep, mock_sub_run, mock_env
    ):
        mock_env.return_value = "dummy-token"
        mock_healthy.return_value = True
        mock_license.return_value = True

        run_tests.start_localstack("localstack/localstack:latest")

        # Verify docker run was called
        mock_sub_run.assert_any_call(
            [
                "docker",
                "run",
                "-d",
                "--name",
                run_tests.LOCALSTACK_CONTAINER_NAME,
                "-p",
                "4566:4566",
                "-e",
                "LOCALSTACK_AUTH_TOKEN",
                "localstack/localstack:latest",
            ],
            check=True,
            stdout=-3,
        )

    @patch("os.path.exists")
    @patch("os.walk")
    @patch("os.listdir")
    @patch("subprocess.run")
    def test_discover_and_run_tests_unit(
        self, mock_sub_run, mock_listdir, mock_walk, mock_exists
    ):
        mock_exists.return_value = True
        # Simulate walking directories and finding "tests" in dirs
        mock_walk.return_value = [
            ("infrastructure/modules/storage", ["tests"], []),
            ("infrastructure/modules/storage/tests", [], []),
        ]
        mock_listdir.return_value = ["integration.tftest.hcl", "storage.tftest.hcl"]

        mock_sub_run.return_value.returncode = 0

        run_tests.discover_and_run_tests("unit")

        # Verify terraform init and terraform test were called
        mock_sub_run.assert_any_call(
            [
                "terraform",
                "-chdir=infrastructure/modules/storage",
                "init",
                "-backend=false",
                "-input=false",
            ]
        )
        # In unit mode, it should filter storage.tftest.hcl (and NOT integration.tftest.hcl)
        mock_sub_run.assert_any_call(
            [
                "terraform",
                "-chdir=infrastructure/modules/storage",
                "test",
                "-filter=tests/storage.tftest.hcl",
            ]
        )

    @patch("os.listdir")
    def test_find_test_files_error(self, mock_listdir):
        mock_listdir.side_effect = Exception("Permission denied")
        with self.assertRaises(run_tests.TestRunnerError) as ctx:
            run_tests._find_test_files("/dummy/dir", "unit")
        self.assertIn("could not read /dummy/dir", str(ctx.exception))

    @patch("subprocess.run")
    def test_run_module_tests_init_failure(self, mock_sub_run):
        mock_sub_run.return_value.returncode = 1
        with self.assertRaises(run_tests.TestRunnerError) as ctx:
            run_tests._run_module_tests("dummy_dir", ["test.tftest.hcl"])
        self.assertIn("terraform init failed in dummy_dir", str(ctx.exception))

    @patch("subprocess.run")
    def test_run_module_tests_test_failure(self, mock_sub_run):
        # init succeeds (returncode = 0), test fails (returncode = 1)
        mock_sub_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=1),
        ]
        with self.assertRaises(run_tests.TestRunnerError) as ctx:
            run_tests._run_module_tests("dummy_dir", ["test.tftest.hcl"])
        self.assertIn("terraform test failed in dummy_dir", str(ctx.exception))

    @patch("time.sleep")
    @patch("run_tests.localstack_healthy")
    def test_wait_localstack_ready_healthy_timeout(self, mock_healthy, mock_sleep):
        mock_healthy.return_value = False
        with self.assertRaises(run_tests.TestRunnerError) as ctx:
            run_tests.wait_localstack_ready()
        self.assertIn("failed to become healthy", str(ctx.exception))

    @patch("subprocess.run")
    @patch("time.sleep")
    @patch("run_tests.localstack_healthy")
    @patch("run_tests.localstack_license_activated")
    def test_wait_localstack_ready_license_timeout(
        self, mock_license, mock_healthy, mock_sleep, mock_sub_run
    ):
        mock_healthy.return_value = True
        mock_license.return_value = False
        with self.assertRaises(run_tests.TestRunnerError) as ctx:
            run_tests.wait_localstack_ready()
        self.assertIn("license failed to activate", str(ctx.exception))
        mock_sub_run.assert_any_call(
            ["docker", "logs", "--tail", "30", run_tests.LOCALSTACK_CONTAINER_NAME]
        )

    @patch("run_tests.require_cmd")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_main_handles_test_runner_error(
        self, mock_exit, mock_print, mock_require_cmd
    ):
        mock_require_cmd.side_effect = run_tests.TestRunnerError("Mocked failure")
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                unit=True, integration=False, get_tag=False
            )
            run_tests.main()
            mock_exit.assert_called_once_with(1)
            mock_print.assert_any_call("Error: Mocked failure", file=sys.stderr)


if __name__ == "__main__":
    unittest.main()
