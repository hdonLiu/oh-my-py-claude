from __future__ import annotations

from dataclasses import dataclass, field

from pyclaude.messages import Message


@dataclass
class AppState:
    messages: list[Message] = field(default_factory=list)
    aborted: bool = False
