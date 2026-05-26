from __future__ import annotations

from pyclaude.messages import ToolResultBlock, ToolUseBlock
from pyclaude.tools.base import Tool


async def run_tool_use(
    tool_use: ToolUseBlock,
    tools: dict[str, Tool],
    context: object | None = None,
) -> ToolResultBlock:
    tool = tools.get(tool_use.name)
    if tool is None:
        return ToolResultBlock(
            tool_use_id=tool_use.id,
            content=f"No such tool available: {tool_use.name}",
            is_error=True,
        )
    try:
        tool.validate_input(tool_use.input)
        result = await tool.call(tool_use.input, context=context)
    except Exception as exc:
        return ToolResultBlock(tool_use_id=tool_use.id, content=f"Tool error: {exc}", is_error=True)
    return ToolResultBlock(tool_use_id=tool_use.id, content=result.content, is_error=result.is_error)
