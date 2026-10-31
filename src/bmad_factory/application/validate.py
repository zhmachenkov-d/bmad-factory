"""Validate Invoke — structural preflight (no Store / auth)."""

from __future__ import annotations

from pathlib import Path

from bmad_factory.application.envelope import (
    REASON_INVALID_MODE,
    REASON_METHOD_FLOOR,
    Envelope,
    preflight_failure_envelope,
    success_envelope,
)
from bmad_factory.application.layout import detect_invalid_mode, is_in_floor


def run_validate(root: Path) -> Envelope:
    """Run structural validate preflight against root; return shared envelope."""
    if detect_invalid_mode(root):
        return preflight_failure_envelope("validate", REASON_INVALID_MODE)
    if not is_in_floor(root):
        return preflight_failure_envelope("validate", REASON_METHOD_FLOOR)
    return success_envelope("validate")
