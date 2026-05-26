from __future__ import annotations

import asyncio

from pyclaude.main import DEFAULT_COMMANDS, build_app
from pyclaude.messages import AssistantMessageEvent, ToolResultEvent
from pyclaude.query_engine import QueryEngine
from pyclaude.tools.base import Tool
from pyclaude.tools.registry import get_default_tools


def run_cli(args, extra_tools_provider: dict[str, Tool] | None = None) -> dict:
    if args.print_commands:
        return {"mode": "print-commands", "commands": list(DEFAULT_COMMANDS)}

    prompt = args.prompt or ""
    if not prompt:
        return {"mode": "repl", "message": "Interactive mode not yet implemented."}

    tools = get_default_tools()
    if extra_tools_provider:
        tools.update(extra_tools_provider)

    app = build_app(tools=tools)
    engine = QueryEngine(tools=tools)
    events = asyncio.run(engine.submit_message(prompt))

    output = []
    for event in events:
        if isinstance(event, AssistantMessageEvent) and event.message.text:
            output.append(event.message.text)
        elif isinstance(event, ToolResultEvent):
            output.append(f"[{event.tool_name}] {event.content}")

    return {
        "mode": "prompt",
        "app": app,
        "prompt": prompt,
        "events": events,
        "state": engine.state,
        "output": "\n".join(output),
    }
