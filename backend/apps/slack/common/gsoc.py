"""Slack bot shared information for GSoC instructions."""

from django.utils import timezone

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.blocks import markdown
from apps.slack.constants import (
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
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
