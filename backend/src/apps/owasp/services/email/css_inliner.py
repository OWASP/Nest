"""CSS inlining for HTML emails."""

from premailer import Premailer


def inline_css(html: str) -> str:
    """Copy CSS from <style> blocks onto matching tags as inline styles."""
    return Premailer(
        html,
        allow_network=False,
        disable_link_rewrites=True,
        disable_validation=True,
        remove_classes=True,
    ).transform()
