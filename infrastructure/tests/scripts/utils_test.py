"""Tests for ``scripts.utils``."""

import os

import pytest

from scripts.utils import temporary_env

VAR = "NEST_TEMPORARY_ENV_TEST"


class TestTemporaryEnv:
    """Tests for ``temporary_env``."""

    @pytest.fixture(autouse=True)
    def _clean_env(self) -> None:
        os.environ.pop(VAR, None)

    def test_sets_and_unsets_when_previously_absent(self) -> None:
        with temporary_env(VAR, "value"):
            assert os.environ[VAR] == "value"
        assert VAR not in os.environ

    def test_restores_previous_value(self) -> None:
        os.environ[VAR] = "original"
        with temporary_env(VAR, "override"):
            assert os.environ[VAR] == "override"
        assert os.environ[VAR] == "original"

    def test_restores_on_exception(self) -> None:
        os.environ[VAR] = "original"
        with pytest.raises(RuntimeError), temporary_env(VAR, "override"):
            raise RuntimeError
        assert os.environ[VAR] == "original"

    def test_unsets_on_exception_when_previously_absent(self) -> None:
        with pytest.raises(RuntimeError), temporary_env(VAR, "value"):
            raise RuntimeError
        assert VAR not in os.environ
