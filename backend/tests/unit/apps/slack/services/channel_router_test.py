"""Tests for the channel_router service."""

import pytest

from apps.slack.constants import (
    OWASP_APPSEC_CHANNEL_ID,
    OWASP_ASKOWASP_CHANNEL_ID,
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_DEVSECOPS_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
    OWASP_JOBS_CHANNEL_ID,
    OWASP_MENTORS_CHANNEL_ID,
    OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
    OWASP_PROJECT_NETTACKER_CHANNEL_ID,
    OWASP_PROJECT_THREAT_DRAGON_CHANNEL_ID,
    OWASP_SPONSORSHIP_CHANNEL_ID,
    OWASP_THREAT_MODELING_CHANNEL_ID,
)
from apps.slack.services.channel_router import route


class TestChannelRouter:
    """Unit tests for the channel_router.route() function."""

    @pytest.mark.parametrize(
        "message",
        ["what is juice shop?", "how do I use JuiceShop?", "tell me about webgoat"],
    )
    def test_routes_juice_shop(self, message):
        """Route Juice Shop queries to the correct channel."""
        result = route(message)
        assert result is not None
        channel_id, label = result
        assert channel_id == OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID
        assert label == "project-juice-shop"

    @pytest.mark.parametrize(
        "message", ["how does nettacker work?", "NETTACKER scanning tutorial"]
    )
    def test_routes_nettacker(self, message):
        """Route Nettacker queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_PROJECT_NETTACKER_CHANNEL_ID

    @pytest.mark.parametrize(
        "message", ["threat dragon setup", "how do I use ThreatDragon?"]
    )
    def test_routes_threat_dragon(self, message):
        """Route Threat Dragon queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_PROJECT_THREAT_DRAGON_CHANNEL_ID

    @pytest.mark.parametrize(
        "message", ["how do I contribute to nest?", "NestBot not responding"]
    )
    def test_routes_nest(self, message):
        """Route Nest/NestBot queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_PROJECT_NEST_CHANNEL_ID

    @pytest.mark.parametrize(
        "message", ["how do I apply for GSoC?", "google summer of code owasp"]
    )
    def test_routes_gsoc(self, message):
        """Route GSoC queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_GSOC_CHANNEL_ID

    @pytest.mark.parametrize(
        "message", ["how to contribute to OWASP?", "contributing guidelines"]
    )
    def test_routes_contribute(self, message):
        """Route contribution queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_CONTRIBUTE_CHANNEL_ID

    @pytest.mark.parametrize(
        "message", ["any security jobs available?", "OWASP hiring"]
    )
    def test_routes_jobs(self, message):
        """Route job queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_JOBS_CHANNEL_ID

    @pytest.mark.parametrize(
        "message", ["looking for a mentor", "OWASP mentorship program"]
    )
    def test_routes_mentors(self, message):
        """Route mentorship queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_MENTORS_CHANNEL_ID

    @pytest.mark.parametrize("message", ["how to sponsor OWASP?", "donate to owasp"])
    def test_routes_sponsorship(self, message):
        """Route sponsorship queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_SPONSORSHIP_CHANNEL_ID

    @pytest.mark.parametrize(
        "message", ["how to do threat modeling?", "STRIDE threat modelling"]
    )
    def test_routes_threat_modeling(self, message):
        """Route threat modeling queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_THREAT_MODELING_CHANNEL_ID

    @pytest.mark.parametrize(
        "message", ["what is devsecops?", "DevSecOps pipeline security"]
    )
    def test_routes_devsecops(self, message):
        """Route DevSecOps queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_DEVSECOPS_CHANNEL_ID

    @pytest.mark.parametrize(
        "message", ["what is appsec?", "OWASP top 10 vulnerabilities"]
    )
    def test_routes_appsec(self, message):
        """Route appsec queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_APPSEC_CHANNEL_ID

    @pytest.mark.parametrize(
        "message", ["is there an OWASP chapter in Berlin?", "local chapter meeting"]
    )
    def test_routes_chapter(self, message):
        """Route chapter queries."""
        result = route(message)
        assert result is not None
        assert result[0] == OWASP_ASKOWASP_CHANNEL_ID

    @pytest.mark.parametrize(
        "message",
        [
            "what is OWASP?",
            "who maintains the cheat sheet series?",
            "how do I report a security issue?",
        ],
    )
    def test_returns_none_for_general_questions(self, message):
        """Return None for general OWASP questions."""
        assert route(message) is None

    def test_returns_none_for_empty_string(self):
        """Return None for empty message."""
        assert route("") is None

    def test_case_insensitive_matching(self):
        """Match keywords case-insensitively."""
        assert route("JUICE SHOP") is not None
        assert route("juice shop") is not None
        assert route("Juice Shop") is not None

    def test_returns_tuple_with_channel_id_and_label(self):
        """Return a (channel_id, label) tuple on match."""
        result = route("gsoc application")
        assert isinstance(result, tuple)
        assert len(result) == 2
