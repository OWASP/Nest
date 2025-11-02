"""GitHub app release managers."""

from django.db import models


class ActiveReleaseManager(models.Manager):
    """Active releases manager."""

    def get_queryset(self):
        """Get queryset of active releases.
        
        Filters out draft and pre-releases, and ensures repository exists.
        """
        return (
            super()
            .get_queryset()
            .select_related("repository")
            .filter(
                is_draft=False,
                is_pre_release=False,
                repository__is_empty=False,
            )
        )
