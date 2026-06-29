"""Mentorship app Dataloaders."""

from strawberry.dataloader import DataLoader

from apps.github.models.user import User
from apps.mentorship.api.internal.dataloaders.admin import get_admin_loaders
from apps.mentorship.api.internal.dataloaders.interested_users import get_interested_users_loaders


def get_mentorship_dataloaders() -> dict[str, object]:
    """Return a dict of dataloader instances for Mentorship API resolvers."""
    loaders: dict[str, object] = {}
    loaders.update(get_admin_loaders())
    loaders.update(get_interested_users_loaders())
    return loaders
