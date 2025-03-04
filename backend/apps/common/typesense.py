"""Typesense client configuration and schema definition."""

import typesense
from django.conf import settings
import logging
from django.apps import apps

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Registry for indexes
REGISTERED_INDEXES = {}

def register(model_name):
    """Decorator to register a model schema."""
    def wrapper(cls):
        instance = cls()
        if not hasattr(instance, "index_name") or not hasattr(instance, "schema"):
            raise AttributeError(f"{cls.__name__} must have 'index_name' and 'schema' attributes.")
        REGISTERED_INDEXES[model_name] = instance
        logging.info(f"Registered index: {model_name}")
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
        model = apps.get_model("owasp", self.index_name)
        if not model:
            raise ValueError(f"Model '{self.index_name}' not found in Django apps.")
        return model

    def create_collection(self):
        """Create collection if it doesn't exist."""
        client = Typesense.get_client()
        try:
            client.collections[self.index_name].retrieve()
            logging.info(f"Collection '{self.index_name}' already exists.")
        except:
            client.collections.create(self.schema)
            logging.info(f"Created collection: {self.index_name}")
            
    def populate_collection(self):
        """Populate Typesense collection with data from the database."""
        client = Typesense.get_client()
        model = self.get_model()
        queryset = model.objects.all()
        
        data = [self.prepare_document(obj) for obj in queryset]

        if not data:
            logging.info(f"No data found for {self.index_name}. Skipping population.")
            return
        
        try:
            client.collections[self.index_name].documents.import_(data, {'action': 'upsert'})
            logging.info(f"Populated '{self.index_name}' with {len(data)} records.")
        except Exception as e:
            logging.error(f"Error populating '{self.index_name}': {e}")

    def prepare_document(self, obj):
        """Convert model instance to a dictionary for Typesense."""
        raise NotImplementedError("Subclasses must implement prepare_document()")