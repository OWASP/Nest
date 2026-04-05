import sys
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from scripts import upload_nest_dump


class TestParseArgs:
    def test_default_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("scripts.common.backend_root", lambda: tmp_path)
        dump = tmp_path / "data" / "nest.dump"
        dump.parent.mkdir(parents=True)
        dump.write_bytes(b"d")
        monkeypatch.setattr(sys, "argv", ["upload_nest_dump.py"])
        ns = upload_nest_dump.parse_args()
        assert Path(ns.path).resolve() == dump.resolve()

    def test_custom_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        custom = tmp_path / "other.dump"
        custom.write_bytes(b"x")
        monkeypatch.setattr(sys, "argv", ["upload_nest_dump.py", str(custom)])
        ns = upload_nest_dump.parse_args()
        assert Path(ns.path).resolve() == custom.resolve()


class TestMain:
    @patch("scripts.upload_nest_dump.boto3.client")
    def test_missing_file_returns_1(self, mock_client: MagicMock) -> None:
        with patch(
            "scripts.upload_nest_dump.parse_args",
            return_value=Namespace(path="/nonexistent/nest.dump"),
        ):
            assert upload_nest_dump.main() == 1
        mock_client.assert_not_called()

    @patch("scripts.upload_nest_dump.boto3.client")
    def test_upload_success(self, mock_client: MagicMock, tmp_path: Path) -> None:
        dump = tmp_path / "nest.dump"
        dump.write_bytes(b"data")
        with patch(
            "scripts.upload_nest_dump.parse_args",
            return_value=Namespace(path=str(dump)),
        ):
            assert upload_nest_dump.main() == 0
        mock_client.return_value.upload_file.assert_called_once_with(
            str(dump),
            "owasp-nest-shared-data",
            "nest.dump",
            ExtraArgs={"ServerSideEncryption": "AES256"},
        )

    @patch("scripts.upload_nest_dump.boto3.client")
    def test_upload_respects_bucket_env(
        self,
        mock_client: MagicMock,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("SHARED_DATA_BUCKET", "env-bucket")
        dump = tmp_path / "nest.dump"
        dump.write_bytes(b"1")
        with patch(
            "scripts.upload_nest_dump.parse_args",
            return_value=Namespace(path=str(dump)),
        ):
            assert upload_nest_dump.main() == 0
        mock_client.return_value.upload_file.assert_called_once_with(
            str(dump),
            "env-bucket",
            "nest.dump",
            ExtraArgs={"ServerSideEncryption": "AES256"},
        )

    @patch("scripts.upload_nest_dump.boto3.client")
    def test_upload_failure_returns_1(self, mock_client: MagicMock, tmp_path: Path) -> None:
        dump = tmp_path / "nest.dump"
        dump.write_bytes(b"1")
        mock_client.return_value.upload_file.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied"}},
            "PutObject",
        )
        with patch(
            "scripts.upload_nest_dump.parse_args",
            return_value=Namespace(path=str(dump)),
        ):
            assert upload_nest_dump.main() == 1
