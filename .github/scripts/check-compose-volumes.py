#!/usr/bin/env python3
"""Check that no Docker Compose volume name has a numeric PR suffix."""

import re
import sys
from pathlib import Path

import yaml

VOLUME_SUFFIX_RE = re.compile(r"^([a-zA-Z0-9_./-]+)-\d+$")


def get_repo_root() -> Path:
    path = Path(__file__).resolve().parent
    for parent in [path, *path.parents]:
        if (parent / ".git").exists():
            return parent
    print("Error: not inside a git repository.", file=sys.stderr)
    sys.exit(1)


def find_compose_files(root: Path) -> list[Path]:
    files = list(root.glob("docker-compose/*/compose.yaml"))
    files += list(root.glob("docker-compose/*/compose.yml"))
    return files


def extract_volume_name(mount: str) -> str | None:
    """Extract volume name from a short-syntax mount string.

    Short syntax: ``name:/path`` or ``name:/path:ro``.
    Bind mounts (``../../path:/container``) and absolute paths
    (``/var/run/docker.sock:/...``) are ignored.
    """
    first_part = mount.split(":")[0]
    if first_part.startswith(("/", ".", "../../")):
        return None
    if "/" in first_part:
        return None
    return first_part


def check_compose_file(filepath: Path) -> list[str]:
    try:
        with open(filepath) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: failed to parse {filepath}:\n  {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict):
        return []

    errors = []

    top_volumes = data.get("volumes")
    if isinstance(top_volumes, dict):
        for key in top_volumes:
            if VOLUME_SUFFIX_RE.match(str(key)):
                errors.append(str(key))

    for service_name, service in data.get("services", {}).items():
        if not isinstance(service, dict):
            continue
        for mount in service.get("volumes", []):
            vol_name = None
            if isinstance(mount, str):
                vol_name = extract_volume_name(mount)
            elif isinstance(mount, dict):
                source = mount.get("source")
                if isinstance(source, str):
                    vol_name = source
            if vol_name and VOLUME_SUFFIX_RE.match(vol_name):
                errors.append(f"{vol_name} (in service '{service_name}')")

    return errors


def main() -> None:
    root = get_repo_root()
    compose_files = find_compose_files(root)

    if not compose_files:
        print(
            "Error: no Docker Compose files found under docker-compose/.",
            file=sys.stderr,
        )
        sys.exit(1)

    found = False
    for filepath in compose_files:
        bad = check_compose_file(filepath)
        if bad:
            found = True
            for entry in bad:
                print(
                    f"Error: volume '{entry}' in {filepath.relative_to(root)} "
                    "has a numeric PR suffix. Use a plain name instead."
                )

    if found:
        sys.exit(1)


if __name__ == "__main__":
    main()
