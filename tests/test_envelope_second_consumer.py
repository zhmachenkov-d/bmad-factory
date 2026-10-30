"""Test-only second consumer of application.envelope (no production stub Invoke)."""

from __future__ import annotations

from bmad_factory.application import envelope
from bmad_factory.application.validate import run_validate


def test_second_consumer_shares_envelope_shape() -> None:
    via_validate = run_validate()
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
