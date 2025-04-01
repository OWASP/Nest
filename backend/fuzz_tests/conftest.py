"""Populating the database with test data."""

import pytest
from django.apps import apps
from django.conf import settings
from model_bakery import baker


@pytest.fixture(autouse=True)
def populate_db(django_db_blocker):
    """Fixture to populate the database with test data."""
    # Create test data for the models you want to test
    settings.DATABASES["default"] = settings.DATABASES["fuzz_tests"]
    with django_db_blocker.unblock():
        all_models = apps.get_models()
        for model in all_models:
            # Skip models that are not relevant for the tests
            if model.__name__ in ["BulkSaveModel", "TimestampedModel"]:
                continue
            # Create a few instances of each model
            baker.make(model, _quantity=5)
