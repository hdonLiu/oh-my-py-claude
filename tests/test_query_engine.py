import pytest

from pyclaude.query_deps import QueryDeps
from pyclaude.query_engine import QueryEngine
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
async def test_query_engine_returns_events(
    assistant_tool_use_factory,
    assistant_text_factory,
    fake_model_class,
):
    model = fake_model_class([
        assistant_tool_use_factory("echo", {"text": "hi"}),
        assistant_text_factory("done"),
    ])
    engine = QueryEngine(tools={"echo": EchoTool()}, deps=QueryDeps(call_model=model))
    events = await engine.submit_message("run")
    assert events[-1].message.text == "done"
