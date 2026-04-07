from __future__ import annotations

from dataclasses import dataclass, asdict

from pyclaude.commands.registry import get_commands
from pyclaude.init import initialize_runtime
from pyclaude.tools.base import Tool


DEFAULT_COMMANDS = list(get_commands())


@dataclass
class AppSession:
    entrypoint: str = "main"
    repl_ready: bool = False


def build_app(
    *,
    session_mode: str = "prompt",
    tools: dict[str, Tool],
) -> dict:
    runtime = initialize_runtime()
    commands = get_commands()
    session = AppSession()

    if session_mode == "repl":
        from pyclaude.tui.launcher import build_repl_session  # noqa: PLC0415
        session.repl_ready = True
        repl_meta = build_repl_session()
        session_dict = asdict(session)
        session_dict.update(repl_meta)
    else:
        session_dict = asdict(session)

    return {
        "entrypoint": session.entrypoint,
        "session": session_dict,
        "runtime": asdict(runtime),
        "commands": list(commands),
        "tools": list(tools),
    }
