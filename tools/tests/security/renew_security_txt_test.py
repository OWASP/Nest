"""Tests for the security.txt renewer."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from renew_security_txt import (
    GeneratedKey,
    GpgKeyGenerator,
    RepositoryPaths,
    SecurityTxtConfig,
    SecurityTxtRenderer,
    SecurityTxtRenewer,
    gpg_expire_date,
)

PACIFIC = ZoneInfo("America/Los_Angeles")
TEST_PASSPHRASE = "test-passphrase"  # noqa: S105

FAKE_PUBLIC_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----
fake-public
-----END PGP PUBLIC KEY BLOCK-----
"""

FAKE_PRIVATE_KEY = """-----BEGIN PGP PRIVATE KEY BLOCK-----
fake-private
-----END PGP PRIVATE KEY BLOCK-----
"""


class FakeKeyGenerator:
    """Test double that returns fixed armored key material."""

    def __init__(self) -> None:
        self.calls = 0
        self.expire_dates: list[str] = []
        self.passphrases: list[str] = []

    def generate(self, *, expire_date: str, passphrase: str) -> GeneratedKey:
        self.calls += 1
        self.expire_dates.append(expire_date)
        self.passphrases.append(passphrase)
        return GeneratedKey(
            fingerprint="A" * 40,
            public_key=FAKE_PUBLIC_KEY,
            private_key=FAKE_PRIVATE_KEY,
        )


class TestSecurityTxtRenderer:
    def test_render_includes_required_fields(self) -> None:
        config = SecurityTxtConfig()
        content = SecurityTxtRenderer(config).render("2027-07-01T00:00:00-07:00")

        assert f"Contact: {config.github_contact}" in content
        assert f"Contact: {config.mailto_contact}" in content
        assert f"Encryption: {config.encryption_url}" in content
        assert "Expires: 2027-07-01T00:00:00-07:00" in content
        assert content.index(f"Contact: {config.github_contact}") < content.index(
            f"Contact: {config.mailto_contact}"
        )
        names = [
            line.split(":", 1)[0]
            for line in content.splitlines()
            if line.strip() and not line.startswith("#")
        ]
        assert names == sorted(names)


class TestSecurityTxtRenewerHelpers:
    def test_gpg_expire_date_uses_pacific_calendar_date(self) -> None:
        assert gpg_expire_date("2027-07-01T00:00:00-07:00") == "2027-07-01"

    def test_next_july_first_expires_uses_current_year_before_july(self) -> None:
        now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=PACIFIC)
        assert SecurityTxtRenewer.next_july_first_expires(now=now) == "2026-07-01T00:00:00-07:00"

    def test_next_july_first_expires_rolls_forward_on_or_after_july_first(self) -> None:
        now = datetime(2026, 7, 1, 0, 0, 0, tzinfo=PACIFIC)
        assert SecurityTxtRenewer.next_july_first_expires(now=now) == "2027-07-01T00:00:00-07:00"

    def test_find_repository_root_discovers_git_directory(self, tmp_path: Path) -> None:
        (tmp_path / ".git").mkdir()
        nested = tmp_path / "tools" / "security"
        nested.mkdir(parents=True)
        assert SecurityTxtRenewer.find_repository_root(nested) == tmp_path

    def test_repository_paths(self, tmp_path: Path) -> None:
        paths = RepositoryPaths(tmp_path)
        assert paths.security_txt == tmp_path / "frontend/public/.well-known/security.txt"
        assert paths.pgp_key == tmp_path / "frontend/public/.well-known/pgp-key.txt"
        assert paths.private_key(2026) == (
            tmp_path / "tools/security/private/nest-security-private-key-2026.asc"
        )

    def test_resolve_passphrase_requires_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("NEST_SECURITY_PGP_PASSPHRASE", raising=False)
        with pytest.raises(RuntimeError, match="NEST_SECURITY_PGP_PASSPHRASE"):
            SecurityTxtRenewer.resolve_passphrase()


