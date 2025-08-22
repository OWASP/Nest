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

    if isinstance(auth, tuple):
        # If auth is a tuple, it contains (authorization_url, state)
        authorization_url = auth[0]
        return [
            markdown(f"Please sign in to Google: <{authorization_url}|Click here>"),
        ]

    return [markdown("✅ You are already signed in to Google.")]
