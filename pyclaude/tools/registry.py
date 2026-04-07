from __future__ import annotations

from pyclaude.permissions import ToolPermissionContext
from pyclaude.tools.base import Tool, ToolUseContext


BASE_TOOLS = {
    "read_file": Tool(name="read_file", needs_permission=False, plan_mode_enabled=True),
    "write_file": Tool(name="write_file", needs_permission=True, plan_mode_enabled=False),
    "ask_user": Tool(
        name="ask_user",
        needs_permission=False,
        plan_mode_enabled=True,
        supports_non_interactive=False,
    ),
}


def assemble_tool_pool(extra_tools: dict[str, Tool] | None = None) -> dict[str, Tool]:
    """Merge BASE_TOOLS with external tools while preserving built-in precedence."""
    pool = dict(extra_tools or {})
    pool.update(BASE_TOOLS)
    return pool


def get_tools(
    *,
    tool_use_context: ToolUseContext,
    permission_context: ToolPermissionContext,
    extra_tools: dict[str, Tool] | None = None,
) -> dict[str, Tool]:
    visible_tools: dict[str, Tool] = {}

    for name, tool in assemble_tool_pool(extra_tools).items():
        if not tool_use_context.allows(tool):
            continue
        if not permission_context.allows(tool.needs_permission):
            continue
        visible_tools[name] = tool

    return visible_tools
