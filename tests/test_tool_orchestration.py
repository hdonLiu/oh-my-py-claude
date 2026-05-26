import pytest

from pyclaude.messages import ToolUseBlock
from pyclaude.tool_orchestration import run_tools
from pyclaude.tools.base import Tool, ToolResult


class ReadTool(Tool):
    name = "read"
    description_text = "Read."
    input_schema = {"type": "object", "properties": {}, "required": []}

    async def call(self, input, context=None):
        return ToolResult(content="read")

    def is_read_only(self, input=None):
        return True


class WriteTool(Tool):
    name = "write"
    description_text = "Write."
    input_schema = {"type": "object", "properties": {}, "required": []}

    async def call(self, input, context=None):
        return ToolResult(content="write")

    def is_read_only(self, input=None):
        return False


@pytest.mark.asyncio
async def test_run_tools_returns_results_in_tool_use_order():
    blocks = [
        ToolUseBlock(id="toolu_1", name="read", input={}),
        ToolUseBlock(id="toolu_2", name="write", input={}),
    ]
    results = await run_tools(blocks, {"read": ReadTool(), "write": WriteTool()})
    assert [result.tool_use_id for result in results] == ["toolu_1", "toolu_2"]
    assert [result.content for result in results] == ["read", "write"]
