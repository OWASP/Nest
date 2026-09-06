"""Tests for OWASP Board Candidate mutation input helpers."""

import datetime

import pytest

from apps.owasp.api.internal.mutations.common import MIN_ELECTION_YEAR, validate_election_year


class TestValidateYear:
    """Tests for validate_election_year."""

    def test_accepts_current_year(self):
        current = datetime.datetime.now(tz=datetime.UTC).year
        assert validate_election_year(current) == current

    def test_accepts_next_year(self):
        next_year = datetime.datetime.now(tz=datetime.UTC).year + 1
        assert validate_election_year(next_year) == next_year

    def test_accepts_min_year(self):
        assert validate_election_year(MIN_ELECTION_YEAR) == MIN_ELECTION_YEAR

    def test_rejects_year_below_minimum(self):
        with pytest.raises(ValueError, match="Year must be between"):
            validate_election_year(MIN_ELECTION_YEAR - 1)

    def test_rejects_year_far_in_future(self):
        far_future = datetime.datetime.now(tz=datetime.UTC).year + 2
        with pytest.raises(ValueError, match="Year must be between"):
            validate_election_year(far_future)
