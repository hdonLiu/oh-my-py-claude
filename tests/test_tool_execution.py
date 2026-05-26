import pytest

from pyclaude.messages import ToolUseBlock
from pyclaude.tool_execution import run_tool_use
from pyclaude.tools.base import Tool, ToolResult


class EchoTool(Tool):
    name = "echo"
    description_text = "Echo."
    input_schema = {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}

    async def call(self, input, context=None):
        return ToolResult(content=input["text"])

    def is_read_only(self, input=None):
        return True


@pytest.mark.asyncio
async def test_run_tool_use_success():
    block = ToolUseBlock(id="toolu_1", name="echo", input={"text": "hi"})
    result = await run_tool_use(block, {"echo": EchoTool()})
    assert result.tool_use_id == "toolu_1"
    assert result.content == "hi"
    assert result.is_error is False


@pytest.mark.asyncio
async def test_run_tool_use_missing_tool():
    block = ToolUseBlock(id="toolu_1", name="missing", input={})
    result = await run_tool_use(block, {})
    assert result.is_error is True
    assert "No such tool" in result.content
