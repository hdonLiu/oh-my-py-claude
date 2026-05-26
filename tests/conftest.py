import pytest

from pyclaude.messages import AssistantMessage, TextBlock, ToolUseBlock


def assistant_text(text: str) -> AssistantMessage:
    return AssistantMessage(content=[TextBlock(text=text)], stop_reason="end_turn")


def assistant_tool_use(
    tool_name: str,
    input: dict,
    tool_use_id: str = "toolu_1",
    text: str = "",
) -> AssistantMessage:
    content = []
    if text:
        content.append(TextBlock(text=text))
    content.append(ToolUseBlock(id=tool_use_id, name=tool_name, input=input))
    return AssistantMessage(content=content, stop_reason="tool_use")


class FakeModel:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses[len(self.calls) - 1]


@pytest.fixture
def assistant_text_factory():
    return assistant_text


@pytest.fixture
def assistant_tool_use_factory():
    return assistant_tool_use


@pytest.fixture
def fake_model_class():
    return FakeModel
