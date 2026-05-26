from __future__ import annotations

from pyclaude.app_state import AppState
from pyclaude.messages import AbortedEvent
from pyclaude.query_deps import QueryDeps
from pyclaude.query_loop import query
from pyclaude.tools.base import Tool


class QueryEngine:
    def __init__(
        self,
        *,
        tools: dict[str, Tool],
        state: AppState | None = None,
        deps: QueryDeps | None = None,
    ) -> None:
        self.tools = tools
        self.state = state or AppState()
        self.deps = deps

    def abort(self) -> None:
        self.state.aborted = True

    async def submit_message(self, prompt: str) -> list[object]:
        if self.state.aborted:
            return [AbortedEvent()]
        events: list[object] = []
        async for event in query(prompt=prompt, state=self.state, tools=self.tools, deps=self.deps):
            events.append(event)
        return events
