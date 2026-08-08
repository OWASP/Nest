"""Tests for the committed RFC 9116 security.txt file."""

from __future__ import annotations

import warnings
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from renew_security_txt import (
    SIGNATURE_BEGIN,
    SIGNED_MESSAGE_BEGIN,
    GpgKeyGenerator,
    SecurityTxtConfig,
    gpg_expire_date,
    unsigned_security_txt_body,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
WELL_KNOWN_DIRECTORY = REPOSITORY_ROOT / "frontend" / "public" / ".well-known"
PGP_KEY_PATH = WELL_KNOWN_DIRECTORY / "pgp-key.txt"
SECURITY_TXT_PATH = WELL_KNOWN_DIRECTORY / "security.txt"

CONFIG = SecurityTxtConfig()
CONTACT_URI_PREFIXES = ("https://", "mailto:")
EXPIRATION_WARNING_WINDOW = timedelta(days=30)


def parse_security_txt(text: str) -> dict[str, list[str]]:
    """Parse security.txt field names to one or more values."""
    fields: dict[str, list[str]] = {}
    for raw_line in unsigned_security_txt_body(text).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            msg = f"invalid security.txt line (missing ':'): {raw_line!r}"
            raise ValueError(msg)
        name, value = line.split(":", 1)
        fields.setdefault(name.strip().lower(), []).append(value.strip())
    return fields


def parse_expires(value: str) -> datetime:
    """Parse an Expires field into an aware UTC datetime."""
    expires = datetime.fromisoformat(value)
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    return expires.astimezone(UTC)


def assert_minimum_contents(fields: dict[str, list[str]]) -> None:
    """Fail when required RFC 9116 fields are missing or malformed."""
    contacts = fields.get("contact", [])
    assert contacts, "security.txt must include at least one Contact field"
    for contact in contacts:
        assert contact.startswith(CONTACT_URI_PREFIXES), (
            f"Contact must use https:// or mailto: URI, got: {contact!r}"
        )

    expires_values = fields.get("expires", [])
    assert len(expires_values) == 1, "security.txt must include exactly one Expires field"
    parse_expires(expires_values[0])


def assert_expiration(
    expires: datetime,
    *,
    now: datetime | None = None,
) -> None:
    """Fail when expired; warn when fewer than 30 days remain."""
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    current = current.astimezone(UTC)

    if current >= expires:
        pytest.fail(f"security.txt expired at {expires.isoformat()}")

    remaining = expires - current
    if remaining < EXPIRATION_WARNING_WINDOW:
        warnings.warn(
            f"security.txt expires in less than 30 days ({expires.isoformat()})",
            UserWarning,
            stacklevel=2,
        )


class TestSecurityTxt:
    """Checks for frontend/public/.well-known/security.txt."""

    def test_file_exists(self) -> None:
        assert SECURITY_TXT_PATH.is_file(), f"missing security.txt at {SECURITY_TXT_PATH}"

    def test_minimum_contents(self) -> None:
        fields = parse_security_txt(SECURITY_TXT_PATH.read_text(encoding="utf-8"))
        assert_minimum_contents(fields)

    def test_contacts_and_encryption(self) -> None:
        text = SECURITY_TXT_PATH.read_text(encoding="utf-8")
        body = unsigned_security_txt_body(text)
        fields = parse_security_txt(text)
        assert CONFIG.github_contact in fields.get("contact", [])
        assert CONFIG.mailto_contact in fields.get("contact", [])
        assert fields.get("encryption") == [CONFIG.encryption_url]
        assert body.index(f"Contact: {CONFIG.github_contact}") < body.index(
            f"Contact: {CONFIG.mailto_contact}"
        )

    def test_fields_are_alphabetical(self) -> None:
        body = unsigned_security_txt_body(SECURITY_TXT_PATH.read_text(encoding="utf-8"))
        names = [
            line.split(":", 1)[0]
            for line in body.splitlines()
            if line.strip() and not line.startswith("#")
        ]
        assert names == sorted(names)

    def test_file_is_clearsigned(self) -> None:
        text = SECURITY_TXT_PATH.read_text(encoding="utf-8")
        assert SIGNED_MESSAGE_BEGIN in text
        assert SIGNATURE_BEGIN in text
        assert text.count(SIGNED_MESSAGE_BEGIN) == 1
        assert text.count(SIGNATURE_BEGIN) == 1

    def test_pgp_public_key_exists(self) -> None:
        assert PGP_KEY_PATH.is_file(), f"missing pgp-key.txt at {PGP_KEY_PATH}"
        content = PGP_KEY_PATH.read_text(encoding="utf-8")
        assert "BEGIN PGP PUBLIC KEY BLOCK" in content
        assert "END PGP PUBLIC KEY BLOCK" in content

    def test_pgp_key_expiry_matches_security_txt_expires(self) -> None:
        try:
            GpgKeyGenerator.require_gpg()
        except RuntimeError:
            pytest.skip("gpg is not installed")

        fields = parse_security_txt(SECURITY_TXT_PATH.read_text(encoding="utf-8"))
        assert_minimum_contents(fields)
        expected = gpg_expire_date(fields["expires"][0])
        actual = GpgKeyGenerator.public_key_expire_date(PGP_KEY_PATH.read_text(encoding="utf-8"))
        assert actual == expected

    def test_expiration(self) -> None:
        fields = parse_security_txt(SECURITY_TXT_PATH.read_text(encoding="utf-8"))
        assert_minimum_contents(fields)
        assert_expiration(parse_expires(fields["expires"][0]))

    def test_parse_ignores_comments_and_blank_lines(self) -> None:
        text = f"""
# comment
Contact: {CONFIG.mailto_contact}

Expires: 2027-07-01T00:00:00-07:00
"""
        fields = parse_security_txt(text)
        assert fields["contact"] == [CONFIG.mailto_contact]
        assert fields["expires"] == ["2027-07-01T00:00:00-07:00"]

    def test_assert_minimum_contents_rejects_missing_contact(self) -> None:
        with pytest.raises(AssertionError, match="Contact"):
            assert_minimum_contents({"expires": ["2027-07-01T00:00:00Z"]})

    def test_assert_minimum_contents_rejects_invalid_contact_uri(self) -> None:
        with pytest.raises(AssertionError, match="Contact must use"):
            assert_minimum_contents(
                {
                    "contact": [CONFIG.key_email],
                    "expires": ["2027-07-01T00:00:00Z"],
                }
            )

    def test_assert_minimum_contents_rejects_missing_expires(self) -> None:
        with pytest.raises(AssertionError, match="Expires"):
            assert_minimum_contents({"contact": [CONFIG.mailto_contact]})

    def test_assert_expiration_fails_when_expired(self) -> None:
        now = datetime(2027, 7, 2, tzinfo=UTC)
        expires = datetime(2027, 7, 1, tzinfo=UTC)
        with pytest.raises(pytest.fail.Exception, match="expired"):
            assert_expiration(expires, now=now)

    def test_assert_expiration_warns_within_thirty_days(self) -> None:
        now = datetime(2027, 6, 15, tzinfo=UTC)
        expires = datetime(2027, 7, 1, tzinfo=UTC)
        with pytest.warns(UserWarning, match="less than 30 days"):
            assert_expiration(expires, now=now)

    def test_assert_expiration_passes_when_fresh(self) -> None:
        now = datetime(2026, 7, 29, tzinfo=UTC)
        expires = datetime(2027, 7, 1, 7, tzinfo=UTC)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            assert_expiration(expires, now=now)
        assert caught == []
