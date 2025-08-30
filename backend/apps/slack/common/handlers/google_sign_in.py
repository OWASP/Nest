"""Slack Google sign in handler."""

from apps.slack.blocks import markdown


def get_blocks(slack_user_id: str):
    """Get the rendered blocks for Google sign-in.

    Args:
        slack_user_id (str): The Slack user ID.

    Returns:
        list: The rendered blocks for Google sign-in.

    """
    from apps.nest.models.google_account_authorization import GoogleAccountAuthorization

    auth = GoogleAccountAuthorization.authorize(slack_user_id)

    return [
        markdown(
            f"Please sign in with Google on <{auth[0]}|this page>"
            if isinstance(auth, tuple)
            else "✅ You are already signed in."
        ),
    ]
