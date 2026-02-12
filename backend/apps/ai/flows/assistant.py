"""Main flow for processing queries with CrewAI."""

from __future__ import annotations

import inspect
import logging

from crewai import Agent, Crew, Task

from apps.ai.agents.channel import create_channel_agent
from apps.ai.agents.chapter import create_chapter_agent
from apps.ai.agents.community import create_community_agent
from apps.ai.agents.contribution import create_contribution_agent
from apps.ai.agents.project import create_project_agent
from apps.ai.agents.rag import create_rag_agent
from apps.ai.common.intent import Intent
from apps.ai.router import route
from apps.common.open_ai import OpenAi
from apps.slack.constants import (
    OWASP_COMMUNITY_CHANNEL_ID,
)

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.7

IMAGE_DESCRIPTION_PROMPT = (
    "Describe what is shown in these images. Focus on any text, "
    "error messages, code snippets, UI elements, or technical details. "
    "Be concise."
)


def normalize_channel_id(channel_id: str) -> str:
    """Normalize channel ID by removing # prefix if present.

    Args:
        channel_id: Channel ID that may or may not have # prefix

    Returns:
        Normalized channel ID without # prefix

    """
    return channel_id.lstrip("#") if channel_id else ""


INTENT_TO_AGENT = {
    Intent.CHAPTER.value: create_chapter_agent,
    Intent.COMMUNITY.value: create_community_agent,
    Intent.CONTRIBUTION.value: create_contribution_agent,
    Intent.GSOC.value: create_contribution_agent,  # GSoC queries handled by contribution agent
    Intent.PROJECT.value: create_project_agent,
    Intent.RAG.value: create_rag_agent,
}


