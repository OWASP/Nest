from unittest.mock import MagicMock

import pytest

from apps.common.models import BulkSaveModel, models


class TestBulkSaveModel:
    @pytest.fixture
    def mock_model(self):
        class MockModel(models.Model):
            class Meta:
                abstract = True

        MockModel.objects = MagicMock()
        return MockModel

    @pytest.fixture
    def mock_objects(self):
        mock_obj1 = MagicMock()
        mock_obj1.id = None
        mock_obj2 = MagicMock()
        mock_obj2.id = 1
        return [mock_obj1, mock_obj2]

    def test_bulk_save(self, mock_model, mock_objects):
        fields = ["field1", "field2"]

        BulkSaveModel.bulk_save(mock_model, mock_objects, fields=fields)

        mock_model.objects.bulk_create.assert_called_once()
        mock_model.objects.bulk_update.assert_called_once()

        assert len(mock_objects) == 0

    def test_bulk_save_default_fields(self, mock_model, mock_objects):
        BulkSaveModel.bulk_save(mock_model, mock_objects)

        mock_model.objects.bulk_create.assert_called_once()
        mock_model.objects.bulk_update.assert_called_once()

        assert len(mock_objects) == 0