class TestSecurityTxtRenewer:
    def test_renew_writes_artifacts_with_injected_generator(self, tmp_path: Path) -> None:
        generator = FakeKeyGenerator()
        renewer = SecurityTxtRenewer(tmp_path, key_generator=generator)
        now = datetime(2026, 7, 29, tzinfo=PACIFIC)

        key = renewer.renew(
            expires="2027-07-01T00:00:00-07:00",
            passphrase=TEST_PASSPHRASE,
            now=now,
        )

        assert generator.calls == 1
        assert generator.expire_dates == ["2027-07-01"]
        assert generator.passphrases == [TEST_PASSPHRASE]
        assert key.fingerprint == "A" * 40
        assert renewer.paths.pgp_key.read_text(encoding="utf-8") == FAKE_PUBLIC_KEY
        assert renewer.paths.private_key(2026).read_text(encoding="utf-8") == FAKE_PRIVATE_KEY
        security_txt = renewer.paths.security_txt.read_text(encoding="utf-8")
        assert f"Contact: {renewer.config.mailto_contact}" in security_txt
        assert f"Encryption: {renewer.config.encryption_url}" in security_txt
        assert "Expires: 2027-07-01T00:00:00-07:00" in security_txt
        names = [
            line.split(":", 1)[0]
            for line in security_txt.splitlines()
            if line.strip() and not line.startswith("#")
        ]
        assert names == sorted(names)

    def test_renew_respects_private_key_out(self, tmp_path: Path) -> None:
        private_key_out = tmp_path / "secure" / "key.asc"
        renewer = SecurityTxtRenewer(tmp_path, key_generator=FakeKeyGenerator())
        now = datetime(2026, 7, 29, tzinfo=PACIFIC)

        renewer.renew(
            expires="2027-07-01T00:00:00-07:00",
            private_key_out=private_key_out,
            passphrase=TEST_PASSPHRASE,
            now=now,
        )

        assert private_key_out.read_text(encoding="utf-8") == FAKE_PRIVATE_KEY
        assert not renewer.paths.private_key(2026).exists()

    def test_renew_requires_passphrase(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("NEST_SECURITY_PGP_PASSPHRASE", raising=False)
        renewer = SecurityTxtRenewer(tmp_path, key_generator=FakeKeyGenerator())
        with pytest.raises(RuntimeError, match="NEST_SECURITY_PGP_PASSPHRASE"):
            renewer.renew(expires="2027-07-01T00:00:00-07:00")


class TestGpgKeyGenerator:
    def test_require_gpg_raises_when_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("renew_security_txt.shutil.which", lambda _name: None)
        with pytest.raises(RuntimeError, match="gpg is required"):
            GpgKeyGenerator.require_gpg()

    def test_fingerprint_from_key_created_prefers_primary(self) -> None:
        status = (
            "[GNUPG:] KEY_CREATED S BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB\n"
            "[GNUPG:] KEY_CREATED P AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        )
        assert (
            GpgKeyGenerator.fingerprint_from_key_created(status)
            == "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        )

    def test_fingerprint_from_key_created_falls_back_to_first(self) -> None:
        status = "[GNUPG:] KEY_CREATED B CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
        assert (
            GpgKeyGenerator.fingerprint_from_key_created(status)
            == "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
        )

    def test_fingerprint_from_key_created_raises_when_missing(self) -> None:
        with pytest.raises(RuntimeError, match="KEY_CREATED"):
            GpgKeyGenerator.fingerprint_from_key_created("[GNUPG:] GOODSIG")

    def test_run_gpg_surfaces_stderr_on_failure(self, tmp_path: Path) -> None:
        try:
            gpg = GpgKeyGenerator.require_gpg()
        except RuntimeError:
            pytest.skip("gpg is not installed")

        generator = GpgKeyGenerator(SecurityTxtConfig(), gpg_binary=gpg)
        with pytest.raises(RuntimeError, match="failed with exit code") as raised:
            generator.run_gpg(tmp_path, "--list-secret-keys", "missing-key-for-error-ux")
        assert "gpg --list-secret-keys" in str(raised.value)

    def test_public_key_expire_date_reads_colon_listing(self) -> None:
        try:
            GpgKeyGenerator.require_gpg()
        except RuntimeError:
            pytest.skip("gpg is not installed")

        key = GpgKeyGenerator(SecurityTxtConfig()).generate(
            expire_date="2027-07-01",
            passphrase=TEST_PASSPHRASE,
        )
        assert GpgKeyGenerator.public_key_expire_date(key.public_key) == "2027-07-01"

    def test_generate_creates_passphrase_protected_keypair(self) -> None:
        try:
            GpgKeyGenerator.require_gpg()
        except RuntimeError:
            pytest.skip("gpg is not installed")

        key = GpgKeyGenerator(SecurityTxtConfig()).generate(
            expire_date="2027-07-01",
            passphrase=TEST_PASSPHRASE,
        )

        assert len(key.fingerprint) >= 40
        assert "BEGIN PGP PUBLIC KEY BLOCK" in key.public_key
        assert "BEGIN PGP PRIVATE KEY BLOCK" in key.private_key
