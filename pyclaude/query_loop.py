from collections.abc import AsyncIterator

from pyclaude.app_state import AppState
from pyclaude.messages import AssistantMessage, AssistantMessageEvent, PartialEvent
from pyclaude.model_adapter import ModelTextDelta
from pyclaude.query_deps import QueryDeps, production_deps
from pyclaude.tools.base import Tool


async def query(
    *,
    prompt: str,
    state: AppState,
    tools: dict[str, Tool],
    deps: QueryDeps | None = None,
) -> AsyncIterator[object]:
    resolved_deps = deps or production_deps()

    response_text = ""
    async for delta in resolved_deps.call_model(prompt=prompt, state=state):
        if isinstance(delta, ModelTextDelta):
            response_text += delta.text
            yield PartialEvent(content=response_text)

    yield AssistantMessageEvent(message=AssistantMessage(content=response_text))
