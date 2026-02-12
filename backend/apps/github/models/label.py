"""Github app label model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.common import NodeModel


class Label(BulkSaveModel, NodeModel, TimestampedModel):
    """Label model."""

    class Meta:
        """Model options."""

        db_table = "github_labels"
        verbose_name_plural = "Labels"

    name = models.CharField(verbose_name="Name", max_length=100)
    description = models.CharField(verbose_name="Description", max_length=200)
    color = models.CharField(verbose_name="Color", max_length=6, default="")
    sequence_id = models.PositiveBigIntegerField(verbose_name="Label ID", default=0)
    is_default = models.BooleanField(verbose_name="Is default", default=False)

    def __str__(self):
        """Return a human-readable representation of the label.

        Returns
            str: The name and description of the label.

        """
        return f"{self.name} ({self.description})" if self.description else self.name

    def from_github(self, gh_label) -> None:
        """Update the instance based on GitHub label data.

        Args:
            gh_label (github.Label.Label): The GitHub label object.

        """
        field_mapping = {
            "color": "color",
            "description": "description",
            "name": "name",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_label, gh_field)
            if value is not None:
                setattr(self, model_field, value)

    @staticmethod
    def bulk_save(labels, *, fields=None) -> None:  # type: ignore[override]
        """Bulk save labels."""
        BulkSaveModel.bulk_save(Label, labels, fields=fields)

    @staticmethod
    def update_data(gh_label, *, save: bool = True) -> "Label":
        """Update label data.

        Args:
            gh_label (github.Label.Label): The GitHub label object.
            save (bool, optional): Whether to save the instance.

        Returns:
            Label: The updated or created label instance.

        """
        label_node_id = Label.get_node_id(gh_label)
        try:
            label = Label.objects.get(node_id=label_node_id)
        except Label.DoesNotExist:
            label = Label(node_id=label_node_id)

        label.from_github(gh_label)
        if save:
            label.save()

        return label
