from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from anthropic import AsyncAnthropic

from pyclaude.messages import AssistantMessage, TextBlock, ToolUseBlock
from pyclaude.tools.base import Tool

DEFAULT_MODEL = "claude-opus-4-6"
DEFAULT_MAX_TOKENS = 64000


@dataclass(frozen=True)
class ModelConfig:
    model: str = DEFAULT_MODEL
    max_tokens: int = DEFAULT_MAX_TOKENS


def parse_api_response(raw: Any) -> AssistantMessage:
    content = []
    for block in raw.content:
        if block.type == "text":
            content.append(TextBlock(text=block.text))
        elif block.type == "tool_use":
            content.append(ToolUseBlock(id=block.id, name=block.name, input=block.input))
    return AssistantMessage(content=content, stop_reason=getattr(raw, "stop_reason", "end_turn") or "end_turn")


async def call_model(
    *,
    messages: list[dict[str, Any]],
    tools: dict[str, Tool],
    config: ModelConfig | None = None,
) -> AssistantMessage:
    cfg = config or ModelConfig()
    client = AsyncAnthropic()
    kwargs: dict[str, Any] = {
        "model": cfg.model,
        "max_tokens": cfg.max_tokens,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = [tool.to_api_definition() for tool in tools.values()]
    response = await client.messages.create(**kwargs)
    return parse_api_response(response)
