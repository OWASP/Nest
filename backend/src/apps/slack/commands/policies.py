"""Slack bot policies command."""

from apps.slack.commands.command import CommandBase


class Policies(CommandBase):
    """Slack bot /policies command."""

    def get_context(self, command):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        policies = (
            ("Chapters Policy", "https://owasp.org/www-policy/operational/chapters"),
            ("Code of Conduct", "https://owasp.org/www-policy/operational/code-of-conduct"),
            ("Committees Policy", "https://owasp.org/www-policy/operational/committees"),
            (
                "Conflict Resolution Policy",
                "https://owasp.org/www-policy/operational/conflict-resolution",
            ),
            ("Copyright Policy", "https://owasp.org/www-policy/operational/copyright"),
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
            ("Privacy Policy", "https://owasp.org/www-policy/operational/privacy"),
            (
                "Whistleblower Policy",
                "https://owasp.org/www-policy/operational/whistleblower",
            ),
        )

        return {
            **super().get_context(command),
            "POLICIES": policies,
        }
