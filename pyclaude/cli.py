from __future__ import annotations

import argparse

from pyclaude import __version__
from pyclaude.bootstrap import run_cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pyclaude")
    parser.add_argument("prompt", nargs="?")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--print-commands", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> dict:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        return {"mode": "version", "version": __version__}

    return run_cli(args)
