"""TUI/REPL launcher - assembly boundary for external TUI integration.

This module encapsulates the REPL session assembly logic, allowing main.py
to delegate without exposing implementation details.
"""
from dataclasses import asdict

from pyclaude.tui.stub import ReplSession


def build_repl_session() -> dict:
    """Assemble REPL session metadata.

    Returns:
        dict: Contains 'repl_session' key with stub metadata (mode, ready).
    """
    return {
        "repl_session": asdict(ReplSession()),
    }
