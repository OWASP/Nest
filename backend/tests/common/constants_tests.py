from apps.common.constants import DAY_IN_SECONDS


class TestConstant:
    def print_day_in_seconds(self):
        assert isinstance(DAY_IN_SECONDS, int)
