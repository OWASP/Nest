from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.interested_users import get_interested_users_loader

INTERESTED_USERS_LOADER = "interested_users_loader"


def get_github_dataloaders() -> dict[str, DataLoader]:
    """Return a dict of dataloader instances for GitHub API resolvers."""
    return {
        INTERESTED_USERS_LOADER: get_interested_users_loader(),
    }
