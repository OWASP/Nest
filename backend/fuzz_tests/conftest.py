"""Populating the database with test data."""

import pytest
from django.apps import apps
from model_bakery import baker


@pytest.fixture(scope="session")
def populate_db():
    """Fixture to populate the database with test data."""
    # Create test data for the models you want to test
    all_models = apps.get_models()
    for model in all_models:
        # Skip models that are not relevant for the tests
        if model.__name__ in ["BulkSaveModel", "TimestampedModel"]:
            continue
        # Create a few instances of each model
        baker.make(model, _quantity=5)
