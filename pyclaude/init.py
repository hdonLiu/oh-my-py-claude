from pyclaude.runtime_config import RuntimeConfig


def initialize_runtime() -> RuntimeConfig:
    runtime = RuntimeConfig()

    runtime.steps.append("enable_config")
    runtime.config_enabled = True

    runtime.steps.append("apply_environment")
    runtime.environment_applied = True

    runtime.steps.append("prepare_auth")
    runtime.auth_ready = True

    runtime.steps.append("prepare_security")
    runtime.security_ready = True

    runtime.steps.append("prepare_network")
    runtime.network_ready = True

    runtime.steps.append("register_graceful_shutdown")
    runtime.graceful_shutdown_ready = True

    return runtime


def initialize_telemetry_after_trust(runtime: RuntimeConfig) -> RuntimeConfig:
    if runtime.trusted:
        runtime.steps.append("initialize_telemetry_after_trust")
        runtime.telemetry_ready = True

    return runtime
