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