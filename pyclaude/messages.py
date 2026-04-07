from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserMessage:
    content: str


@dataclass(frozen=True)
class AssistantMessage:
    content: str


@dataclass(frozen=True)
class PartialEvent:
    content: str
    type: str = field(default="partial", init=False)


@dataclass(frozen=True)
class ToolResultEvent:
    tool_name: str
    tool_result: dict
    type: str = field(default="tool_result", init=False)


@dataclass(frozen=True)
class ToolSummaryEvent:
    summary: str
    type: str = field(default="tool_summary", init=False)


@dataclass(frozen=True)
class AssistantMessageEvent:
    message: AssistantMessage
    type: str = field(default="assistant_message", init=False)


@dataclass(frozen=True)
class AbortedEvent:
    type: str = field(default="aborted", init=False)
