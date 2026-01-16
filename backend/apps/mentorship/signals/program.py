"""Signal handler for Program post_save to clear Algolia and GraphQL cache."""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.utils.index import clear_index_cache, invalidate_program_graphql_cache
from apps.mentorship.models import Program

logger = logging.getLogger(__name__)


class ProgramPostSaveHandler:
    """Handles post_save signal for Program model to clear Algolia and GraphQL cache."""

    @receiver(post_save, sender=Program)
    def program_post_save_clear_algolia_cache(sender, instance, **kwargs):  # noqa: N805
        """Signal handler to clear Algolia cache for the Program index.

        The sender, instance, and kwargs arguments are provided by the post_save signal.
        """
        logger.info("Signal received for program '%s'. Clearing 'programs' index.", instance.name)
        clear_index_cache("programs")

    @receiver(post_save, sender=Program)
    def program_post_save_clear_graphql_cache(sender, instance, **kwargs):  # noqa: N805
        """Signal handler to clear GraphQL cache for the program.

        This ensures that when a program's status changes (e.g. from published to draft),
        the cached GraphQL response is cleared immediately.
        """
        logger.info(
            "Signal received for program '%s' (status: %s). Clearing GraphQL cache.",
            instance.name,
            instance.status,
        )
        invalidate_program_graphql_cache(instance.key)
