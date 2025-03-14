"""Typesense client configuration and schema definition."""

import logging

import typesense
from django.apps import apps
from django.conf import settings
from typesense.exceptions import TypesenseClientError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Registry for indexes
REGISTERED_INDEXES = {}


def register(model_name):
    """Register a model schema."""

    def wrapper(cls):
        instance = cls()
        if not hasattr(instance, "index_name") or not hasattr(instance, "schema"):
            message = f"{cls.__name__} must have 'index_name' and 'schema' attributes."
            raise AttributeError(message)
        REGISTERED_INDEXES[model_name] = instance
        logging.info("Registered index: %s", model_name)
        return cls

    return wrapper


class Typesense:
    """Typesense client manager."""

    @staticmethod
    def get_client():
        """Return an instance of Typesense client."""
        return typesense.Client(
            {
                "api_key": settings.TYPESENSE_API_KEY,
                "nodes": [
                    {
                        "host": settings.TYPESENSE_HOST,
                        "port": settings.TYPESENSE_PORT,
                        "protocol": "http",
                    }
                ],
                "connection_timeout_seconds": 5,
            }
        )


class IndexBase:
    """Base class for Typesense indexes."""

    index_name = None
    schema = {}

    def get_model(self):
        """Retrieve the Django model associated with the index name."""
        for app_config in apps.get_app_configs():
            try:
                if self.index_name == "user":
                    model = apps.get_model("github", "User")
                else:
                    model = app_config.get_model(self.index_name)

                if model:
                    return model

            except LookupError:
                continue
        raise ValueError(self.index_name)

    def create_collection(self):
        """Create collection if it doesn't exist."""
        client = Typesense.get_client()
        try:
            try:
                client.collections[self.index_name].delete()
            except TypesenseClientError as e:
                logging.info("%s", e)
            client.collections.create(self.schema)
            logging.info("Created collection: %s", self.index_name)
        except TypesenseClientError:
            logging.exception("Error while creating collection %s", self.index_name)

    def populate_collection(self):
        """Populate Typesense collection with data from the database."""
        client = Typesense.get_client()
        model = self.get_model()
        queryset = model.objects.filter().iterator()

        data = (self.prepare_document(obj) for obj in queryset if obj.is_indexable)

        if not data:
            logging.info("No data found for {self.index_name}. Skipping... .")
            return

        try:
            response = client.collections[self.index_name].documents.import_(
                data, {"action": "upsert"}
            )

            errors = [item["error"] for item in response if "error" in item]
            if errors:
                logging.info("Errors while populating '%s': %s", self.index_name, errors)
            logging.info("Populated '%s'", self.index_name)
        except TypesenseClientError:
            logging.exception("Error while populating '%s'", self.index_name)

    def prepare_document(self, obj):
        """Convert model instance to a dictionary for Typesense."""
        message = "Subclasses must implement prepare_document()"
        raise NotImplementedError(message)
