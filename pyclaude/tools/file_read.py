from __future__ import annotations

from pathlib import Path
from typing import Any

from pyclaude.tools.base import Tool, ToolResult


class FileReadTool(Tool):
    name = "file_read"
    description_text = "Read a file from the local filesystem."
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "The absolute path to the file to read"},
            "offset": {"type": "integer", "description": "The 1-based line number to start reading from"},
            "limit": {"type": "integer", "description": "The number of lines to read"},
            "pages": {
                "type": "string",
                "description": "Page range for PDF files; accepted but not used by the short-term text reader",
            },
        },
        "required": ["file_path"],
    }

    async def call(self, input: dict[str, Any], context: Any = None) -> ToolResult:
        self.validate_input(input)
        file_path = Path(input["file_path"]).expanduser()
        if not file_path.exists():
            return ToolResult(content=f"File not found: {file_path}", is_error=True)
        if file_path.is_dir():
            return ToolResult(content=f"Path is a directory: {file_path}", is_error=True)

        try:
            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            return ToolResult(content=f"Error reading file: {exc}", is_error=True)

        offset = int(input.get("offset", 1))
        limit = input.get("limit")
        start = max(0, offset - 1)
        selected = lines[start:] if limit is None else lines[start : start + int(limit)]
        content = "\n".join(f"{line_number}|{line}" for line_number, line in enumerate(selected, start=start + 1))
        return ToolResult(content=content)

    def is_read_only(self, input: dict[str, Any] | None = None) -> bool:
        return True
