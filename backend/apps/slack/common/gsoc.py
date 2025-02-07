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
)

SEPTEMBER = 9

now = timezone.now()
previous_gsoc_year = now.year if now.month > SEPTEMBER else now.year - 1
projects_url = get_absolute_url("projects")

GSOC_GENERAL_INFORMATION_BLOCKS = (
    markdown(
        f"🚀 *Getting Started with OWASP GSoC*{2*NL}"
        f"  • Join the <{OWASP_GSOC_CHANNEL_ID}> and <{OWASP_CONTRIBUTE_CHANNEL_ID}> channels "
        f"if you haven't done it yet for suggestions and tips on how to get started.{2*NL}"
        f"  • Explore previous years GSoC projects by using corresponding tags, (e.g. "
        f"`gsoc{previous_gsoc_year}`, `gsoc{previous_gsoc_year -1 }`) "
        f"on <{projects_url}?q=gsoc{previous_gsoc_year}|OWASP Nest> as they are more likely to "
        f"participate in GSoC again.{2*NL}"
        f"  • Run `/contribute --start` to get more information on how to contribute to OWASP."
    ),
)

GSOC_2025_MILESTONES_URL = (
    "https://github.com/OWASP/Nest/issues?"
    "q=is%3Aissue%20state%3Aopen%20label%3Agsoc2025%20%20sort%3Aupdated-desc"
)

GSOC_2025_MILESTONES = (
    markdown(
        f":exclamation: *<{settings.SITE_URL}|OWASP Nest>* is focused on solving real-world "
        "challenges that will help take the OWASP organization to the next level. Each milestone "
        "is designed to tackle key problems, making OWASP more efficient, accessible, and "
        f"impactful.{2*NL}"
        f"*<{GSOC_2025_MILESTONES_URL}|Here are the key milestones for GSoC 2025>*:{2*NL}"
        "  • *OWASP Contribution Hub*: Aiming to streamline the onboarding process and connect "
        "contributors with mentors and impactful projects. This milestone focuses on improving "
        f"collaboration within the OWASP community.{2*NL}"
        "  • *OWASP Nest API*: The development of REST and GraphQL API endpoints for OWASP "
        "Projects, Chapters, Events, and Committees. This milestone will standardize data access "
        f"across OWASP's resources.{2*NL}"
        "  • *OWASP Nest Kubernetes Adoption*: This milestone focuses on migrating the OWASP Nest "
        "application to Kubernetes, ensuring scalability, reliability, and ease of "
        f"deployment.{2*NL}"
        "  •  *OWASP Project Health Dashboard*: A dashboard for monitoring the health of OWASP "
        "Projects. This includes tracking vital metrics such as release frequency, issue "
        f"resolution, and contributor growth.{2*NL}"
        " •  *OWASP Schema*: Developing and extending a standardized schema for OWASP Projects "
        "and Chapters. This milestone aims to ensure consistency and ease of integration across "
        f"OWASP resources.{2*NL}"
        " •  *OWASP Snapshots*: Creating a summary of activities within OWASP Projects, Chapters, "
        "and Events, including new blog posts and news, to keep the community informed about "
        f"recent developments.{NL}"
    ),
    divider(),
    markdown(
        f"Join the effort at <{OWASP_PROJECT_NEST_CHANNEL_ID}|project-nest> and help shape "
        "the future :rocket:"
    ),
)
