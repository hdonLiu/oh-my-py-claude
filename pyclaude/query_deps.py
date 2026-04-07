from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass

from pyclaude.model_adapter import ModelTextDelta


@dataclass(frozen=True)
class QueryDeps:
    call_model: Callable[..., AsyncGenerator[ModelTextDelta, None]]


def production_deps() -> QueryDeps:
    from pyclaude.model_adapter import query_model_with_streaming

    return QueryDeps(call_model=query_model_with_streaming)
