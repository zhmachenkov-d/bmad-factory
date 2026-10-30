"""Validate Invoke — happy path only (no Store / method-floor checks)."""

from __future__ import annotations

from bmad_factory.application.envelope import Envelope, success_envelope


def run_validate() -> Envelope:
    """Return the happy-path validate envelope (empty args; no ticket-tree checks)."""
    return success_envelope("validate")
