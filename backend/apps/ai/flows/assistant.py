"""Main flow for processing queries with CrewAI."""

from __future__ import annotations

import inspect
import logging
from typing import cast

from crewai import Agent, Crew, Process, Task
from django.conf import settings

from apps.ai.agents.channel import create_channel_agent
from apps.ai.agents.chapter import create_chapter_agent
from apps.ai.agents.community import create_community_agent
from apps.ai.agents.contribution import create_contribution_agent
from apps.ai.agents.project import create_project_agent
from apps.ai.agents.rag import create_rag_agent
from apps.ai.common.constants import DEFAULT_VISION_MODEL, DELIMITER
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


def normalize_channel_id(channel_id: str | None) -> str:
    """Normalize channel ID by removing # prefix if present.

    Args:
        channel_id: Channel ID that may or may not have # prefix, or None.

    Returns:
        Normalized channel ID without # prefix, or empty string if None.

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
        images: Optional list of base64 encoded image data URIs
        channel_id: Optional Slack channel ID where the query originated
        is_app_mention: Whether this is an explicit app mention (vs channel monitored message)

    Returns:
        Response string formatted for Slack, or None if answer should be skipped
        (for channel monitored messages with low confidence)

    """
    try:
        # Process images if provided - enrich query with image context
        if images:
            try:
                image_context = (
                    OpenAi(model=DEFAULT_VISION_MODEL)
                    .set_prompt(IMAGE_DESCRIPTION_PROMPT)
                    .set_input(query)
                    .set_images(images)
                    .complete()
                )
                if image_context:
                    query = f"{query}{DELIMITER}Image context: {image_context}"
            except Exception:  # noqa: BLE001 - intentionally broad so image failure never fails the request
                logger.warning(
                    "Image enrichment failed; continuing without image context",
                    extra={"query": query[:200]},
                )
        # Step 0: Handle simple greetings and non-question messages
        # Normalize for comparison: strip, lower, remove trailing punctuation
        query_normalized = query.strip().lower().rstrip(".!?,;:")
        query_lower = query_normalized
        # Common greetings and simple acknowledgments (standalone only)
        simple_greetings = [
            "hello",
            "hi",
            "hey",
            "greetings",
            "thanks",
            "thank you",
            "thankyou",
            "thx",
            "ty",
            "goodbye",
            "bye",
            "see you",
            "good morning",
            "good afternoon",
            "good evening",
            "good night",
            "gn",
            "gm",
        ]

        # Check if query is ONLY a simple greeting (exact match, no question words or content)
        # If it contains question words or OWASP-related terms, it's not just a greeting
        question_indicators = [
            "?",
            "what",
            "how",
            "when",
            "where",
            "who",
            "why",
            "which",
            "tell",
            "explain",
            "find",
            "show",
            "help",
        ]
        has_question_content = any(indicator in query_lower for indicator in question_indicators)
        has_owasp_content = any(
            term in query_lower
            for term in ["owasp", "project", "chapter", "contribute", "gsoc", "security"]
        )

        # Only treat as simple greeting if it's exactly a greeting
        # AND has no question/OWASP content
        is_simple_greeting = (
            query_lower in simple_greetings and not has_question_content and not has_owasp_content
        )

        if is_simple_greeting:
            # For app mentions, respond friendly; for channel messages, skip
            if is_app_mention:
                return (
                    "Hello! 👋 I'm NestBot, your OWASP assistant. "
                    "I can help you with questions about OWASP projects, chapters, contributions, "
                    "GSoC, and more. What would you like to know?"
                )
            return None

        # Step 1: Check owasp-community channel first (before router) so channel
        # suggestion flow always runs and we avoid unnecessary route() calls
        normalized_channel_id = normalize_channel_id(channel_id) if channel_id else ""
        community_channel_id = normalize_channel_id(OWASP_COMMUNITY_CHANNEL_ID)
        is_community_channel = normalized_channel_id == community_channel_id

        if is_community_channel:
            intent = Intent.COMMUNITY.value
            confidence = 0.99
            router_result = {
                "intent": intent,
                "confidence": confidence,
                "alternative_intents": [],
            }
        else:
            router_result = route(query)
            intent = cast("str", router_result.get("intent"))
            confidence = cast("float", router_result.get("confidence", 0.5))

            # Validate router result - ensure we got a proper intent
            if not intent or intent not in Intent.values():
                logger.error(
                    "Router returned invalid intent",
                    extra={
                        "intent": intent,
                        "router_result": router_result,
                        "query": query[:200],
                    },
                )
                # Fallback to RAG
                intent = Intent.RAG.value
                confidence = 0.3

        logger.info(
            "Query routed",
            extra={
                "intent": intent,
                "confidence": confidence,
                "query": query[:200],
            },
        )

        # Collaborative flow: if low confidence or multiple intents, invoke all expert agents
        # Skip collaborative flow for owasp-community channel to preserve
        # channel suggestion routing
        if (
            confidence < CONFIDENCE_THRESHOLD or router_result.get("alternative_intents")
        ) and not is_community_channel:
            logger.info(
                "Low confidence or multiple intents detected, invoking collaborative flow",
                extra={
                    "confidence": confidence,
                    "alternatives": router_result.get("alternative_intents"),
                },
            )
            # Collect all intents while preserving order: primary intent first, then alternatives
            # Use dict.fromkeys() for deterministic deduplication (preserves insertion order)
            alternatives = cast("list[str]", router_result.get("alternative_intents", []))
            all_intents = [intent, *alternatives]
            all_intents = list(dict.fromkeys(all_intents))

            agents = []
            tasks = []
            rag_agent = None

            for intent_value in all_intents:
                if creator := INTENT_TO_AGENT.get(intent_value):
                    agent = creator(allow_delegation=True)
                    agents.append(agent)
                    # Track RAG agent for synthesis
                    if intent_value == Intent.RAG.value:
                        rag_agent = agent
                    tasks.append(
                        Task(
                            description=(
                                f"Address the user query '{query}' "
                                f"from the perspective of an {agent.role}. "
                                "Focus on parts relevant to your expertise and tools."
                            ),
                            agent=agent,
                            expected_output=f"Information related to {intent_value}",
                        )
                    )

            if not agents:
                logger.warning(
                    "No agents created for collaborative flow, falling back to single agent",
                    extra={"intent": intent, "all_intents": all_intents},
                )
            else:
                # Add RAG agent for synthesis if not already present and we have multiple agents
                if len(agents) > 1 and rag_agent is None:
                    rag_agent = create_rag_agent(allow_delegation=False)
                    agents.append(rag_agent)

                # Use RAG agent for synthesis if available (best suited for synthesis)
                # RAG has access to all knowledge and is ideal for synthesizing
                # multiple perspectives
                synthesis_agent = rag_agent if rag_agent is not None else agents[-1]

                synthesis_task = Task(
                    description=(
                        f"Using all previous observations, synthesize a complete, "
                        f"accurate, and concise answer to the user query: '{query}'. "
                        "Ensure all parts of the query are addressed and formatted "
                        "nicely for Slack."
                    ),
                    agent=synthesis_agent,
                    expected_output="Final comprehensive answer for Slack",
                )
                tasks.append(synthesis_task)

                crew = Crew(
                    agents=agents,
                    tasks=tasks,
                    process=Process.sequential,
                    verbose=True,
                    max_iter=5,
                    max_rpm=10,
                )
                result = crew.kickoff()
                result_str = str(result).strip() if result else ""

                # Validate result - if it's just "YES" or "NO", something went wrong
                # This prevents leaking Question Detector output to users
                if result_str and result_str.upper() in ("YES", "NO"):
                    logger.error(
                        "Collaborative flow returned Question Detector output "
                        "instead of proper response",
                        extra={
                            "intent": intent,
                            "all_intents": all_intents,
                            "result": result_str,
                            "result_length": len(result_str),
                            "query": query[:200],
                        },
                    )
                    # Return a fallback response instead
                    return get_fallback_response()

                return result_str or get_fallback_response()

        # Step 2: Handle queries in owasp-community channel - suggest channels
        # If query is in owasp-community channel, ALWAYS route to community agent
        # for channel suggestions regardless of intent
        if channel_id and is_community_channel:
            logger.debug(
                "Checking channel suggestion",
                extra={
                    "channel_id": channel_id,
                    "normalized_channel_id": normalized_channel_id,
                    "community_channel_id": community_channel_id,
                    "intent": intent,
                },
            )
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
                from apps.ai.agents.channel.tools import (  # noqa: PLC0415
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
                    from apps.ai.common.decorators import render_template  # noqa: PLC0415
                    from apps.slack.constants import OWASP_GSOC_CHANNEL_ID  # noqa: PLC0415

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
                from apps.ai.agents.channel.tools import (  # noqa: PLC0415
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
                elif result is None:
                    # Fallback: call render_template directly
                    from apps.ai.common.decorators import render_template  # noqa: PLC0415
                    from apps.slack.constants import (  # noqa: PLC0415
                        OWASP_CONTRIBUTE_CHANNEL_ID,
                    )

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
        result = execute_task(agent, query)
        result_str = str(result).strip() if result else ""

        # Validate result - if it's just "YES" or "NO", something went wrong
        if result_str and result_str.upper() in ("YES", "NO"):
            logger.error(
                "Agent returned Question Detector output instead of proper response",
                extra={
                    "intent": intent,
                    "result": result_str,
                    "result_length": len(result_str),
                    "query": query[:200],
                },
            )
            # Return a fallback response instead
            return get_fallback_response()
        return result_str or get_fallback_response()

    except Exception as e:
        logger.exception(
            "Failed to process query",
            extra={
                "query": query[:200],
                "error": str(e),
            },
        )
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
        "- For RAG agent: If the first search doesn't yield good results, "
        "try searching with different keywords or rephrased queries "
        "(e.g., if searching for 'project lifecycle' doesn't work, "
        "try 'project maturity', 'project stages', or 'project development process')\n"
        "- IMPORTANT: Do NOT retry the same tool call with the same input if it fails\n"
        "- If a tool call fails or doesn't provide useful results, try a different "
        "approach or tool\n"
        "- If you've already tried a tool and it didn't work, do NOT call it again "
        "with the same parameters\n"
        "- If semantic search returns no results or irrelevant results after trying multiple "
        "queries, provide a helpful response explaining what information you were looking for "
        "and suggest where the user might find it (e.g., OWASP website, specific project pages)"
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
    result_str = str(result).strip() if result else ""
    # Avoid leaking Question Detector output (YES/NO) to users
    if result_str and result_str.upper() in ("YES", "NO"):
        return get_fallback_response()
    return result_str or get_fallback_response()


def get_fallback_response() -> str:
    """Get fallback response on error.

    Returns:
        Fallback error message (detailed in development, generic in production)

    """
    # Only show detailed error message in local/development environment
    if getattr(settings, "IS_LOCAL_ENVIRONMENT", False) or getattr(settings, "DEBUG", False):
        return (
            "⚠️ I encountered an error processing your request. "
            "Please try rephrasing your question or contact support if the issue persists."
        )

    # Generic message for production
    return (
        "I'm sorry, I encountered an issue processing your request. "
        "Please try again or rephrase your question."
    )
