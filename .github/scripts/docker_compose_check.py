"""Docker Compose volume allowlist check for merge queue.

Canonical volume names are the fixed ``CANONICAL_VOLUMES`` baseline below — not
whatever keys happen to appear in the merge-group revision. Overrides and Compose
``name:`` values must use those names. Custom Docker volume names are fine on
PR branches for local isolation and review; this check runs on ``merge_group``
so they do not land on main (see ``docker-compose/README.md``).

When adding a legitimate new named volume, update ``CANONICAL_VOLUMES`` in the
same PR as the compose change so the expansion is reviewable.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE_COMPOSE_GLOBS = (
    "docker-compose/*/compose.yaml",
    "docker-compose/*/compose.yml",
)
OVERRIDE_COMPOSE_GLOBS = (
    "docker-compose/*/compose.override.yaml",
    "docker-compose/*/compose.override.yml",
)

# Baseline allowlist independent of the revision under test. Do not derive this
# from compose files in the merge group.
CANONICAL_VOLUMES = frozenset(
    {
        "backend-venv",
        "cache-data",
        "db-data",
        "docs-venv",
        "e2e-cache-data",
        "e2e-db-data",
        "frontend-next",
        "frontend-node-modules",
        "fuzz-cache-data",
        "fuzz-db-data",
    }
)


class ComposeCheckError(Exception):
    """Raised when a compose manifest cannot be parsed or checked."""


class ComposeVolumeChecker:
    """Validate named volumes in committed Docker Compose manifests."""

    def __init__(
        self,
        root: Path,
        *,
        allowed_volumes: frozenset[str] | None = None,
    ) -> None:
        """Create a checker for compose files under ``root``.

        If ``allowed_volumes`` is omitted, ``CANONICAL_VOLUMES`` is used.
        """
        self.root = root
        self.allowed_volumes = allowed_volumes

    @classmethod
    def from_repository(cls) -> ComposeVolumeChecker:
        """Build a checker rooted at the Git repository containing this script."""
        return cls(cls.find_repository_root(Path(__file__)))

    @staticmethod
    def find_repository_root(start: Path) -> Path:
        """Walk parents of ``start`` until a ``.git`` entry is found."""
        current = start.resolve()
        if current.is_file():
            current = current.parent
        for path in (current, *current.parents):
            if (path / ".git").exists():
                return path
        message = "Error: not inside a git repository."
        raise ComposeCheckError(message)

    def find_base_compose_files(self) -> list[Path]:
        """Discover committed base compose manifests (not overrides)."""
        files: list[Path] = []
        for pattern in BASE_COMPOSE_GLOBS:
            files.extend(self.root.glob(pattern))
        return files

    def find_compose_files(self) -> list[Path]:
        """Discover committed compose manifests and overrides."""
        files = self.find_base_compose_files()
        for pattern in OVERRIDE_COMPOSE_GLOBS:
            files.extend(self.root.glob(pattern))
        return files

    def resolve_allowed_volumes(self) -> frozenset[str]:
        """Return the effective allowlist (explicit or ``CANONICAL_VOLUMES``)."""
        if self.allowed_volumes is not None:
            return self.allowed_volumes
        return CANONICAL_VOLUMES

    def is_allowed(self, name: str, *, allowed_volumes: frozenset[str] | None = None) -> bool:
        """Return whether ``name`` is in the effective allowlist."""
        if allowed_volumes is None:
            allowed_volumes = self.resolve_allowed_volumes()
        return name in allowed_volumes

    @staticmethod
    def extract_volume_name(mount: str) -> str | None:
        """Extract a named volume from a short-syntax mount string.

        Short syntax: ``name:/path`` or ``name:/path:ro``.
        Bind mounts and absolute paths are ignored.
        """
        first_part = mount.split(":", maxsplit=1)[0]
        if first_part.startswith(("/", ".")) or "/" in first_part:
            return None
        return first_part

    def load_compose_file(self, filepath: Path) -> object:
        """Load and return parsed YAML from ``filepath``."""
        try:
            with filepath.open() as handle:
                return yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            message = f"Error: failed to parse {filepath}:\n  {exc}"
            raise ComposeCheckError(message) from exc

    def check_file(
        self,
        filepath: Path,
        *,
        allowed_volumes: frozenset[str] | None = None,
    ) -> list[str]:
        """Return disallowed volume references found in one compose file."""
        data = self.load_compose_file(filepath)
        if not isinstance(data, dict):
            return []

        if allowed_volumes is None:
            allowed_volumes = self.resolve_allowed_volumes()
        violations: list[str] = []
        violations.extend(
            self.check_top_level_volumes(data.get("volumes"), allowed_volumes=allowed_volumes)
        )
        violations.extend(
            self.check_service_volumes(data.get("services"), allowed_volumes=allowed_volumes)
        )
        return violations

    def check_top_level_volumes(
        self,
        top_volumes: object,
        *,
        allowed_volumes: frozenset[str],
    ) -> list[str]:
        """Return disallowed names from a top-level ``volumes`` mapping."""
        if not isinstance(top_volumes, dict):
            return []

        violations: list[str] = []
        for key, value in top_volumes.items():
            key_str = str(key)
            if not self.is_allowed(key_str, allowed_volumes=allowed_volumes):
                violations.append(key_str)
            if isinstance(value, dict):
                external_name = value.get("name")
                if isinstance(external_name, str) and not self.is_allowed(
                    external_name,
                    allowed_volumes=allowed_volumes,
                ):
                    violations.append(f"{external_name} (name for '{key_str}')")
        return violations

    def check_service_volumes(
        self,
        services: object,
        *,
        allowed_volumes: frozenset[str],
    ) -> list[str]:
        """Return disallowed named volumes referenced by services."""
        if not isinstance(services, dict):
            return []

        violations: list[str] = []
        for service_name, service in services.items():
            if not isinstance(service, dict):
                continue
            mounts = service.get("volumes") or []
            for mount in mounts:
                volume_name = self.volume_name_from_mount(mount)
                if volume_name and not self.is_allowed(
                    volume_name,
                    allowed_volumes=allowed_volumes,
                ):
                    violations.append(f"{volume_name} (in service '{service_name}')")
        return violations

    def volume_name_from_mount(self, mount: object) -> str | None:
        """Return a named volume from a short- or long-syntax mount entry.

        Long syntax without ``type`` is treated as a named volume when ``source``
        is not a bind path. Explicit ``type: bind`` mounts are ignored.
        """
        if isinstance(mount, str):
            return self.extract_volume_name(mount)

        if (
            isinstance(mount, dict)
            and mount.get("type") in (None, "volume")
            and isinstance(mount.get("source"), str)
        ):
            source = mount["source"]
            if not source.startswith(("/", ".")) and "/" not in source:
                return source

        return None

    def violations(self) -> list[tuple[Path, str]]:
        """Return ``(filepath, volume)`` pairs for disallowed volume references."""
        compose_files = self.find_compose_files()
        if not compose_files:
            message = "Error: no Docker Compose files found under docker-compose/."
            raise ComposeCheckError(message)

        allowed_volumes = self.resolve_allowed_volumes()
        findings: list[tuple[Path, str]] = []
        for filepath in sorted(compose_files):
            findings.extend(
                (filepath, volume)
                for volume in self.check_file(filepath, allowed_volumes=allowed_volumes)
            )
        return findings


def main() -> None:
    """Run the allowlist check against the current repository."""
    try:
        checker = ComposeVolumeChecker.from_repository()
        findings = checker.violations()
    except ComposeCheckError as exc:
        sys.stderr.write(f"{exc}\n")
        sys.exit(1)

    for filepath, volume in findings:
        sys.stdout.write(
            f"Error: volume '{volume}' in {filepath.relative_to(checker.root)} "
            "is not in the canonical allowlist. Custom names are fine on PR "
            "branches in compose.override.yaml; revert before merge. See "
            "docker-compose/README.md.\n"
        )

    if findings:
        sys.exit(1)


if __name__ == "__main__":
    main()