def process_query(  # noqa: PLR0911
    query: str,
    images: list[str] | None = None,
    channel_id: str | None = None,
    *,
    is_app_mention: bool = False,
) -> str | None:
    """Process query using multi-agent architecture.

    Supports both single-agent and collaborative multi-agent flows.

    Args:
        query: User's question
        images (list[str] | None): A list of base64 encoded image data URIs.
        channel_id: Optional Slack channel ID where the query originated
        is_app_mention: Whether this is an explicit app mention (vs channel monitored message)

    Returns:
        Response string formatted for Slack, or None if answer should be skipped
        (for channel monitored messages with low confidence)

    """
    try:
        if images:
            image_context = (
                OpenAi(model="gpt-4o")
                .set_prompt(IMAGE_DESCRIPTION_PROMPT)
                .set_input(query)
                .set_images(images)
                .complete()
            )
            if image_context:
                query = f"{query}\n\nImage context: {image_context}"

        # Step 1: Route to appropriate expert agent
        router_result = route(query)
        intent = router_result["intent"]
        confidence = router_result["confidence"]
        logger.info(
            "Query routed",
            extra={
                "intent": intent,
                "confidence": confidence,
                "query": query,
                "channel_id": channel_id,
            },
        )

        # Step 2: Handle queries in owasp-community channel - suggest channels
        # If query is in owasp-community channel, ALWAYS route to community agent
        # for channel suggestions regardless of intent
        if channel_id:
            normalized_channel_id = normalize_channel_id(channel_id)
            community_channel_id = normalize_channel_id(OWASP_COMMUNITY_CHANNEL_ID)

            logger.debug(
                "Checking channel suggestion",
                extra={
                    "channel_id": channel_id,
                    "normalized_channel_id": normalized_channel_id,
                    "community_channel_id": community_channel_id,
                    "intent": intent,
                },
            )

            # If question is asked in owasp-community channel, route to community agent
            # for channel suggestions
            if normalized_channel_id == community_channel_id:
                # Pre-check for contribution keywords to help guide the agent
                contribution_keywords = [
                    "contribute",
                    "contributing",
                    "contributor",
                    "contributors",
                    "get involved",
                    "getting involved",
                    "how to get involved",
                    "beginner-friendly",
                    "starter issues",
                    "new contributors",
                    "contribution guidelines",
                    "contribution opportunities",
                    "how to start",
                    "getting started",
                    "how contributors get involved",
                    "good projects for",
                    "projects for beginners",
                    "interested in",
                    "excited to join",
                    "looking forward to contributing",
                    "keen on learning",
                    "would love some guidance",
                    "I'd love some guidance",
                    "how teams collaborate",
                    "how projects are structured",
                    "how to find issues",
                    "contributing along",
                    "contributing along the way",
                    "contributing to",
                    "guidance on",
                    "some guidance",
                    "love some guidance",
                    "repositories are good",
                    "projects or repositories",
                ]
                query_lower = query.lower()
                has_contribution_keywords = any(
                    keyword in query_lower for keyword in contribution_keywords
                )

                logger.info(
                    "Query from owasp-community channel detected (intent: %s, "
                    "has_contribution_keywords: %s), routing to community agent for "
                    "channel suggestions",
                    intent,
                    has_contribution_keywords,
                    extra={
                        "channel_id": channel_id,
                        "intent": intent,
                        "confidence": confidence,
                        "has_contribution_keywords": has_contribution_keywords,
                        "community_channel_id": community_channel_id,
                    },
                )

                # Check for GSoC keywords first (more specific)
                gsoc_keywords = [
                    "gsoc",
                    "google summer of code",
                    "google summer",
                    "summer of code",
                ]
                has_gsoc_keywords = any(keyword in query_lower for keyword in gsoc_keywords)

                # If GSoC keywords detected, directly call the GSoC suggestion tool
                if has_gsoc_keywords:
                    logger.info(
                        "GSoC keywords detected in owasp-community channel, "
                        "directly calling GSoC channel suggestion tool",
                        extra={"query": query[:200]},
                    )
                    from apps.ai.agents.channel.tools import (
                        suggest_gsoc_channel,
                    )

                    # Try to get the underlying function from the Tool object
                    func = None
                    result = None
                    if hasattr(suggest_gsoc_channel, "__wrapped__"):
                        func = suggest_gsoc_channel.__wrapped__
                    elif hasattr(suggest_gsoc_channel, "func"):
                        func = suggest_gsoc_channel.func
                    elif hasattr(suggest_gsoc_channel, "run"):
                        # If it has a run method, call that
                        result = suggest_gsoc_channel.run({})
                    else:
                        # Try to unwrap using inspect
                        func = inspect.unwrap(suggest_gsoc_channel)

                    if func and callable(func):
                        result = func()
                    elif result is None:
                        # Fallback: call render_template directly
                        from apps.ai.common.decorators import render_template
                        from apps.slack.constants import OWASP_GSOC_CHANNEL_ID

                        channel_id = OWASP_GSOC_CHANNEL_ID.lstrip("#")
                        result = render_template(
                            "agents/channel/tools/gsoc.jinja",
                            gsoc_channel_id=channel_id,
                        )
                    logger.info(
                        "Direct GSoC channel suggestion tool call completed",
                        extra={"result_preview": result[:100]},
                    )
                    return result

                # If contribution keywords detected, directly call the suggestion tool
                if has_contribution_keywords:
                    matched_keywords = [kw for kw in contribution_keywords if kw in query_lower]
                    logger.info(
                        "Contribution keywords detected in owasp-community channel, "
                        "directly calling channel suggestion tool",
                        extra={
                            "query": query[:200],
                            "matched_keywords": matched_keywords,
                            "has_contribution_keywords": has_contribution_keywords,
                        },
                    )
                    from apps.ai.agents.channel.tools import (
                        suggest_contribute_channel,
                    )

                    # Try to get the underlying function from the Tool object
                    func = None
                    result = None
                    if hasattr(suggest_contribute_channel, "__wrapped__"):
                        func = suggest_contribute_channel.__wrapped__
                    elif hasattr(suggest_contribute_channel, "func"):
                        func = suggest_contribute_channel.func
                    elif hasattr(suggest_contribute_channel, "run"):
                        # If it has a run method, call that
                        result = suggest_contribute_channel.run({})
                    else:
                        # Try to unwrap using inspect
                        func = inspect.unwrap(suggest_contribute_channel)

                    if func and callable(func):
                        result = func()
                    elif not result:
                        # Fallback: call render_template directly
                        from apps.ai.common.decorators import render_template
                        from apps.slack.constants import OWASP_CONTRIBUTE_CHANNEL_ID

                        channel_id = OWASP_CONTRIBUTE_CHANNEL_ID.lstrip("#")
                        result = render_template(
                            "agents/channel/tools/contribute.jinja",
                            contribute_channel_id=channel_id,
                        )
                    logger.info(
                        "Direct channel suggestion tool call completed",
                        extra={"result_preview": result[:100]},
                    )
                    return result

                # For all other queries in owasp-community channel, use channel agent
                logger.info(
                    "Query from owasp-community channel, routing to channel agent",
                    extra={"query": query[:200]},
                )
                channel_agent = create_channel_agent()
                return execute_task(
                    channel_agent,
                    query,
                    channel_id=channel_id,
                    is_channel_suggestion=True,
                )

        # Step 3: Check for contribution intent even if misclassified
        # This is a fallback to catch contribution queries that might be misclassified
        contribution_keywords = [
            "contribute",
            "contributing",
            "contributor",
            "contributors",
            "get involved",
            "getting involved",
            "beginner-friendly",
            "starter issues",
            "contribution guidelines",
            "contribution opportunities",
            "how to start",
            "getting started",
            "new contributors",
            "good projects for",
            "would love",
            "interested in",
            "excited to join",
            "looking forward to contributing",
            "keen on learning",
        ]
        query_lower = query.lower()
        has_contribution_keywords = any(
            keyword in query_lower for keyword in contribution_keywords
        )

        # Step 4: Handle low confidence - skip or provide short message
        # Exception: RAG intent can proceed with lower confidence since it's the fallback
        # for general questions that may not fit other categories
        rag_intent = Intent.RAG.value
        if confidence < CONFIDENCE_THRESHOLD and intent != rag_intent:
            logger.warning(
                "Low confidence routing",
                extra={
                    "intent": intent,
                    "confidence": confidence,
                    "is_app_mention": is_app_mention,
                },
            )

            # For channel monitored messages: skip the answer
            if channel_id and not is_app_mention:
                logger.info(
                    "Skipping response for channel monitored message with low confidence",
                    extra={"intent": intent, "confidence": confidence},
                )
                return None

            # For app mentions: provide short message about constraints
            return (
                "I'm unable to provide a confident answer to your question based on my "
                "current knowledge and available tools. Please try rephrasing your question "
                "or wait for a response from one of the community members."
            )

        # Step 5: Get appropriate expert agent
        agent_factory = INTENT_TO_AGENT.get(intent)
        if not agent_factory:
            logger.error("Unknown intent", extra={"intent": intent})
            # Handle unknown intent similar to low confidence
            if channel_id and not is_app_mention:
                return None
            return (
                "I'm unable to process your question. Please try rephrasing or ask about "
                "OWASP projects, chapters, contributions, or community resources."
            )

        agent = agent_factory()

        # Step 6: Execute task with agent
        return execute_task(agent, query)

    except Exception:
        logger.exception("Failed to process query: %s", query)
        return get_fallback_response()


