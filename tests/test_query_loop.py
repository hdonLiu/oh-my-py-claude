import pytest

from pyclaude.app_state import AppState
from pyclaude.messages import AssistantMessageEvent, ToolResultEvent
from pyclaude.query_deps import QueryDeps
from pyclaude.query_loop import query
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
async def test_query_loop_executes_tool_and_calls_model_again(
    assistant_tool_use_factory,
    assistant_text_factory,
    fake_model_class,
):
    model = fake_model_class([
        assistant_tool_use_factory("echo", {"text": "hello"}, tool_use_id="toolu_1"),
        assistant_text_factory("done"),
    ])
    events = []
    async for event in query(
        prompt="say hello",
        state=AppState(),
        tools={"echo": EchoTool()},
        deps=QueryDeps(call_model=model),
    ):
        events.append(event)

    assert len(model.calls) == 2
    assert any(isinstance(event, ToolResultEvent) and event.content == "hello" for event in events)
    assert isinstance(events[-1], AssistantMessageEvent)
    assert events[-1].message.text == "done"
    second_call_messages = model.calls[1]["messages"]
    assert second_call_messages[-1]["content"][0]["type"] == "tool_result"
