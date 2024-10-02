import pytest

from apps.common.utils import join_values


class TestUtils:
    @pytest.mark.parametrize(
        ("values", "delimiter", "expected"),
        [
            (("1", "2", "3"), " ", "1 2 3"),
            (("1", "2", "3"), ",", "1,2,3"),
        ],
    )
    def test_join_values(self, values, delimiter, expected):
        assert join_values(values, delimiter=delimiter) == expected
