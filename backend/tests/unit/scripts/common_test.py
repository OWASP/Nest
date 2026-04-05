import pytest

from scripts import common


class TestSharedDataBucket:
    def test_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SHARED_DATA_BUCKET", raising=False)
        assert common.shared_data_bucket() == "owasp-nest-shared-data"

    def test_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SHARED_DATA_BUCKET", "my-bucket")
        assert common.shared_data_bucket() == "my-bucket"


class TestBackendRoot:
    def test_points_at_tree_containing_scripts(self) -> None:
        root = common.backend_root()
        assert (root / "scripts" / "common.py").is_file()
