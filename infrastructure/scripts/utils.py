"""Infrastructure utilities."""

import os
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def temporary_env(name: str, value: str) -> Iterator[None]:
    """Set an environment variable for the duration of the context."""
    previous = os.environ.get(name, None)
    os.environ[name] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = previous
