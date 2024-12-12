"""Slack bot shared information for GSoC participants."""

from django.utils import timezone

from apps.common.utils import get_absolute_url
from apps.slack.blocks import markdown
from apps.slack.constants import (
    OWASP_CONTRIBUTE_CHANNEL_ID,
    OWASP_GSOC_CHANNEL_ID,
    OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID,
    OWASP_PROJECT_NEST_CHANNEL_ID,
    OWASP_PROJECT_THREAT_DRAGON_CHANNEL_ID,
)

SEPTERMER = 9

now = timezone.now()
previous_gsoc_year = now.year if now.month > SEPTERMER else now.year - 1
project_issues_url = get_absolute_url("project-issues")
projects_url = get_absolute_url("projects")

GENERAL_INFORMATION_BLOCKS = (
    markdown(
        "🚀 *Getting Started with Contributions*\n"
        f"  • Join the <#{OWASP_CONTRIBUTE_CHANNEL_ID}> for contribution "
        "suggestions and tips on how to get started.\n"
        f"  • Explore previous year GSoC projects by using the _gsoc{previous_gsoc_year}_ tag "
        f"on <{projects_url}?q=gsoc{previous_gsoc_year}|OWASP Nest> as they are more likely "
        "to participate in GSoC again.\n"
        "  • Search for issues relevant to your technical skills and interests, "
        f"such as <{project_issues_url}?q=MERN|MERN stack>, "
        f"<{project_issues_url}?q=python|Python>, "
        f"<{project_issues_url}?q=javascript|JavaScript>, "
        f"<{project_issues_url}?q=kubernetes|Kubernetes>, and more. To get the full list of "
        "current project issues see each project's GitHub Issues section.",
    ),
    markdown(
        "⚙️ *Finding the Right Slack Channels*\n"
        "Each project has its own dedicated channel prefixed with #project- in the OWASP "
        "Slack workspace. For example:\n"
        f"  • <#{OWASP_PROJECT_JUICE_SHOP_CHANNEL_ID}> - Project Juice Shop.\n"
        f"  • <#{OWASP_PROJECT_NEST_CHANNEL_ID}> - Project Nest.\n"
        f"  • <#{OWASP_PROJECT_THREAT_DRAGON_CHANNEL_ID}> - Project Thread Dragon.\n"
        "\n"
        "Some projects, like BLT, also have their own Slack workspace -- be sure to check "
        "if the project you're interested in has additional communication channels."
    ),
    markdown(
        "👥 *Identifying Project Leaders, Contributors, and Ongoing Project Activity*\n"
        "  • Check the Leaders section on the official <https://owasp.org/projects|OWASP site> "
        f"or <{projects_url}|OWASP Nest> to identify project leaders.\n"
        "  • Review the project's codebase commit history on GitHub to find active contributors "
        "who can also provide valuable guidance and insights.\n"
        "  • Review the project's channel history to get understanding of recent and ongoing "
        "activity."
    ),
    markdown(
        "📌 *Tips for Effective Communication*\n"
        f"  • Check the channel's pinned messages for important announcements and "
        f"resources (especially <#{OWASP_CONTRIBUTE_CHANNEL_ID}> and "
        f"<#{OWASP_GSOC_CHANNEL_ID}> channels).\n"
        f"  • Feel free to introduce yourself in the channel, but avoid sharing personal "
        "information like your email address.\n"
        f"  • Ask project-specific questions in their respective #project- channels only.\n"
    ),
    markdown(
        "🛠️ *Making Your First Contribution*\n"
        "  • After identifying a project you want to work on, inspect the list of open issues "
        f"-- either directly on GitHub or using <{project_issues_url}|OWASP Nest>.\n"
        "  • Let project leaders and other contributors know that you're interested in working on "
        "an existing issue by commenting it or suggest a new one. If you're suggesting your own "
        "idea, please double-check that a similar or identical issue does not already exist. "
        "Ideally, get the issue assigned to you to avoid overlaps.\n"
        "  • Familiarize yourself with the project's contributing guidelines, style guides, "
        "and code standards to ensure your work aligns with the project's expectations.\n"
        "  • Resolve the issue and submit a pull request when ready. If the issue is not "
        "trivial and takes time, make sure to keep the project leaders updated on your progress.\n"
        "\n"
        "Remember, communication is key to a smooth contribution process and will help you "
        "succeed in your Google Summer of Code journey."
    ),
    markdown(
        "🎉 We're excited to have you on board, and we can't wait to see the amazing "
        "contributions you'll make! Happy contributing and good luck with your GSoC journey!"
    ),
)
