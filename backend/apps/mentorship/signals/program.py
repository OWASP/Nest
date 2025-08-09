"""Signal handler for Program post_save to clear Algolia cache."""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.utils.index import clear_algolia_cache_by_index
from apps.mentorship.models import Program

logger = logging.getLogger(__name__)
logger.warning("program.py imported and signal registered")


class ProgramPostSaveHandler:
    """Handles post_save signal for Program model to clear Algolia cache."""

    @receiver(post_save, sender=Program)
    def program_post_save_clear_algolia_cache(sender, instance, **kwargs):  # noqa: N805
        """Signal handler to clear Algolia cache for the Program index.

        The sender, instance, and kwargs arguments are provided by the post_save signal.
        """
        logger.info("Signal received for program '%s'. Clearing 'programs' index.", instance.name)
        clear_algolia_cache_by_index("programs")
