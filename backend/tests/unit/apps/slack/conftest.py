"""Shared Slack unit-test helpers."""

from unittest.mock import Mock


def enabled_workspace(**kwargs: object):
    """Return a workspace mock with content reporting enabled."""
    workspace = Mock(**kwargs)
    workspace.is_content_reporting_enabled = True
    return workspace


def disabled_workspace(**kwargs: object):
    """Return a workspace mock with content reporting disabled."""
    workspace = Mock(**kwargs)
    workspace.is_content_reporting_enabled = False
    return workspace
