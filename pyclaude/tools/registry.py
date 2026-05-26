from __future__ import annotations

from pyclaude.tools.base import Tool
from pyclaude.tools.bash import BashTool
from pyclaude.tools.file_read import FileReadTool
from pyclaude.tools.file_write import FileWriteTool


def get_default_tools() -> dict[str, Tool]:
    tools: list[Tool] = [FileReadTool(), FileWriteTool(), BashTool()]
    return {tool.name: tool for tool in tools}


def get_tools(*args, extra_tools: dict[str, Tool] | None = None, **kwargs) -> dict[str, Tool]:
    tools = get_default_tools()
    if extra_tools:
        tools.update(extra_tools)
    return tools
