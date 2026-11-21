import pytest


@pytest.fixture(
    params=[
        (1, 1, []),
        (2, 1, [("Next", "2")]),
        (2, 2, [("Previous", "1")]),
        (3, 1, [("Next", "2")]),
        (3, 2, [("Previous", "1"), ("Next", "3")]),
        (3, 3, [("Previous", "2")]),
    ],
    ids=["one-page", "two-first", "two-last", "three-first", "three-middle", "three-last"],
)
def pagination_case(request):
    """Page counts, current pages and expected button targets for each handler."""
    return request.param
