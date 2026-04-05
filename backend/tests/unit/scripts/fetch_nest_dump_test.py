from pathlib import Path
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from scripts import fetch_nest_dump


class TestStripEtagQuotes:
    def test_strips_quotes_and_whitespace(self) -> None:
        assert fetch_nest_dump.strip_etag_quotes('  "abc"  ') == "abc"

    def test_no_quotes(self) -> None:
        assert fetch_nest_dump.strip_etag_quotes("xyz") == "xyz"


class TestLoadLocalEtag:
    def test_missing_returns_none(self, tmp_path: Path) -> None:
        assert fetch_nest_dump.load_local_etag(tmp_path / "missing.etag") is None

    def test_reads_file(self, tmp_path: Path) -> None:
        path = tmp_path / "x.etag"
        path.write_text("etag1\n", encoding="utf-8")
        assert fetch_nest_dump.load_local_etag(path) == "etag1"


def _mock_probe_body() -> MagicMock:
    body = MagicMock()
    body.__enter__.return_value.read.return_value = b"x"
    body.__exit__.return_value = None
    return body


class TestMain:
    @patch("scripts.fetch_nest_dump.boto3.client")
    def test_probe_failure_returns_1(
        self,
        mock_client: MagicMock,
        tmp_path: Path,
    ) -> None:
        (tmp_path / "data").mkdir()
        mock_client.return_value.get_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey"}},
            "GetObject",
        )
        with patch("scripts.common.backend_root", return_value=tmp_path):
            assert fetch_nest_dump.main() == 1

    @patch("scripts.fetch_nest_dump.boto3.client")
    def test_skips_download_when_etag_matches(
        self,
        mock_client: MagicMock,
        tmp_path: Path,
    ) -> None:
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        target = data_dir / "nest.dump"
        target.write_bytes(b"existing")
        etag_path = tmp_path / "data" / "nest.dump.etag"
        etag_path.write_text("same-etag", encoding="utf-8")
        mock_client.return_value.get_object.return_value = {
            "ETag": '"same-etag"',
            "Body": _mock_probe_body(),
        }
        with patch("scripts.common.backend_root", return_value=tmp_path):
            assert fetch_nest_dump.main() == 0
        mock_client.return_value.download_file.assert_not_called()

    @patch("scripts.fetch_nest_dump.boto3.client")
    def test_downloads_when_missing_file(
        self,
        mock_client: MagicMock,
        tmp_path: Path,
    ) -> None:
        (tmp_path / "data").mkdir()
        mock_client.return_value.get_object.return_value = {
            "ETag": '"remote-1"',
            "Body": _mock_probe_body(),
        }
        with patch("scripts.common.backend_root", return_value=tmp_path):
            assert fetch_nest_dump.main() == 0
        mock_client.return_value.download_file.assert_called_once()
        args = mock_client.return_value.download_file.call_args[0]
        assert args[0] == "owasp-nest-shared-data"
        assert args[1] == "nest.dump"
        assert args[2] == str(tmp_path / "data" / "nest.dump")
        etag_path = tmp_path / "data" / "nest.dump.etag"
        assert etag_path.read_text(encoding="utf-8") == "remote-1"

    @patch("scripts.fetch_nest_dump.boto3.client")
    def test_downloads_when_local_etag_differs(
        self,
        mock_client: MagicMock,
        tmp_path: Path,
    ) -> None:
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        target = data_dir / "nest.dump"
        target.write_bytes(b"stale")
        etag_path = tmp_path / "data" / "nest.dump.etag"
        etag_path.write_text("old-etag", encoding="utf-8")
        mock_client.return_value.get_object.return_value = {
            "ETag": '"new-etag"',
            "Body": _mock_probe_body(),
        }
        with patch("scripts.common.backend_root", return_value=tmp_path):
            assert fetch_nest_dump.main() == 0
        mock_client.return_value.download_file.assert_called_once()
        assert etag_path.read_text(encoding="utf-8") == "new-etag"

    @patch("scripts.fetch_nest_dump.boto3.client")
    def test_download_failure_returns_1(
        self,
        mock_client: MagicMock,
        tmp_path: Path,
    ) -> None:
        (tmp_path / "data").mkdir()
        mock_client.return_value.get_object.return_value = {
            "ETag": '"v2"',
            "Body": _mock_probe_body(),
        }
        mock_client.return_value.download_file.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied"}},
            "GetObject",
        )
        with patch("scripts.common.backend_root", return_value=tmp_path):
            assert fetch_nest_dump.main() == 1
