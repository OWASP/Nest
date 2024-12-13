"""Slack bot shared information for contributing instructions."""

from apps.common.utils import get_absolute_url
from apps.slack.blocks import markdown
from apps.slack.constants import (
    NL,
    NLNL,
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
    OWASP_PROJECT_THREAT_DRAGON_CHANNEL_ID,
)

project_issues_url = get_absolute_url("project-issues")
projects_url = get_absolute_url("projects")

CONTRIBUTE_GENERAL_INFORMATION_BLOCKS = (
    markdown(
        f"🚀 *Getting Started with OWASP Contributions*{NLNL}"
        f"  • Join the <#{OWASP_CONTRIBUTE_CHANNEL_ID}> if you haven't done it yet for "
        f"contribution suggestions and tips on how to get started.{NLNL}"
        "  • Search for issues relevant to your technical skills and interests, "
        f"such as <{project_issues_url}?q=MERN|MERN stack>, "
        f"<{project_issues_url}?q=python|Python>, "
        f"<{project_issues_url}?q=javascript|JavaScript>, "
        f"<{project_issues_url}?q=kubernetes|Kubernetes>, or any other topic you are "
        "interested in. To get the full list of current project issues see each project's "
        "GitHub Issues section.",
    ),
    markdown(
        f"📢 *Finding the Right Slack Channels*{NLNL}"
        "Each project has its own dedicated channel prefixed with `#project-` in the OWASP "
        f"Slack workspace. For example:{NL}"
        f"  • <#{OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID}> - project Juice Shop.{NL}"
        f"  • <#{OWASP_PROJECT_NEST_CHANNEL_ID}> - project Nest.{NL}"
        f"  • <#{OWASP_PROJECT_THREAT_DRAGON_CHANNEL_ID}> - project Thread Dragon.{NL}"
        f"{NL}"
        "Some projects, like BLT or CycloneDX, also have their own Slack workspaces -- be sure "
        "to check if the project you're interested in has additional communication channels."
    ),
    markdown(
        f"👥 *Identifying Project Leaders, Contributors, and Ongoing Project Activity*{NLNL}"
        "  • Check the Leaders section on the official <https://owasp.org/projects|OWASP site> "
        f"or <{projects_url}|OWASP Nest Projects> page to identify project leaders. Normally, "
        "a project has at least two leaders. Having multiple project leaders who are not all "
        "employed by the same company is a good practice.>{NLNL}"
        "  • Review the project's codebase commit history on GitHub to find active contributors "
        f"who can also provide valuable guidance and insights.{NLNL}"
        "  • Review the project's channel history to get understanding of recent and ongoing "
        "activity."
    ),
    markdown(
        f"📌 *Tips for Effective Communication*{NLNL}"
        f"  • Check the channel's pinned messages for important announcements.{NLNL}"
        f"  • Ask project-specific questions in their respective `#project-` channels only.{NLNL}"
        f"  • Feel free to introduce yourself in the channel, but avoid sharing personal "
        f"information like your email address.{NLNL}"
    ),
    markdown(
        f"🛠️ *Making Your First Contribution*{NLNL}"
        "  • After identifying a project you want to work on, inspect the list of open issues "
        f"-- either directly on GitHub or using <{project_issues_url}|OWASP Nest>.{NLNL}"
        "  • Let project leaders and other contributors know that you're interested in working on "
        "an existing issue by commenting it or suggest a new one. If you're suggesting your own "
        "idea, please double-check that a similar or identical issue does not already exist. "
        f"Ideally, get the issue assigned to you to avoid overlaps.{NLNL}"
        "  • Familiarize yourself with the project's contributing guidelines, style guides, "
        f"and code standards to ensure your work aligns with the project's expectations.{NLNL}"
        "  • Resolve the issue and submit a pull request when ready. If the issue is not "
        "trivial or takes more time for any other reason, make sure to keep the project leaders "
        f"updated on your progress.{NL}"
        "Remember, communication is key to a smooth contribution process and will help you "
        "succeed in your journey."
    ),
)
