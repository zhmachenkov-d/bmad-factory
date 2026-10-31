"""Normative CLI JSON envelope builder and exit helpers."""

from __future__ import annotations

import json
import sys
from typing import Any

EXIT_SUCCESS = 0
EXIT_PREFLIGHT = 40
EXIT_USAGE_ERROR = 60

REASON_SUCCESS = "success"
REASON_INVALID_MODE = "invalid-mode"
REASON_METHOD_FLOOR = "method-floor"
REASON_USAGE_ERROR = "usage-error"

Envelope = dict[str, Any]


def build_envelope(
    *,
    ok: bool,
    command: str,
    exit_code: int,
    reason: str,
    epic_complete: bool = False,
    fault_class: str | None = None,
    ticket_id: str | None = None,
    run_id: str | None = None,
    review: str | None = None,
    publish: dict[str, Any] | None = None,
    plan_status: str | None = None,
    message: str | None = None,
) -> Envelope:
    """Build the normative appendix-cli-contract JSON field object."""
    return {
        "ok": ok,
        "command": command,
        "exit_code": exit_code,
        "reason": reason,
        "fault_class": fault_class,
        "ticket_id": ticket_id,
        "run_id": run_id,
        "epic_complete": epic_complete,
        "review": review,
        "publish": publish,
        "plan_status": plan_status,
        "message": message,
    }


def success_envelope(command: str) -> Envelope:
    """Happy-path envelope: ok, exit 0, reason success, epic_complete false."""
    return build_envelope(
        ok=True,
        command=command,
        exit_code=EXIT_SUCCESS,
        reason=REASON_SUCCESS,
        epic_complete=False,
    )


def preflight_failure_envelope(command: str, reason: str) -> Envelope:
    """Preflight reject envelope: ok false, exit 40, nullables null."""
    return build_envelope(
        ok=False,
        command=command,
        exit_code=EXIT_PREFLIGHT,
        reason=reason,
        epic_complete=False,
    )


def envelope_json(envelope: Envelope) -> str:
    """Serialize envelope to a single JSON object string (no trailing newline)."""
    return json.dumps(envelope, separators=(",", ":"), ensure_ascii=False)


def print_envelope(envelope: Envelope) -> None:
    """Write exactly one JSON object to stdout (with optional trailing newline)."""
    sys.stdout.write(envelope_json(envelope) + "\n")
