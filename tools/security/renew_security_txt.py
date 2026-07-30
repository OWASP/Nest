"""Renew security.txt and generate the Nest security OpenPGP keypair."""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

PACIFIC = ZoneInfo("America/Los_Angeles")
PASSPHRASE_ENV = "NEST_SECURITY_PGP_PASSPHRASE"  # noqa: S105


def private_key_filename(year: int) -> str:
    """Return the year-scoped private key export filename."""
    return f"nest-security-private-key-{year}.asc"


def gpg_expire_date(expires: str) -> str:
    """Convert a security.txt Expires value to a GnuPG ``Expire-Date`` (YYYY-MM-DD)."""
    return normalize_expires(expires)[:10]


def normalize_expires(expires: str) -> str:
    """Parse ``expires`` and rebuild a trusted Pacific ISO-8601 string.

    Reconstructs the value from datetime fields so untrusted CLI input cannot
    flow into written ``security.txt`` content.
    """
    expires_at = datetime.fromisoformat(expires)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=PACIFIC)
    expires_at = expires_at.astimezone(PACIFIC)
    return datetime(
        expires_at.year,
        expires_at.month,
        expires_at.day,
        expires_at.hour,
        expires_at.minute,
        expires_at.second,
        tzinfo=PACIFIC,
    ).isoformat(timespec="seconds")


@dataclass(frozen=True)
class SecurityTxtConfig:
    """Canonical Nest security.txt field values."""

    canonical_url: str = "https://nest.owasp.org/.well-known/security.txt"
    encryption_url: str = "https://nest.owasp.org/.well-known/pgp-key.txt"
    github_contact: str = "https://github.com/OWASP/Nest/security/advisories/new"
    mailto_contact: str = "mailto:nest+security@owasp.org"
    policy_url: str = "https://github.com/OWASP/Nest/blob/main/SECURITY.md"
    preferred_languages: str = "en"
    key_name: str = "OWASP Nest Security"
    key_email: str = "nest+security@owasp.org"


@dataclass(frozen=True)
class GeneratedKey:
    """ASCII-armored OpenPGP key material."""

    fingerprint: str
    public_key: str
    private_key: str


class RepositoryPaths:
    """Resolved paths for Nest security disclosure artifacts."""

    def __init__(self, root: Path) -> None:
        """Bind paths under the repository ``root``."""
        self.root = root.resolve()
        self.well_known = self.root / "frontend" / "public" / ".well-known"
        self.security_txt = self.well_known / "security.txt"
        self.pgp_key = self.well_known / "pgp-key.txt"
        self.private_key_directory = self.root / "tools" / "security" / "private"

    def private_key(self, year: int) -> Path:
        """Return the year-scoped private key export path."""
        return self.private_key_directory / private_key_filename(year)


