"""Slack bot policies command."""

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase


class Policies(CommandBase):
    """Slack bot /policies command."""

    def get_render_text(self, command):
        """Get the rendered text."""
        policies_list = [
            ("Chapters Policy", "https://owasp.org/www-policy/operational/chapters"),
            ("Code of Conduct", "https://owasp.org/www-policy/operational/code-of-conduct"),
            ("Committees Policy", "https://owasp.org/www-policy/operational/committees"),
            (
                "Conflict Resolution Policy",
                "https://owasp.org/www-policy/operational/conflict-resolution",
            ),
            (
                "Conflict of Interest Policy",
                "https://owasp.org/www-policy/operational/conflict-of-interest",
            ),
            ("Donations Policy", "https://owasp.org/www-policy/operational/donations"),
            ("Elections Policy", "https://owasp.org/www-policy/operational/election"),
            ("Events Policy", "https://owasp.org/www-policy/operational/events"),
            ("Expense Policy", "https://owasp.org/www-policy/operational/expense-reimbursement"),
            ("Grant Policy", "https://owasp.org/www-policy/operational/grants"),
            ("Membership Policy", "https://owasp.org/www-policy/operational/membership"),
            ("Project Policy", "https://owasp.org/www-policy/operational/projects"),
            (
                "Whistleblower & Anti-Retaliation Policy",
                "https://owasp.org/www-policy/operational/whistleblower",
            ),
        ]

        return self.get_template_file().render(
            policies=policies_list,
            NL=NL,
            SECTION_BREAK="{{ SECTION_BREAK }}",
            DIVIDER="{{ DIVIDER }}",
        )


if SlackConfig.app:
    Policies().config_command()
