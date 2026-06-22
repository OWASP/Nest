from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.repository import get_repository_loaders
from apps.github.models.repository import Repository


def get_github_dataloaders() -> dict[
    str,
    DataLoader[int, Repository | None] | DataLoader[int, str],
]:
    """Return a dict of dataloader instances for GitHub API resolvers."""
    loaders: dict[
        str,
        DataLoader[int, Repository | None] | DataLoader[int, str],
    ] = {}
    loaders.update(get_repository_loaders())
    return loaders
