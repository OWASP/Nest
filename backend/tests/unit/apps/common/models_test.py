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

    def test_bulk_save_with_timestamps(self, mock_model, mock_objects):
        field_created = MagicMock()
        field_created.name = "nest_created_at"
        field_created.primary_key = False
        field_updated = MagicMock()
        field_updated.name = "nest_updated_at"
        field_updated.primary_key = False
        mock_model._meta.fields = [field_created, field_updated]

        fields = ["field1", "field2"]
        objs_copy = list(mock_objects)

        BulkSaveModel.bulk_save(mock_model, mock_objects, fields=fields)

        mock_obj1, mock_obj2 = objs_copy[0], objs_copy[1]
        assert mock_obj1.nest_created_at is not None
        assert mock_obj1.nest_updated_at is not None
        assert mock_obj2.nest_updated_at is not None

        mock_model.objects.bulk_update.assert_called_once_with(
            [mock_obj2],
            fields=["field1", "field2", "nest_updated_at"],
            batch_size=1000,
        )

    def test_bulk_save_with_timestamps_no_fields(self, mock_model, mock_objects):
        field_created = MagicMock()
        field_created.name = "nest_created_at"
        field_created.primary_key = False
        field_updated = MagicMock()
        field_updated.name = "nest_updated_at"
        field_updated.primary_key = False
        mock_model._meta.fields = [field_created, field_updated]

        objs_copy = list(mock_objects)

        BulkSaveModel.bulk_save(mock_model, mock_objects)

        mock_obj1, mock_obj2 = objs_copy[0], objs_copy[1]
        assert mock_obj1.nest_created_at is not None
        assert mock_obj1.nest_updated_at is not None
        assert mock_obj2.nest_updated_at is not None

        mock_model.objects.bulk_update.assert_called_once_with(
            [mock_obj2],
            fields=["nest_created_at", "nest_updated_at"],
            batch_size=1000,
        )
