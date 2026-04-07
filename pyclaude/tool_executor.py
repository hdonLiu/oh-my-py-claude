from pyclaude.messages import ToolResultEvent, ToolSummaryEvent
from pyclaude.tools.base import Tool


async def execute_tool(*, tool_name: str, path: str, tools: dict[str, Tool]) -> tuple[ToolResultEvent, ToolSummaryEvent]:
    if tool_name not in tools:
        raise ValueError(f"Tool not available: {tool_name}")

    if tool_name != "read_file":
        raise ValueError(f"Unsupported tool: {tool_name}")

    result = {
        "path": path,
        "content": f"stub content from {path}",
    }
    return (
        ToolResultEvent(tool_name=tool_name, tool_result=result),
        ToolSummaryEvent(summary=f"{tool_name}({path})"),
    )
