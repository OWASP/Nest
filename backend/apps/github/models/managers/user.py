"""GitHub app user managers."""

from django.db import models

from apps.github.constants import (
    GITHUB_ACTIONS_USER_LOGIN,
    GITHUB_GHOST_USER_LOGIN,
    OWASP_FOUNDATION_LOGIN,
)


class ActiveUserManager(models.Manager):
    """Active users."""

    def get_queryset(self):
        """Get queryset of active users.

        Filters out bot users and system accounts to ensure valid user data
        for snapshot processing.
        """
        return (
            super()
            .get_queryset()
            .filter(is_bot=False)
            .exclude(
                login__in=[
                    GITHUB_ACTIONS_USER_LOGIN,
                    GITHUB_GHOST_USER_LOGIN,
                    OWASP_FOUNDATION_LOGIN,
                ]
            )
        )
