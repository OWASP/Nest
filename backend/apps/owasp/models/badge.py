
from django.db import models
from safedelete.models import SafeDeleteModel

from apps.common.models import TimestampedModel


class Badge(TimestampedModel, SafeDeleteModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text='Name of the badge.'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text='A short description of the badge.'
    )
    weight = models.IntegerField(
        default=0,
        help_text='A weight to sort badges by.'
    )
    css_class = models.CharField(
        max_length=255,
        help_text='The font-awesome css class for the badge.'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['weight', 'name'] 


