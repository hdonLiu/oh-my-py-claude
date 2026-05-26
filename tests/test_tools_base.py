import pytest

from pyclaude.tools.base import Tool, ToolResult


class EchoTool(Tool):
    name = "echo"
    description_text = "Echo input text."
    input_schema = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    }

    async def call(self, input, context=None):
        return ToolResult(content=input["text"])

    def is_read_only(self, input=None):
        return True


@pytest.mark.asyncio
async def test_tool_call_returns_result():
    result = await EchoTool().call({"text": "hi"})
    assert result.content == "hi"
    assert result.is_error is False


def test_tool_api_definition():
    assert EchoTool().to_api_definition() == {
        "name": "echo",
        "description": "Echo input text.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    }


def test_default_concurrency_and_destructive_flags():
    tool = EchoTool()
    assert tool.is_concurrency_safe({"text": "hi"}) is True
    assert tool.is_destructive({"text": "hi"}) is False
    assert tool.needs_permission({"text": "hi"}) is False
