from strawberry.dataloader import DataLoader

from apps.github.models.user import User
from apps.mentorship.api.internal.dataloaders.interested_users import get_interested_users_loaders


def get_mentorship_dataloaders() -> dict[str, DataLoader[int, list[User]]]:
    """Return a dict of dataloader instances for Mentorship API resolvers."""
    loaders: dict[str, DataLoader[int, list[User]]] = {}
    loaders.update(get_interested_users_loaders())
    return loaders
