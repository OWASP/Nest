"""GitHub app Dataloaders."""

from apps.github.api.internal.dataloaders.issue import get_issue_loaders
from apps.github.api.internal.dataloaders.milestone import get_milestone_loaders
from apps.github.api.internal.dataloaders.release import get_release_loaders
from apps.github.api.internal.dataloaders.repository import get_repository_loaders
from apps.github.api.internal.dataloaders.user import get_user_loaders


def get_github_dataloaders() -> dict[str, object]:
    """Return a dict of dataloader instances for GitHub API resolvers."""
    loaders: dict[str, object] = {}
    loaders.update(get_issue_loaders())
    loaders.update(get_milestone_loaders())
    loaders.update(get_release_loaders())
    loaders.update(get_repository_loaders())
    loaders.update(get_user_loaders())
    return loaders
