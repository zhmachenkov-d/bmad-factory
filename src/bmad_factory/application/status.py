"""Status-only viewer Invoke — envelope shell (no Store / RunState / TUI)."""

from __future__ import annotations

from bmad_factory.application.envelope import Envelope, success_envelope


def run_status() -> Envelope:
    """Return the normative success envelope for the status viewer."""
    return success_envelope("status")
