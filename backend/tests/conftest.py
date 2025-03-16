import pytest
from configurations import importer


@pytest.fixture(scope="session", autouse=True)
def django_configurations_setup():  # noqa: PT004
    importer.install()
    