from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .conversation import Conversation

class EntityChannel(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey('content_type', 'object_id')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    is_main_channel = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)
    kind = models.CharField(max_length=32, default='slack')

    class Meta:
        unique_together = ('content_type', 'object_id', 'conversation')
        verbose_name = 'Entity Channel'
        verbose_name_plural = 'Entity Channels'

    def __str__(self):
        return f"{self.entity} - {self.conversation} ({self.kind})"
