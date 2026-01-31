"""Router agent for intent classification."""

import contextlib

from crewai import Agent, Crew, Task

from apps.ai.common.intent import Intent
from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env


def create_router_agent() -> Agent:
    """Create router agent for intent classification.

    Returns:
        Agent: Router agent configured for intent classification

    """
    backstory_template = env.get_template("router/backstory.jinja")

    context = {
        "Intent": Intent,
    }

    return Agent(
        role="Intent Classifier",
        goal=(
            "Classify user queries into one of these expert agents: "
            f"{', '.join(Intent.values())}. Provide confidence score and reasoning."
        ),
        backstory=backstory_template.render(**context).strip(),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def route(query: str) -> dict:
    """Route query with confidence scoring.

    Args:
        query: User's question

    Returns:
        Dictionary with 'intent', 'confidence', 'reasoning', and 'alternative_intents'

    """
    import logging

    logger = logging.getLogger(__name__)

    router_agent = create_router_agent()

    task_template = env.get_template("router/tasks/route.jinja")
    task_description = task_template.render(
        query=query,
        intent_values=", ".join(Intent.values()),
    ).strip()

    routing_task = Task(
        description=task_description,
        agent=router_agent,
        expected_output="Intent classification with confidence score and reasoning",
    )

    crew = Crew(
        agents=[router_agent],
        tasks=[routing_task],
        verbose=True,
        max_iter=5,
        max_rpm=10,
    )

    result = crew.kickoff()

    # Parse result
    result_str = str(result).strip()

    # Validate result - if it's just "YES" or "NO", something went wrong
    result_upper = result_str.upper().strip()
    # Check if result is exactly "YES" or "NO" (with or without whitespace)
    if result_upper in {"YES", "NO"}:
        logger.error(
            "Router returned Question Detector output instead of routing result",
            extra={
                "result_str": result_str,
                "result_length": len(result_str),
                "query": query[:200],
            },
        )
        # Default to RAG as fallback
        return {
            "intent": Intent.RAG.value,
            "confidence": 0.3,
            "reasoning": "Router returned invalid output, defaulting to RAG",
            "alternative_intents": [],
        }

    # Additional validation: check if result looks like routing format
    has_intent_line = any("intent:" in line.lower() for line in result_str.split("\n")[:10])
    if not has_intent_line and len(result_str) < 50:
        # If result is very short and doesn't have "intent:" line, it's probably wrong
        logger.error(
            "Router result doesn't look like routing format",
            extra={
                "result_str": result_str[:200],
                "query": query[:200],
            },
        )
        return {
            "intent": Intent.RAG.value,
            "confidence": 0.3,
            "reasoning": "Router returned invalid format, defaulting to RAG",
            "alternative_intents": [],
        }

    intent = None
    confidence = 0.5
    reasoning = ""
    alternatives = []

    # Simple parsing (can be enhanced)
    for line in result_str.split("\n"):
        line_lower = line.lower().strip()
        if line_lower.startswith("intent:"):
            intent_value = line.split(":", 1)[1].strip().lower()
            if intent_value in Intent.values():
                intent = intent_value
        elif line_lower.startswith("confidence:"):
            with contextlib.suppress(ValueError):
                confidence = float(line.split(":", 1)[1].strip())
        elif line_lower.startswith("reasoning:"):
            reasoning = line.split(":", 1)[1].strip()
        elif line_lower.startswith("alternatives:"):
            alt_str = line.split(":", 1)[1].strip().lower()
            if alt_str and alt_str != "none":
                alternatives = [a.strip() for a in alt_str.split(",")]

    # Default to RAG if intent not found (most general fallback)
    if not intent:
        logger.warning(
            "Router did not return a valid intent, defaulting to RAG",
            extra={
                "result_str": result_str[:500],
                "parsed_intent": intent,
            },
        )
        intent = Intent.RAG.value
        confidence = 0.3

    logger.info(
        "Router completed",
        extra={
            "intent": intent,
            "confidence": confidence,
        },
    )

    return {
        "intent": intent,
        "confidence": confidence,
        "reasoning": reasoning or "Intent classification completed",
        "alternative_intents": alternatives,
    }
