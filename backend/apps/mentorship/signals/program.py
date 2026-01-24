"""Signal handler for Program post_save to clear Algolia cache."""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.utils.index import clear_index_cache
from apps.mentorship.models import Program

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Program)
def program_post_save_clear_algolia_cache(sender, instance, **kwargs):  # noqa: ARG001
    """Signal handler to clear Algolia cache for the Program index."""
    logger.info("Signal received for program '%s'. Clearing 'programs' index.", instance.name)
    clear_index_cache("programs")
