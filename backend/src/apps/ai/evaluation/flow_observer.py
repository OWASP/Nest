"""Scoped observation of the production assistant flow."""

import sys
from contextlib import ExitStack, contextmanager
from copy import deepcopy
from functools import wraps
from unittest.mock import patch

from apps.ai.flows import assistant


def observe_stage(name, function, events):
    """wrap a stage while preserving its results and exceptions."""

    @wraps(function) #keep original 
    def wrapped(*args, **kwargs):
        event = {"stage": name}
        events.append(event)

        if name == "execute_task":
            agent = args[0] if args else kwargs["agent"]
            event.update(
                role= agent.role,
                model=getattr(agent.llm, "model", None),
                query = args[1] if len(args)>1 else kwargs.get("query"),
            )

        try:
            result = function(*args, **kwargs)
        except Exception as error:
            event["error"] = f"{type(error).__name__}:{error}"
            raise
        else:
            event["result"] = deepcopy(result)
            return result

    return wrapped

@contextmanager
def observe_flow():
    """Observe one sequential evaluation with semantic caching bypassed."""

    events = []
    original_log_exception = assistant.logger.exception

    def record_logged_error(message, *args , **kwargs):
        error = sys.exception()
        events.append(
            {
            "stage": "logged_error",
                "message": str(message),
                "error": (
                    f"{type(error).__name__}: {error}"
                    if error is not None
                    else None
                ),
            }
        )
        return original_log_exception(message, *args, **kwargs)

    with ExitStack() as stack: 
        stack.enter_context(
            patch.object(assistant, "get_catched_response", return_value=None)
            
        )
        stack.enter_context(
            patch.object(assistant, "store_cached_response", return_value=None)
        )
        stack.enter_context(
            patch.object(
                assistant.logger,
                "exception",
                new=record_logged_error,
            )
        )

        for name in (
            "process_query",
            "analyze_query",
            "route",
            "handle_collaborative_query",
            "execute_task",
        ):
            function = getattr(assistant, name)
            stack.enter_context(
                patch.object(
                    assistant,
                    name,
                    new=observe_stage(name, function, events),
                )
            )

            yield events