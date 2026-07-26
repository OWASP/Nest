"""Tests for the Docker Compose merge-queue volume allowlist check."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from docker_compose_check import ComposeCheckError, ComposeVolumeChecker

CANONICAL_VOLUMES = frozenset(
    {
        "backend-venv",
        "cache-data",
        "db-data",
        "e2e-cache-data",
    }
)


class TestComposeVolumeChecker:
    """Tests for ``ComposeVolumeChecker``."""

    @pytest.fixture
    def checker(self, tmp_path: Path) -> ComposeVolumeChecker:
        return ComposeVolumeChecker(tmp_path, allowed_volumes=CANONICAL_VOLUMES)

    def test_extract_volume_name_accepts_named_volume(self) -> None:
        assert (
            ComposeVolumeChecker.extract_volume_name("db-data:/var/lib/postgresql/data")
            == "db-data"
        )

    def test_extract_volume_name_accepts_named_volume_with_mode(self) -> None:
        assert ComposeVolumeChecker.extract_volume_name("cache-data:/tmp/cache:ro") == "cache-data"

    def test_extract_volume_name_ignores_bind_mount(self) -> None:
        assert (
            ComposeVolumeChecker.extract_volume_name("../../backend:/home/owasp/backend") is None
        )

    def test_extract_volume_name_ignores_absolute_path(self) -> None:
        assert (
            ComposeVolumeChecker.extract_volume_name("/var/run/docker.sock:/var/run/docker.sock")
            is None
        )

    def test_extract_volume_name_ignores_relative_path_with_slash(self) -> None:
        assert ComposeVolumeChecker.extract_volume_name("./data:/data") is None

    @pytest.mark.parametrize(
        ("name", "allowed"),
        [
            ("db-data", True),
            ("e2e-cache-data", True),
            ("db-data-123", False),
            ("db-data-fix-login", False),
            ("cache-data-ark", False),
        ],
    )
    def test_is_allowed(
        self,
        checker: ComposeVolumeChecker,
        name: str,
        allowed: bool,
    ) -> None:
        assert checker.is_allowed(name) is allowed

    def test_find_compose_files_discovers_yaml_yml_and_overrides(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        local = tmp_path / "docker-compose" / "local"
        staging = tmp_path / "docker-compose" / "staging"
        local.mkdir(parents=True)
        staging.mkdir(parents=True)
        (local / "compose.yaml").write_text("services: {}\n")
        (local / "compose.override.yaml").write_text("# local overrides\n")
        (staging / "compose.yml").write_text("services: {}\n")
        (tmp_path / "docker-compose" / "README.md").write_text("docs\n")

        found = {path.name for path in checker.find_compose_files()}

        assert found == {"compose.yaml", "compose.yml", "compose.override.yaml"}

    def test_derive_allowed_volumes_from_base_compose_only(
        self,
        tmp_path: Path,
    ) -> None:
        local = tmp_path / "docker-compose" / "local"
        local.mkdir(parents=True)
        (local / "compose.yaml").write_text(
            yaml.dump({"volumes": {"db-data": None, "cache-data": None}})
        )
        (local / "compose.override.yaml").write_text(
            yaml.dump({"volumes": {"db-data": {"name": "db-data-local"}}})
        )

        checker = ComposeVolumeChecker(tmp_path)

        assert checker.derive_allowed_volumes() == frozenset({"db-data", "cache-data"})

    def test_check_file_allows_comment_only_override(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.override.yaml"
        compose.write_text("# local overrides only\n")

        assert checker.check_file(compose) == []

    def test_check_file_flags_unknown_top_level_volume(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.yaml"
        compose.write_text(
            yaml.dump(
                {
                    "services": {},
                    "volumes": {
                        "db-data-42": None,
                        "db-data": None,
                    },
                }
            )
        )

        assert checker.check_file(compose) == ["db-data-42"]

    def test_check_file_flags_custom_external_name_in_override(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.override.yaml"
        compose.write_text(
            yaml.dump(
                {
                    "volumes": {
                        "backend-venv": {"name": "backend-venv-local-test"},
                    },
                }
            )
        )

        assert checker.check_file(compose) == [
            "backend-venv-local-test (name for 'backend-venv')",
        ]

    def test_check_file_allows_canonical_external_name(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.yaml"
        compose.write_text(
            yaml.dump(
                {
                    "services": {},
                    "volumes": {
                        "db-data": {"name": "db-data"},
                    },
                }
            )
        )

        assert checker.check_file(compose) == []

    def test_check_file_flags_short_syntax_service_mount(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.yaml"
        compose.write_text(
            yaml.dump(
                {
                    "services": {
                        "db": {
                            "volumes": ["db-data-7:/var/lib/postgresql/data"],
                        },
                    },
                }
            )
        )

        assert checker.check_file(compose) == [
            "db-data-7 (in service 'db')",
        ]

    def test_check_file_flags_long_syntax_service_mount(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.yaml"
        compose.write_text(
            yaml.dump(
                {
                    "services": {
                        "api": {
                            "volumes": [
                                {
                                    "type": "volume",
                                    "source": "cache-data-99",
                                    "target": "/data",
                                },
                            ],
                        },
                    },
                }
            )
        )

        assert checker.check_file(compose) == [
            "cache-data-99 (in service 'api')",
        ]

    def test_check_file_flags_long_syntax_without_type(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.yaml"
        compose.write_text(
            yaml.dump(
                {
                    "services": {
                        "api": {
                            "volumes": [
                                {
                                    "source": "cache-data-99",
                                    "target": "/data",
                                },
                            ],
                        },
                    },
                }
            )
        )

        assert checker.check_file(compose) == [
            "cache-data-99 (in service 'api')",
        ]

    def test_check_file_ignores_typeless_bind_path_source(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.yaml"
        compose.write_text(
            yaml.dump(
                {
                    "services": {
                        "api": {
                            "volumes": [
                                {
                                    "source": "./config",
                                    "target": "/config",
                                },
                            ],
                        },
                    },
                }
            )
        )

        assert checker.check_file(compose) == []

    def test_check_file_ignores_bind_mounts_and_allowlisted_names(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.yaml"
        compose.write_text(
            yaml.dump(
                {
                    "services": {
                        "api": {
                            "volumes": [
                                "../../backend:/home/owasp/backend",
                                "db-data:/var/lib/postgresql/data",
                                {
                                    "type": "bind",
                                    "source": "./config",
                                    "target": "/config",
                                },
                            ],
                        },
                    },
                    "volumes": {"db-data": None},
                }
            )
        )

        assert checker.check_file(compose) == []

    def test_check_file_returns_empty_for_non_mapping(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.yaml"
        compose.write_text("- just a list\n")

        assert checker.check_file(compose) == []

    def test_check_file_raises_on_invalid_yaml(
        self,
        checker: ComposeVolumeChecker,
        tmp_path: Path,
    ) -> None:
        compose = tmp_path / "compose.yaml"
        compose.write_text("services: [\n")

        with pytest.raises(ComposeCheckError, match="failed to parse"):
            checker.check_file(compose)

    def test_violations_flags_override_custom_name_using_derived_allowlist(
        self,
        tmp_path: Path,
    ) -> None:
        local = tmp_path / "docker-compose" / "local"
        local.mkdir(parents=True)
        (local / "compose.yaml").write_text(yaml.dump({"volumes": {"db-data": None}}))
        (local / "compose.override.yaml").write_text(
            yaml.dump({"volumes": {"db-data": {"name": "db-data-local-test"}}})
        )

        findings = ComposeVolumeChecker(tmp_path).violations()

        assert findings == [
            (
                local / "compose.override.yaml",
                "db-data-local-test (name for 'db-data')",
            ),
        ]

    def test_violations_raises_when_no_compose_files(self, tmp_path: Path) -> None:
        with pytest.raises(ComposeCheckError, match="no Docker Compose files"):
            ComposeVolumeChecker(tmp_path).violations()

    def test_find_repository_root_walks_parents(self, tmp_path: Path) -> None:
        (tmp_path / ".git").mkdir()
        nested = tmp_path / "docker-compose" / "local"
        nested.mkdir(parents=True)
        script = nested / "docker_compose_check.py"
        script.write_text("# placeholder\n")

        assert ComposeVolumeChecker.find_repository_root(script) == tmp_path

    def test_find_repository_root_raises_outside_git(self, tmp_path: Path) -> None:
        with pytest.raises(ComposeCheckError, match="not inside a git repository"):
            ComposeVolumeChecker.find_repository_root(tmp_path)
