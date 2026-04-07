from dataclasses import dataclass


@dataclass(frozen=True)
class Tool:
    name: str
    needs_permission: bool
    plan_mode_enabled: bool = True
    supports_non_interactive: bool = True


@dataclass(frozen=True)
class ToolUseContext:
    plan_mode: bool
    is_interactive: bool

    def allows(self, tool: Tool) -> bool:
        if self.plan_mode and not tool.plan_mode_enabled:
            return False
        if not self.is_interactive and not tool.supports_non_interactive:
            return False

        return True
