from pyclaude.app_state import AppState
from pyclaude.messages import AbortedEvent, UserMessage
from pyclaude.query_loop import query
from pyclaude.tools.base import Tool


class QueryEngine:
    def __init__(
        self,
        *,
        tools: dict[str, Tool],
        state: AppState | None = None,
    ) -> None:
        self.tools = tools
        self.state = state or AppState()

    def abort(self) -> None:
        self.state.aborted = True

    async def submit_message(self, prompt: str) -> list[object]:
        self.state.messages.append(UserMessage(content=prompt))

        if self.state.aborted:
            return [AbortedEvent()]

        events: list[object] = []
        async for event in query(prompt=prompt, state=self.state, tools=self.tools):
            events.append(event)
            if event.type == "partial":
                self.state.partial_response = event.content
            elif event.type == "tool_summary":
                self.state.tool_summaries.append(event.summary)
            elif event.type == "assistant_message":
                self.state.messages.append(event.message)

        return events
