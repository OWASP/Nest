from strawberry.dataloader import DataLoader

from apps.github.api.internal.dataloaders.interested_users import make_interested_users_loader


def make_github_dataloaders() -> dict[str, DataLoader]:
    """Return a dict of dataloader instances for GitHub API resolvers."""
    return {
        "interested_users_loader": make_interested_users_loader(),
    }
