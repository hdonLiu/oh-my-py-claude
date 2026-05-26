from __future__ import annotations

from pyclaude.messages import ToolResultBlock, ToolUseBlock
from pyclaude.tool_orchestration import run_tools
from pyclaude.tools.base import Tool


class ToolExecutor:
    def __init__(self, tools: dict[str, Tool]) -> None:
        self.tools = tools

    async def execute(self, tool_uses: list[ToolUseBlock], context: object | None = None) -> list[ToolResultBlock]:
        return await run_tools(tool_uses, self.tools, context=context)
