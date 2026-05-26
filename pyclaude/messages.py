from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class TextBlock:
    text: str
    type: str = field(default="text", init=False)

    def to_api_dict(self) -> dict[str, Any]:
        return {"type": "text", "text": self.text}


@dataclass(frozen=True)
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]
    type: str = field(default="tool_use", init=False)

    def to_api_dict(self) -> dict[str, Any]:
        return {"type": "tool_use", "id": self.id, "name": self.name, "input": self.input}


@dataclass(frozen=True)
class ToolResultBlock:
    tool_use_id: str
    content: str
    is_error: bool = False
    type: str = field(default="tool_result", init=False)

    def to_api_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": "tool_result",
            "tool_use_id": self.tool_use_id,
            "content": self.content,
        }
        if self.is_error:
            result["is_error"] = True
        return result


ContentBlock = TextBlock | ToolUseBlock | ToolResultBlock


@dataclass(frozen=True)
class UserMessage:
    content: str | list[ToolResultBlock]
    role: Literal["user"] = field(default="user", init=False)

    @classmethod
    def text(cls, text: str) -> UserMessage:
        return cls(content=text)

    @classmethod
    def tool_results(cls, results: list[ToolResultBlock]) -> UserMessage:
        return cls(content=results)

    def to_api_dict(self) -> dict[str, Any]:
        if isinstance(self.content, str):
            return {"role": self.role, "content": self.content}
        return {"role": self.role, "content": [block.to_api_dict() for block in self.content]}


@dataclass(frozen=True)
class AssistantMessage:
    content: list[TextBlock | ToolUseBlock]
    stop_reason: str = "end_turn"
    role: Literal["assistant"] = field(default="assistant", init=False)

    @property
    def text(self) -> str:
        return "".join(block.text for block in self.content if isinstance(block, TextBlock))

    @property
    def tool_use_blocks(self) -> list[ToolUseBlock]:
        return [block for block in self.content if isinstance(block, ToolUseBlock)]

    def to_api_dict(self) -> dict[str, Any]:
        return {"role": self.role, "content": [block.to_api_dict() for block in self.content]}


Message = UserMessage | AssistantMessage


@dataclass(frozen=True)
class PartialEvent:
    content: str
    type: str = field(default="partial", init=False)


@dataclass(frozen=True)
class AssistantMessageEvent:
    message: AssistantMessage
    type: str = field(default="assistant_message", init=False)


@dataclass(frozen=True)
class ToolResultEvent:
    tool_use_id: str
    tool_name: str
    content: str
    is_error: bool
    type: str = field(default="tool_result", init=False)


@dataclass(frozen=True)
class ToolSummaryEvent:
    summary: str
    type: str = field(default="tool_summary", init=False)


@dataclass(frozen=True)
class AbortedEvent:
    type: str = field(default="aborted", init=False)
