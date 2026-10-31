"""Test-only second consumer of application.envelope (no production stub Invoke)."""

from __future__ import annotations

from pathlib import Path

from bmad_factory.application import envelope
from bmad_factory.application.status import run_status
from bmad_factory.application.validate import run_validate

IN_FLOOR = Path(__file__).resolve().parent / "fixtures" / "validate" / "in-floor"


def test_second_consumer_shares_envelope_shape() -> None:
    via_validate = run_validate(IN_FLOOR)
    via_builder = envelope.build_envelope(
        ok=True,
        command="validate",
        exit_code=envelope.EXIT_SUCCESS,
        reason=envelope.REASON_SUCCESS,
        epic_complete=False,
    )
    via_success = envelope.success_envelope("validate")

    assert set(via_validate) == set(via_builder) == set(via_success)
    assert via_validate == via_builder == via_success


def test_status_shares_envelope_shape() -> None:
    via_status = run_status()
    via_success = envelope.success_envelope("status")
    assert via_status == via_success
    assert set(via_status) == set(via_success)


def test_second_consumer_shares_preflight_failure_shape() -> None:
    via_builder = envelope.preflight_failure_envelope(
        "validate",
        envelope.REASON_METHOD_FLOOR,
    )
    via_manual = envelope.build_envelope(
        ok=False,
        command="validate",
        exit_code=envelope.EXIT_PREFLIGHT,
        reason=envelope.REASON_METHOD_FLOOR,
        epic_complete=False,
    )
    assert via_builder == via_manual
    assert via_builder["exit_code"] == 40
