from __future__ import annotations

from collections.abc import AsyncIterator

from pyclaude.app_state import AppState
from pyclaude.messages import AssistantMessageEvent, ToolResultEvent, UserMessage
from pyclaude.query_deps import QueryDeps, production_deps
from pyclaude.tool_executor import ToolExecutor
from pyclaude.tools.base import Tool


async def query(
    *,
    prompt: str,
    state: AppState,
    tools: dict[str, Tool],
    deps: QueryDeps | None = None,
) -> AsyncIterator[object]:
    resolved_deps = deps or production_deps()
    executor = ToolExecutor(tools)

    state.messages.append(UserMessage.text(prompt))

    while not state.aborted:
        api_messages = [message.to_api_dict() for message in state.messages]
        assistant_message = await resolved_deps.call_model(messages=api_messages, tools=tools)
        state.messages.append(assistant_message)
        yield AssistantMessageEvent(message=assistant_message)

        tool_uses = assistant_message.tool_use_blocks
        if not tool_uses:
            return

        tool_results = await executor.execute(tool_uses)
        for tool_use, result in zip(tool_uses, tool_results, strict=True):
            yield ToolResultEvent(
                tool_use_id=result.tool_use_id,
                tool_name=tool_use.name,
                content=result.content,
                is_error=result.is_error,
            )
        state.messages.append(UserMessage.tool_results(tool_results))
