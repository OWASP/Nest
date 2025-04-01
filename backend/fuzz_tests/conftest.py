import pytest
from django.apps import apps
from model_bakery import baker
from django.test import override_settings
from django.conf import settings

@override_settings(DATABASES={"default": settings.DATABASES["fuzz_tests"]})
@pytest.fixture(autouse=True)
def populate_db():
    """Fixture to populate the database with test data."""
    # Create test data for the models you want to test
    all_models = apps.get_models()
    for model in all_models:
        # Skip models that are not relevant for the tests
        if model.__name__ in ["BulkSaveModel", "TimestampedModel"]:
            continue
        # Create a few instances of each model
        try:
            baker.make(model, _quantity=5)
        except Exception as e:
            print(f"Error creating instances for {model.__name__}: {e}")
