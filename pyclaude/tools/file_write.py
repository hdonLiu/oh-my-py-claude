from __future__ import annotations

from pathlib import Path
from typing import Any

from pyclaude.tools.base import Tool, ToolResult


class FileWriteTool(Tool):
    name = "file_write"
    description_text = "Write content to a local file."
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "The absolute path to the file to write"},
            "content": {"type": "string", "description": "The content to write to the file"},
        },
        "required": ["file_path", "content"],
    }

    async def call(self, input: dict[str, Any], context: Any = None) -> ToolResult:
        self.validate_input(input)
        file_path = Path(input["file_path"]).expanduser()
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(input["content"], encoding="utf-8")
        except OSError as exc:
            return ToolResult(content=f"Error writing file: {exc}", is_error=True)
        return ToolResult(content=f"Successfully wrote {file_path}")

    def is_read_only(self, input: dict[str, Any] | None = None) -> bool:
        return False

    def is_destructive(self, input: dict[str, Any] | None = None) -> bool:
        return True
