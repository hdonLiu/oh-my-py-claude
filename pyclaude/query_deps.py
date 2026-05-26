from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from pyclaude.messages import AssistantMessage


@dataclass(frozen=True)
class QueryDeps:
    call_model: Callable[..., Awaitable[AssistantMessage]]


def production_deps() -> QueryDeps:
    from pyclaude.model_adapter import call_model

    return QueryDeps(call_model=call_model)
