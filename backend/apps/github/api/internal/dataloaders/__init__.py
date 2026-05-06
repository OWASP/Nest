from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.interested_users import make_interested_users_loader

INTERESTED_USERS_LOADER = "interested_users_loader"


def make_github_dataloaders() -> dict[str, DataLoader]:
    """Return a dict of dataloader instances for GitHub API resolvers."""
    return {
        INTERESTED_USERS_LOADER: make_interested_users_loader(),
    }
