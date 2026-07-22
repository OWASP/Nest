"""OWASP app Dataloaders."""

from apps.owasp.api.internal.dataloaders.board_of_directors import (
    get_board_of_directors_loaders,
)
from apps.owasp.api.internal.dataloaders.member_snapshot import (
    get_member_snapshot_loaders,
)
from apps.owasp.api.internal.dataloaders.project import get_project_loaders


def get_owasp_dataloaders() -> dict[str, object]:
    """Return a dict of dataloader instances for OWASP API resolvers."""
    loaders: dict[str, object] = {}
    loaders.update(get_board_of_directors_loaders())
    loaders.update(get_member_snapshot_loaders())
    loaders.update(get_project_loaders())
    return loaders