class GpgKeyGenerator:
    """Generate Nest security OpenPGP keypairs with GnuPG."""

    def __init__(
        self,
        config: SecurityTxtConfig | None = None,
        *,
        gpg_binary: str | None = None,
    ) -> None:
        """Create a generator using ``config`` and an optional ``gpg`` path."""
        self.config = config or SecurityTxtConfig()
        self.gpg_binary = gpg_binary or self.require_gpg()

    @staticmethod
    def require_gpg() -> str:
        """Return the gpg binary path or raise if GnuPG is missing."""
        gpg = shutil.which("gpg")
        if gpg is None:
            msg = "gpg is required; install GnuPG and retry"
            raise RuntimeError(msg)
        return gpg

    def run_gpg(
        self,
        gnupg_home: Path,
        *args: str,
        stdin_data: str | None = None,
        passphrase_file: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run a gpg command against an isolated home directory."""
        command = [self.gpg_binary, "--homedir", str(gnupg_home), "--batch", "--yes"]
        if passphrase_file is not None:
            command.extend(
                [
                    "--pinentry-mode",
                    "loopback",
                    "--passphrase-file",
                    str(passphrase_file),
                ]
            )
        command.extend(args)
        logger.debug("Running: %s", " ".join(command))
        try:
            return subprocess.run(  # noqa: S603
                command,
                check=True,
                capture_output=True,
                text=True,
                input=stdin_data,
            )
        except subprocess.CalledProcessError as error:
            detail = (error.stderr or error.stdout or "").strip()
            message = f"gpg {' '.join(args)} failed with exit code {error.returncode}"
            if detail:
                message = f"{message}: {detail}"
            raise RuntimeError(message) from error

    def generate(self, *, expire_date: str, passphrase: str) -> GeneratedKey:
        """Generate a passphrase-protected Ed25519 keypair.

        ``expire_date`` must be ``YYYY-MM-DD`` and should match security.txt
        ``Expires`` (Pacific calendar date).
        """
        if not passphrase:
            msg = "passphrase must not be empty"
            raise ValueError(msg)

        with tempfile.TemporaryDirectory(prefix="nest-security-gpg-") as temp_home:
            gnupg_home = Path(temp_home)
            passphrase_path = gnupg_home / "passphrase"
            passphrase_path.write_text(f"{passphrase}\n", encoding="utf-8")
            passphrase_path.chmod(0o600)

            fingerprint = self.generate_keypair(
                gnupg_home,
                expire_date=expire_date,
                passphrase_file=passphrase_path,
            )
            return GeneratedKey(
                fingerprint=fingerprint,
                public_key=self.export_public_key(gnupg_home, fingerprint),
                private_key=self.export_private_key(
                    gnupg_home,
                    fingerprint,
                    passphrase_file=passphrase_path,
                ),
            )

    def generate_keypair(
        self,
        gnupg_home: Path,
        *,
        expire_date: str,
        passphrase_file: Path,
    ) -> str:
        """Generate an Ed25519 key and return its fingerprint."""
        batch = "\n".join(
            [
                "Key-Type: eddsa",
                "Key-Curve: ed25519",
                "Key-Usage: sign",
                "Subkey-Type: ecdh",
                "Subkey-Curve: cv25519",
                "Subkey-Usage: encrypt",
                f"Name-Real: {self.config.key_name}",
                f"Name-Email: {self.config.key_email}",
                f"Expire-Date: {expire_date}",
                "%commit",
                "",
            ]
        )
        logger.info(
            "Generating OpenPGP key for %s <%s> (expires %s)",
            self.config.key_name,
            self.config.key_email,
            expire_date,
        )
        result = self.run_gpg(
            gnupg_home,
            "--status-fd",
            "1",
            "--generate-key",
            stdin_data=batch,
            passphrase_file=passphrase_file,
        )
        fingerprint = self.fingerprint_from_key_created(result.stdout)
        logger.info("Generated key fingerprint %s", fingerprint)
        return fingerprint

    @staticmethod
    def fingerprint_from_key_created(status_output: str) -> str:
        """Return the primary-key fingerprint from GnuPG ``KEY_CREATED`` status lines.

        Prefers ``KEY_CREATED P`` (primary). Falls back to the first ``KEY_CREATED``
        line when the primary marker is absent.
        """
        primary: str | None = None
        first: str | None = None
        for line in status_output.splitlines():
            if not line.startswith("[GNUPG:] KEY_CREATED "):
                continue
            parts = line.split()
            # [GNUPG:] KEY_CREATED <type> <fingerprint> ...
            if len(parts) < 4:  # noqa: PLR2004
                continue
            key_type, fingerprint = parts[2], parts[3]
            if first is None:
                first = fingerprint
            if key_type == "P":
                primary = fingerprint
                break
        fingerprint = primary or first
        if fingerprint is None:
            msg = "gpg did not report KEY_CREATED fingerprint for the new key"
            raise RuntimeError(msg)
        return fingerprint

    @staticmethod
    def public_key_expire_date(armored_key: str, *, gpg_binary: str | None = None) -> str:
        """Return the primary public key expiry as a Pacific ``YYYY-MM-DD`` date.

        Uses ``gpg --show-keys --with-colons`` so committed ``pgp-key.txt`` can be
        checked against ``security.txt`` ``Expires`` without importing the key.
        """
        gpg = gpg_binary or shutil.which("gpg")
        if gpg is None:
            msg = "gpg is required; install GnuPG and retry"
            raise RuntimeError(msg)

        result = subprocess.run(  # noqa: S603
            [gpg, "--batch", "--yes", "--show-keys", "--with-colons"],
            check=False,
            capture_output=True,
            text=True,
            input=armored_key,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            message = f"gpg --show-keys failed with exit code {result.returncode}"
            if detail:
                message = f"{message}: {detail}"
            raise RuntimeError(message)

        for line in result.stdout.splitlines():
            if not line.startswith("pub:"):
                continue
            fields = line.split(":")
            # colon format: pub:...:created:expire:...
            if len(fields) < 7:  # noqa: PLR2004
                break
            expire_epoch = fields[6]
            if not expire_epoch:
                msg = "public key has no expiry date"
                raise RuntimeError(msg)
            expires_at = datetime.fromtimestamp(int(expire_epoch), tz=PACIFIC)
            return expires_at.date().isoformat()

        msg = "gpg --show-keys did not report a pub record"
        raise RuntimeError(msg)

    def export_public_key(self, gnupg_home: Path, fingerprint: str) -> str:
        """Export the ASCII-armored public key."""
        result = self.run_gpg(gnupg_home, "--armor", "--export", fingerprint)
        if "BEGIN PGP PUBLIC KEY BLOCK" not in result.stdout:
            msg = "public key export did not return an armored public key"
            raise RuntimeError(msg)
        return result.stdout if result.stdout.endswith("\n") else f"{result.stdout}\n"

    def export_private_key(
        self,
        gnupg_home: Path,
        fingerprint: str,
        *,
        passphrase_file: Path,
    ) -> str:
        """Export the ASCII-armored private key."""
        result = self.run_gpg(
            gnupg_home,
            "--armor",
            "--export-secret-keys",
            fingerprint,
            passphrase_file=passphrase_file,
        )
        if "BEGIN PGP PRIVATE KEY BLOCK" not in result.stdout:
            msg = "private key export did not return an armored private key"
            raise RuntimeError(msg)
        return result.stdout if result.stdout.endswith("\n") else f"{result.stdout}\n"


class SecurityTxtRenderer:
    """Render RFC 9116 security.txt contents for Nest."""

    def __init__(self, config: SecurityTxtConfig | None = None) -> None:
        """Create a renderer using ``config`` defaults when omitted."""
        self.config = config or SecurityTxtConfig()

    def render(self, expires: str) -> str:
        """Build the canonical security.txt contents."""
        return "\n".join(
            [
                f"Canonical: {self.config.canonical_url}",
                f"Contact: {self.config.github_contact}",
                f"Contact: {self.config.mailto_contact}",
                f"Encryption: {self.config.encryption_url}",
                f"Expires: {expires}",
                f"Policy: {self.config.policy_url}",
                f"Preferred-Languages: {self.config.preferred_languages}",
                "",
            ]
        )


class SecurityTxtRenewer:
    """Generate a Nest security keypair and refresh disclosure artifacts."""

    def __init__(
        self,
        root: Path,
        *,
        config: SecurityTxtConfig | None = None,
        key_generator: GpgKeyGenerator | None = None,
        renderer: SecurityTxtRenderer | None = None,
    ) -> None:
        """Create a renewer rooted at the Nest repository ``root``."""
        self.config = config or SecurityTxtConfig()
        self.paths = RepositoryPaths(root)
        self.key_generator = key_generator or GpgKeyGenerator(self.config)
        self.renderer = renderer or SecurityTxtRenderer(self.config)

    @staticmethod
    def find_repository_root(start: Path | None = None) -> Path:
        """Walk parents until a ``.git`` entry is found.

        Defaults to the process working directory first so Docker mounts
        (``-w /work``) resolve correctly even when the script lives outside
        the repository.
        """
        starts: list[Path] = []
        if start is not None:
            starts.append(start.resolve())
        else:
            starts.append(Path.cwd().resolve())
            starts.append(Path(__file__).resolve())

        for candidate in starts:
            current = candidate.parent if candidate.is_file() else candidate
            for path in (current, *current.parents):
                if (path / ".git").exists():
                    return path

        msg = f"could not find repository root from {start or Path.cwd()}"
        raise FileNotFoundError(msg)

    @staticmethod
    def next_july_first_expires(*, now: datetime | None = None) -> str:
        """Return the next 1 July midnight Pacific as an ISO-8601 offset datetime."""
        current = now or datetime.now(PACIFIC)
        if current.tzinfo is None:
            current = current.replace(tzinfo=PACIFIC)
        current = current.astimezone(PACIFIC)

        year = current.year
        candidate = datetime(year, 7, 1, 0, 0, 0, tzinfo=PACIFIC)
        if current >= candidate:
            candidate = datetime(year + 1, 7, 1, 0, 0, 0, tzinfo=PACIFIC)
        return candidate.isoformat(timespec="seconds")

    @staticmethod
    def resolve_passphrase() -> str:
        """Resolve the PGP passphrase from ``NEST_SECURITY_PGP_PASSPHRASE``."""
        value = os.environ.get(PASSPHRASE_ENV)
        if not value:
            msg = f"PGP passphrase required via {PASSPHRASE_ENV} environment variable"
            raise RuntimeError(msg)
        return value

    @staticmethod
    def validate_repository_root(root: Path) -> Path:
        """Resolve ``root`` and require Nest repository layout markers."""
        root_resolved = Path(os.path.realpath(root.expanduser()))
        required = (
            root_resolved / ".git",
            root_resolved / "frontend" / "public",
            root_resolved / "tools" / "security",
        )
        missing = [str(path.relative_to(root_resolved)) for path in required if not path.exists()]
        if missing:
            msg = f"path {root} is not a Nest repository root (missing: {', '.join(missing)})"
            raise ValueError(msg)
        return root_resolved

    @staticmethod
    def resolve_within_root(root: Path, path: Path) -> Path:
        """Resolve ``path`` and require it to stay under ``root``.

        Uses ``os.path.realpath`` + prefix check so path-escape sanitizers
        (including Sonar S8707) recognize the validation before any write.
        """
        root_real = os.path.realpath(root.expanduser())
        path_real = os.path.realpath(path.expanduser())
        root_prefix = root_real if root_real.endswith(os.sep) else f"{root_real}{os.sep}"
        if path_real != root_real and not path_real.startswith(root_prefix):
            msg = f"path {path} escapes repository root {root_real}"
            raise ValueError(msg)
        return Path(path_real)

    def write_text(self, path: Path, content: str) -> None:
        """Create parent directories and write UTF-8 text under the repository root."""
        safe_path = self.resolve_within_root(self.paths.root, path)
        safe_parent = self.resolve_within_root(self.paths.root, safe_path.parent)
        safe_parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding="utf-8")
        logger.info("Wrote %s", safe_path)

    def write_security_txt(self, expires: str) -> None:
        """Write ``security.txt`` using only trusted path segments under the repo root."""
        expires_value = normalize_expires(expires)
        root_real = os.path.realpath(self.paths.root)
        # Literal path segments — do not accept a caller-supplied path for this artifact.
        target = os.path.realpath(
            os.path.join(root_real, "frontend", "public", ".well-known", "security.txt")  # noqa: PTH118
        )
        root_prefix = root_real if root_real.endswith(os.sep) else f"{root_real}{os.sep}"
        if not target.startswith(root_prefix):
            msg = f"security.txt path escapes repository root {root_real}"
            raise ValueError(msg)
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        Path(target).write_text(self.renderer.render(expires_value), encoding="utf-8")
        logger.info("Wrote %s", target)

    def renew(
        self,
        *,
        expires: str | None = None,
        private_key_out: Path | None = None,
        passphrase: str | None = None,
        now: datetime | None = None,
    ) -> GeneratedKey:
        """Generate a new keypair and refresh security.txt artifacts.

        ``passphrase`` overrides the environment for tests; CLI renewal always
        reads ``NEST_SECURITY_PGP_PASSPHRASE``.
        """
        current = now or datetime.now(PACIFIC)
        if current.tzinfo is None:
            current = current.replace(tzinfo=PACIFIC)
        current = current.astimezone(PACIFIC)

        expires_value = (
            normalize_expires(expires)
            if expires is not None
            else self.next_july_first_expires(now=current)
        )
        expire_date = gpg_expire_date(expires_value)
        passphrase_value = passphrase if passphrase is not None else self.resolve_passphrase()
        private_key_path = (
            self.resolve_within_root(self.paths.root, private_key_out)
            if private_key_out is not None
            else self.paths.private_key(current.year)
        )
        key = self.key_generator.generate(
            expire_date=expire_date,
            passphrase=passphrase_value,
        )

        self.write_text(self.paths.pgp_key, key.public_key)
        self.write_text(private_key_path, key.private_key)
        self.write_security_txt(expires_value)

        logger.info("Renewal complete.")
        logger.info("Public key:   %s", self.paths.pgp_key)
        logger.info("security.txt: %s", self.paths.security_txt)
        logger.info("Private key:  %s", private_key_path)
        logger.warning(
            "Store the private key and passphrase in an organization secret store, "
            "then delete the local private-key copy. Never commit tools/security/private/."
        )
        return key


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a Nest security OpenPGP key and renew security.txt.",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        help="Nest repository root (default: discover from cwd / script path)",
    )
    parser.add_argument(
        "--expires",
        type=normalize_expires,
        help="ISO-8601 Expires value (default: next 1 July midnight Pacific)",
    )
    parser.add_argument(
        "--private-key-out",
        type=Path,
        help="Path for the private key export (default: tools/security/private/...)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )
    root = (
        SecurityTxtRenewer.validate_repository_root(args.repository_root)
        if args.repository_root is not None
        else SecurityTxtRenewer.find_repository_root()
    )
    renewer = SecurityTxtRenewer(root)
    renewer.renew(
        expires=args.expires,
        private_key_out=args.private_key_out,
    )


if __name__ == "__main__":
    main()
