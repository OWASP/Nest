"""Github app label model."""

#!/usr/bin/env python3
from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.common import NodeModel


class Label(BulkSaveModel, NodeModel, TimestampedModel):
    """Label model."""

    class Meta:
        db_table = "github_labels"
        verbose_name_plural = "Labels"

    name = models.CharField(verbose_name="Name", max_length=100)
    description = models.CharField(verbose_name="Description", max_length=200)
    color = models.CharField(verbose_name="Color", max_length=6, default="")
    sequence_id = models.PositiveBigIntegerField(verbose_name="Label ID", default=0)
    is_default = models.BooleanField(verbose_name="Is default", default=False)

    def __str__(self):
        """Label human readable representation."""
        return f"{self.name} ({self.description})" if self.description else self.name

    def from_github(self, gh_label):
        """Update instance based on GitHub label data."""
        # TODO(arkid15r): uncomment after PyGithub supports all fields.
        field_mapping = {
            "color": "color",
            "description": "description",
            # "is_default": "default",
            "name": "name",
            # "sequence_id": "id",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_label, gh_field)
            if value is not None:
                setattr(self, model_field, value)

    @staticmethod
    def bulk_save(labels):
        """Bulk save labels."""
        BulkSaveModel.bulk_save(Label, labels)

    @staticmethod
    def update_data(gh_label, save=True):
        """Update label data."""
        label_node_id = Label.get_node_id(gh_label)
        try:
            label = Label.objects.get(node_id=label_node_id)
        except Label.DoesNotExist:
            label = Label(node_id=label_node_id)

        label.from_github(gh_label)
        if save:
            label.save()

        return label
