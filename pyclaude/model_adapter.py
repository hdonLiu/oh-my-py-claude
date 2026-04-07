from collections.abc import AsyncGenerator
from dataclasses import dataclass

from anthropic import AsyncAnthropic

from pyclaude.app_state import AppState
from pyclaude.messages import AssistantMessage, UserMessage

DEFAULT_MODEL = "claude-opus-4-6"
DEFAULT_MAX_TOKENS = 64000


@dataclass(frozen=True)
class ModelTextDelta:
    text: str


def _to_api_messages(state: AppState) -> list[dict]:
    result = []
    for msg in state.messages:
        if isinstance(msg, UserMessage):
            result.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AssistantMessage):
            result.append({"role": "assistant", "content": msg.content})
    return result


async def query_model_with_streaming(*, prompt: str, state: AppState) -> AsyncGenerator[ModelTextDelta, None]:
    client = AsyncAnthropic()
    messages = _to_api_messages(state)

    async with client.messages.stream(
        model=DEFAULT_MODEL,
        max_tokens=DEFAULT_MAX_TOKENS,
        thinking={"type": "adaptive"},
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            if text:
                yield ModelTextDelta(text=text)
        await stream.get_final_message()
