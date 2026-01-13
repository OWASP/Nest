"""Common utilities for AI tools."""

from collections.abc import Callable

from apps.ai.template_loader import env


def render_template(
    template_path: str,
    context_factory: Callable[[], dict] | None = None,
    **kwargs: str,
) -> str:
    """Render a Jinja2 template.

    This function handles template loading and rendering, reducing code repetition.
    It can be called directly from tool functions.

    Args:
        template_path: Path to the Jinja2 template relative to templates directory
        context_factory: Optional callable that returns a dict of template variables.
            If None, the template is rendered without variables.
        **kwargs: Optional keyword arguments to pass as template variables.
            If both context_factory and kwargs are provided, kwargs take precedence.

    Returns:
        Rendered template string (stripped)

    Example:
        from crewai.tools import tool

        @tool("Get contribution information")
        def get_contribute_info() -> str:
            \"\"\"Tool docstring.\"\"\"
            return render_template("agents/contribution/tools/get_contribute_info.jinja")

        @tool("Get GSoC information")
        def get_gsoc_info() -> str:
            \"\"\"Tool docstring.\"\"\"
            return render_template(
                "agents/contribution/tools/get_gsoc_info.jinja",
                year=2024,
                url="https://example.com"
            )

    """
    template = env.get_template(template_path)
    if context_factory:
        context = context_factory()
        context.update(kwargs)
        return template.render(**context).strip()
    if kwargs:
        return template.render(**kwargs).strip()
    return template.render().strip()
