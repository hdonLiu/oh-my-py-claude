from __future__ import annotations

import asyncio
from typing import Any

from pyclaude.tools.base import Tool, ToolResult


class BashTool(Tool):
    name = "bash"
    description_text = "Run a shell command."
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The command to execute"},
            "timeout": {"type": "integer", "description": "Optional timeout in seconds"},
            "description": {"type": "string", "description": "Short description of what this command does"},
            "run_in_background": {
                "type": "boolean",
                "description": "Accepted for TS compatibility; foreground execution in short term",
            },
            "dangerouslyDisableSandbox": {
                "type": "boolean",
                "description": "Accepted for TS compatibility; ignored in short term",
            },
        },
        "required": ["command"],
    }

    async def call(self, input: dict[str, Any], context: Any = None) -> ToolResult:
        self.validate_input(input)
        timeout = int(input.get("timeout", 120))
        proc = await asyncio.create_subprocess_shell(
            input["command"],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return ToolResult(content=f"Timeout: command exceeded {timeout}s", is_error=True)

        output_parts = []
        if stdout:
            output_parts.append(stdout.decode("utf-8", errors="replace"))
        if stderr:
            output_parts.append("STDERR:\n" + stderr.decode("utf-8", errors="replace"))
        if proc.returncode:
            output_parts.append(f"Exit code: {proc.returncode}")
        return ToolResult(content="\n".join(output_parts) or "(no output)", is_error=proc.returncode != 0)

    def is_read_only(self, input: dict[str, Any] | None = None) -> bool:
        return False

    def interrupt_behavior(self) -> str:
        return "cancel"
