"""Slack bot shared information for GSoC instructions."""

from django.conf import settings
from django.utils import timezone

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.blocks import divider, markdown
from apps.slack.constants import (
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
    OWASP_SPONSORSHIP_CHANNEL_ID,
)

MARCH = 3

now = timezone.now()
gsoc_year = now.year if now.month >= MARCH else now.year - 1
projects_url = get_absolute_url("/projects")

GSOC_GENERAL_INFORMATION_BLOCKS = (
    markdown(
        f"🚀 *Getting Started with OWASP GSoC*{2 * NL}"
        f"  • Join the <{OWASP_GSOC_CHANNEL_ID}> and <{OWASP_CONTRIBUTE_CHANNEL_ID}> channels "
        f"if you haven't done it yet for suggestions and tips on how to get started.{2 * NL}"
        f"  • Explore previous years GSoC projects by using corresponding tags, (e.g. "
        f"`gsoc{gsoc_year}`, `gsoc{gsoc_year - 1}`) "
        f"on <{projects_url}?q=gsoc{gsoc_year}|OWASP Nest> as they are more likely to "
        f"participate in GSoC again.{2 * NL}"
        f"  • Run `/contribute --start` to get more information on how to contribute to OWASP."
    ),
)

OWASP_NEST_MILESTONES_URL = "https://github.com/OWASP/Nest/milestones"

OWASP_NEST_MILESTONES = (
    markdown(
        f":exclamation: *<{settings.SITE_URL}|OWASP Nest>* is focused on solving real-world "
        "challenges that will help take the OWASP organization to the next level. Each milestone "
        "is designed to tackle key problems, making OWASP more efficient, accessible, and "
        f"impactful.{2 * NL}"
        f"Here are the key *<{OWASP_NEST_MILESTONES_URL}|milestones>* that were accepted as part "
        f"of the OWASP Nest project for *GSoC 2025*:{2 * NL}"
        "  • *OWASP Contribution Hub*: Aiming to streamline the onboarding process and connect "
        "contributors with mentors and impactful projects. This milestone focuses on improving "
        f"collaboration within the OWASP community.{2 * NL}"
        "  • *OWASP Nest API*: The development of REST and GraphQL API endpoints for OWASP "
        "Projects, Chapters, Events, and Committees. This milestone will standardize data access "
        f"across OWASP's resources.{2 * NL}"
        "  • *OWASP NestBot AI Assistant*: Develop an AI-powered Slack assistant, NestBot, that "
        " acts as an auto-responder for frequently asked questions, intelligently routes queries "
        f"to the appropriate OWASP channels, and helps users navigate the OWASP community.{2 * NL}"
        " •  *OWASP Schema*: Developing and extending a standardized schema for OWASP Projects "
        "and Chapters. This milestone aims to ensure consistency and ease of integration across "
        f"OWASP resources.{2 * NL}"
    ),
    divider(),
    markdown(
        "No other OWASP project received more than 3 slots this year, placing OWASP Nest among "
        "the most active OWASP initiatives in this year's program. With Google reporting an "
        "overall acceptance rate of around 8%, this is a strong reflection of the quality of the "
        f"proposals and the growing impact of the OWASP Nest project.{2 * NL}"
    ),
    markdown(
        ":bangbang: For projects that were not accepted this year we've launched a dedicated "
        "sponsorship program to support them. We're looking for high-quality contributors to help "
        "us with those project ideas. "
        f"Feel free to join <{OWASP_SPONSORSHIP_CHANNEL_ID}|sponsorship> channel to learn more "
        f"about it.{NL}"
    ),
    divider(),
    markdown(
        f"Join the effort at <{OWASP_PROJECT_NEST_CHANNEL_ID}|project-nest> and help shape "
        "the future -- we're so looking forward to participating in GSoC 2026!"
    ),
)
