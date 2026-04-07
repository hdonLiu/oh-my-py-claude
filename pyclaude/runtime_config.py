from dataclasses import dataclass, field


@dataclass
class RuntimeConfig:
    steps: list[str] = field(default_factory=list)
    config_enabled: bool = False
    environment_applied: bool = False
    auth_ready: bool = False
    security_ready: bool = False
    network_ready: bool = False
    graceful_shutdown_ready: bool = False
    telemetry_ready: bool = False
    trusted: bool = False
