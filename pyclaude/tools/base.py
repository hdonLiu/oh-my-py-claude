from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    content: str
    is_error: bool = False


class Tool(ABC):
    name: str
    description_text: str
    input_schema: dict[str, Any]

    @abstractmethod
    async def call(self, input: dict[str, Any], context: Any = None) -> ToolResult:
        pass

    def description(self, input: dict[str, Any] | None = None) -> str:
        return self.description_text

    @abstractmethod
    def is_read_only(self, input: dict[str, Any] | None = None) -> bool:
        pass

    def is_concurrency_safe(self, input: dict[str, Any] | None = None) -> bool:
        return self.is_read_only(input)

    def is_destructive(self, input: dict[str, Any] | None = None) -> bool:
        return False

    def interrupt_behavior(self) -> str:
        return "block"

    def needs_permission(self, input: dict[str, Any] | None = None) -> bool:
        return not self.is_read_only(input)

    def validate_input(self, input: dict[str, Any]) -> None:
        required = self.input_schema.get("required", [])
        for key in required:
            if key not in input:
                raise ValueError(f"Missing required input: {key}")

    def to_api_definition(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description_text,
            "input_schema": self.input_schema,
        }
