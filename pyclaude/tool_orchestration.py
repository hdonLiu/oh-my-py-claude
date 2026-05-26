from __future__ import annotations

import asyncio

from pyclaude.messages import ToolResultBlock, ToolUseBlock
from pyclaude.tool_execution import run_tool_use
from pyclaude.tools.base import Tool


def _is_concurrency_safe(tool_use: ToolUseBlock, tools: dict[str, Tool]) -> bool:
    tool = tools.get(tool_use.name)
    if tool is None:
        return True
    try:
        return tool.is_concurrency_safe(tool_use.input)
    except Exception:
        return False


async def run_tools(
    tool_uses: list[ToolUseBlock],
    tools: dict[str, Tool],
    context: object | None = None,
) -> list[ToolResultBlock]:
    results: list[ToolResultBlock] = []
    batch: list[ToolUseBlock] = []

    async def flush_batch() -> None:
        nonlocal batch
        if not batch:
            return
        batch_results = await asyncio.gather(*(run_tool_use(block, tools, context=context) for block in batch))
        results.extend(batch_results)
        batch = []

    for tool_use in tool_uses:
        if _is_concurrency_safe(tool_use, tools):
            batch.append(tool_use)
            continue
        await flush_batch()
        results.append(await run_tool_use(tool_use, tools, context=context))
    await flush_batch()
    return results
