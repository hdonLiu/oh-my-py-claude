from dataclasses import dataclass


@dataclass(frozen=True)
class ToolPermissionContext:
    mode: str
    allow_sensitive: bool = False

    def allows(self, needs_permission: bool) -> bool:
        if not needs_permission:
            return True

        return self.allow_sensitive
