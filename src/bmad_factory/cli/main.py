"""CLI composition root for bmad-factory Invokes."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import NoReturn

from bmad_factory.application.envelope import EXIT_USAGE_ERROR, print_envelope
from bmad_factory.application.validate import run_validate


class _CliParser(argparse.ArgumentParser):
    """ArgumentParser that maps usage/argument errors to exit code 60."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(EXIT_USAGE_ERROR, f"{self.prog}: error: {message}\n")


def _build_parser() -> _CliParser:
    parser = _CliParser(prog="bmad-factory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Happy-path preflight stub (no ticket-tree or Store checks yet)",
    )
    validate_parser.add_argument(
        "--json",
        action="store_true",
        dest="json_out",
        help="Emit the normative JSON envelope on stdout",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Parse argv, dispatch Invokes, print JSON when requested, exit with exit_code."""
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "validate":
        envelope = run_validate()
        if args.json_out:
            print_envelope(envelope)
        raise SystemExit(int(envelope["exit_code"]))

    # Unreachable when subparsers.required=True; keep fail-closed.
    raise SystemExit(EXIT_USAGE_ERROR)


if __name__ == "__main__":
    main()
