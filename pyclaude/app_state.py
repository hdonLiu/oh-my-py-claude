from dataclasses import dataclass, field

from pyclaude.messages import AssistantMessage, UserMessage


@dataclass
class AppState:
    messages: list[UserMessage | AssistantMessage] = field(default_factory=list)
    partial_response: str = ""
    tool_summaries: list[str] = field(default_factory=list)
    aborted: bool = False
