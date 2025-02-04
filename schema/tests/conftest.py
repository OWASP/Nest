import json
from pathlib import Path

import pytest

tests_dir = Path(__file__).resolve().parent
tests_data_dir = tests_dir / "data"
schema_dir = tests_dir.parent


@pytest.fixture
def chapter_schema():
    with Path(schema_dir / "chapter.json").open() as file:
        yield json.load(file)


@pytest.fixture
def project_schema():
    with Path(schema_dir / "project.json").open() as file:
        yield json.load(file)
