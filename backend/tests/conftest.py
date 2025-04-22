import pytest
from configurations import importer


@pytest.fixture(scope="session", autouse=True)
def django_configurations_setup():
    importer.install()
