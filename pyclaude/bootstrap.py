import asyncio
from dataclasses import asdict

from pyclaude.main import build_app, DEFAULT_COMMANDS
from pyclaude.permissions import ToolPermissionContext
from pyclaude.query_engine import QueryEngine
from pyclaude.tools.base import Tool, ToolUseContext
from pyclaude.tools.registry import get_tools


def run_cli(args, extra_tools_provider: dict[str, Tool] | None = None) -> dict:
    if args.print_commands:
        return {"mode": "print-commands", "commands": list(DEFAULT_COMMANDS)}

    prompt = args.prompt or ""

    tools = get_tools(
        tool_use_context=ToolUseContext(plan_mode=False, is_interactive=True),
        permission_context=ToolPermissionContext(mode="default", allow_sensitive=False),
        extra_tools=extra_tools_provider,
    )
    app = build_app(tools=tools)
    engine = QueryEngine(tools=tools)
    events = asyncio.run(engine.submit_message(prompt))

    return {
        "mode": "prompt",
        "app": app,
        "prompt": prompt,
        "events": [asdict(event) for event in events],
        "state": asdict(engine.state),
    }
