"""OWASP app Dataloaders."""

from apps.owasp.api.internal.dataloaders.board_of_directors import (
    get_board_of_directors_loaders,
)
from apps.owasp.api.internal.dataloaders.project import get_project_loaders
from apps.owasp.api.internal.dataloaders.snapshot import get_snapshot_loaders


def get_owasp_dataloaders() -> dict[str, object]:
    """Return a dict of dataloader instances for OWASP API resolvers."""
    loaders: dict[str, object] = {}
    loaders.update(get_board_of_directors_loaders())
    loaders.update(get_project_loaders())
    loaders.update(get_snapshot_loaders())
    return loaders
