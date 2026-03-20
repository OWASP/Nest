"""AI app utils."""


def get_fallback_response() -> str:
    """Get fallback response on error.

    Returns:
        Fallback error message (detailed in development, generic in production)

    """
    from django.conf import settings  # noqa: PLC0415

    # Only show detailed error message in local/development environment
    if getattr(settings, "IS_LOCAL_ENVIRONMENT", False) or getattr(settings, "DEBUG", False):
        return (
            "⚠️ I encountered an error processing your request. "
            "Please try rephrasing your question or contact support if the issue persists."
        )

    # Generic message for production
    return (
        "I'm sorry, I encountered an issue processing your request. "
        "Please try again or rephrasing your question."
    )


def get_intent_to_agent_map() -> dict:
    """Get intent to agent map.

    Returns:
        Dictionary with intent as key and agent constructor as value.

    """
    from apps.ai.agents.chapter import create_chapter_agent  # noqa: PLC0415
    from apps.ai.agents.community import create_community_agent  # noqa: PLC0415
    from apps.ai.agents.contribution import create_contribution_agent  # noqa: PLC0415
    from apps.ai.agents.project import create_project_agent  # noqa: PLC0415
    from apps.ai.agents.rag import create_rag_agent  # noqa: PLC0415
    from apps.ai.common.intent import Intent  # noqa: PLC0415

    return {
        Intent.CHAPTER.value: create_chapter_agent,
        Intent.COMMUNITY.value: create_community_agent,
        Intent.CONTRIBUTION.value: create_contribution_agent,
        Intent.GSOC.value: create_contribution_agent,  # GSoC queries handled by contribution agent
        Intent.PROJECT.value: create_project_agent,
        Intent.RAG.value: create_rag_agent,
    }
