#!/usr/bin/env python3
"""Ensures no Docker Compose volume is named with a temporary PR suffix (e.g. db-data-5079).
Runs as a pre-commit hook and in CI via `make pre-commit`."""

import re
import sys
from pathlib import Path

import yaml


def check_compose_file(file_path: Path) -> bool:
    """Check a single compose file for volume names with numeric suffixes."""
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data or 'volumes' not in data:
            return True
        
        volumes = data['volumes']
        if not isinstance(volumes, dict):
            return True
        
        # Check each top-level volume key for numeric suffix pattern
        for vol_name in volumes.keys():
            if isinstance(vol_name, str) and re.search(r'-[0-9]+$', vol_name):
                print(f'ERROR: {file_path}:0: temporary volume name detected: {vol_name}')
                print('       Volume names must not end with a numeric PR suffix (e.g. db-data-5079).')
                print('       Rename it back to its canonical name (e.g. db-data).')
                return False
        
        return True
    except Exception as e:
        # If YAML parsing fails, fail closed to ensure issues are caught
        print(f'ERROR: Could not parse {file_path} as YAML: {e}', file=sys.stderr)
        return False


def main() -> int:
    """Main entry point."""
    # Get compose files from git
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'ls-files', 'docker-compose/*/compose.yaml'],
            capture_output=True,
            text=True,
            check=True
        )
        compose_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
    except Exception as e:
        # If git ls-files fails, fail closed to ensure issues are caught
        print(f'ERROR: Could not enumerate compose files: {e}', file=sys.stderr)
        return 1
    
    if not compose_files:
        return 0
    
    failed = 0
    for file_str in compose_files:
        file_path = Path(file_str)
        if not file_path.is_file():
            continue
        
        if not check_compose_file(file_path):
            failed = 1
    
    return failed


if __name__ == '__main__':
    sys.exit(main())
