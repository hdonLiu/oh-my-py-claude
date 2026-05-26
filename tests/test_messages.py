from pyclaude.messages import (
    AssistantMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)


def test_user_text_message_to_api_dict():
    msg = UserMessage.text("hello")
    assert msg.to_api_dict() == {"role": "user", "content": "hello"}


def test_assistant_tool_use_message_to_api_dict():
    msg = AssistantMessage(
        content=[
            TextBlock(text="Reading file."),
            ToolUseBlock(id="toolu_1", name="file_read", input={"file_path": "/tmp/a.txt"}),
        ],
        stop_reason="tool_use",
    )
    assert msg.tool_use_blocks[0].name == "file_read"
    assert msg.text == "Reading file."
    assert msg.to_api_dict()["content"][1] == {
        "type": "tool_use",
        "id": "toolu_1",
        "name": "file_read",
        "input": {"file_path": "/tmp/a.txt"},
    }


def test_tool_result_block_error_serialization():
    block = ToolResultBlock(tool_use_id="toolu_1", content="boom", is_error=True)
    assert block.to_api_dict() == {
        "type": "tool_result",
        "tool_use_id": "toolu_1",
        "content": "boom",
        "is_error": True,
    }


def test_user_tool_result_message_to_api_dict():
    msg = UserMessage.tool_results([
        ToolResultBlock(tool_use_id="toolu_1", content="ok"),
    ])
    assert msg.to_api_dict() == {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": "toolu_1", "content": "ok"},
        ],
    }
