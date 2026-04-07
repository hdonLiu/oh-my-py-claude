from dataclasses import dataclass


@dataclass
class ReplSession:
    """Minimal REPL/TUI stub session metadata.

    This is the assembly boundary for Task 6.  A real TUI implementation
    would replace or extend this stub via a registry/adapter pattern without
    touching query_engine.py or query_loop.py.
    """

    mode: str = "repl"
    ready: bool = True