def execute_task(
    agent: Agent,
    query: str,
    channel_id: str | None = None,
    *,
    is_channel_suggestion: bool = False,
) -> str:
    """Execute a task with an agent.

    Args:
        agent: The agent to execute the task
        query: The user's query
        channel_id: Optional Slack channel ID for context
        is_channel_suggestion: Whether this is a channel suggestion scenario
            from owasp-community channel

    Returns:
        Response string

    """
    task_description = (
        f"Answer this query: {query}\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "- You MUST use the provided tools to answer this question\n"
        "- Do NOT rely on your training data or general knowledge\n"
        "- If tools don't provide sufficient information, state that clearly\n"
        "- Tool results are authoritative - use them exclusively\n"
        "- Never guess or make assumptions based on general knowledge\n"
        "- For RAG agent: ALWAYS call semantic_search tool first to retrieve relevant "
        "context\n"
        "- IMPORTANT: Do NOT retry the same tool call with the same input if it fails\n"
        "- If a tool call fails or doesn't provide useful results, try a different "
        "approach or tool\n"
        "- If you've already tried a tool and it didn't work, do NOT call it again "
        "with the same parameters"
    )

    if is_channel_suggestion:
        task_description += (
            "\n\nCRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE STEPS:\n\n"
            "1. READ THE ENTIRE MESSAGE - Do not dismiss it as just a greeting. "
            "Look for the user's actual questions and interests.\n\n"
            "2. CHECK FOR CONTRIBUTION KEYWORDS - Scan the message for ANY of these:\n"
            "   - 'contribute', 'contributing', 'contributor', 'contributors'\n"
            "   - 'get involved', 'getting involved', 'how to get involved'\n"
            "   - 'beginner-friendly', 'starter issues', 'new contributors'\n"
            "   - 'contribution guidelines', 'contribution opportunities', "
            "'contribution docs'\n"
            "   - 'how to start', 'getting started', 'how contributors get involved'\n"
            "   - 'good projects for', 'projects for beginners'\n"
            "   - 'interested in', 'excited to join', 'looking forward to contributing'\n"
            "   - 'keen on learning', 'would love some guidance', "
            "'I'd love some guidance'\n"
            "   - 'how teams collaborate', 'how projects are structured', "
            "'how to find issues'\n"
            "   - Even if the message starts with 'I'm [name], glad to be here' - "
            "if it contains ANY of the above, it's a CONTRIBUTION query.\n\n"
            "3. IF CONTRIBUTION KEYWORDS FOUND → YOU MUST IMMEDIATELY CALL: "
            "suggest_contribute_channel()\n"
            "   - Call the tool ONCE with no parameters (it takes no arguments)\n"
            "   - The tool will return a formatted message\n"
            "   - Your task is COMPLETE after receiving the tool output\n"
            "   - Return the tool output EXACTLY as-is, word-for-word\n"
            "   - Do NOT call any other tools\n"
            "   - Do NOT generate any additional text\n"
            "   - Do NOT call the tool again - it has no parameters, calling it again "
            "does nothing\n"
            "   - STOP immediately after returning the tool output\n\n"
            "4. IF GSoC MENTIONED → CALL: suggest_gsoc_channel()\n"
            "   - Same rules: call once with no parameters, return output exactly, "
            "then STOP\n\n"
            "5. IF SPECIFIC PROJECT/CHAPTER NAME → CALL: get_entity_channels() with the name\n\n"
            "6. OTHERWISE → CALL: get_entity_channels()\n\n"
            "STOP CONDITION: After calling a tool and receiving its output, you are DONE. "
            "Do not continue. Do not call the tool again. The tool output is your complete "
            "response. Return it immediately and stop. Do not try to improve it. Do not add "
            "anything to it."
        )

    if channel_id:
        task_description += f"\n\nContext: This query was asked in Slack channel {channel_id}"

    expected_output = (
        "Clear, concise answer based ONLY on tool results, "
        "formatted for Slack markdown. If tools don't provide enough "
        "information, explicitly state what information is missing."
    )

    if is_channel_suggestion:
        expected_output = (
            "The exact, unmodified output from the channel suggestion tool. "
            "Call the tool ONCE, copy its output exactly, and return it. "
            "That is your complete response. Do not add anything. Do not call the tool again."
        )

    task = Task(
        description=task_description,
        agent=agent,
        expected_output=expected_output,
    )

    # For channel suggestions, use stricter limits to prevent loops
    crew_kwargs = {
        "agents": [agent],
        "tasks": [task],
        "verbose": True,
        "memory": False,
        "max_rpm": 10,
    }

    if is_channel_suggestion:
        crew_kwargs["max_iter"] = 2
    else:
        crew_kwargs["max_iter"] = 15

    crew = Crew(**crew_kwargs)
    result = crew.kickoff()
    return str(result)


def get_fallback_response() -> str:
    """Get fallback response on error.

    Returns:
        Fallback error message (detailed in development, generic in production)

    """
    from django.conf import settings

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
