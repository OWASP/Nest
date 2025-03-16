import django
import pytest
from django.conf import settings


@pytest.fixture(scope="session", autouse=True)
def _setup_django():
    settings.configure()
    django.setup()
