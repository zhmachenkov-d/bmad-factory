"""Earned Hypothesis property tests for normative envelope invariants."""

from __future__ import annotations

import json
from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from bmad_factory.application import envelope

REQUIRED_KEYS = frozenset(
    {
        "ok",
        "command",
        "exit_code",
        "reason",
        "fault_class",
        "ticket_id",
        "run_id",
        "epic_complete",
        "review",
        "publish",
        "plan_status",
        "message",
    }
)

commands = st.sampled_from(
    [
        "validate",
        "build",
        "resume",
        "resolve",
        "finalize-on-merge",
        "epic-close",
        "status",
    ]
)
reasons = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)), min_size=1, max_size=64
)
optional_str = st.one_of(st.none(), st.text(max_size=32))
optional_publish = st.one_of(
    st.none(),
    st.fixed_dictionaries({"pr": st.text(min_size=1, max_size=64)}),
)


@given(
    ok=st.booleans(),
    command=commands,
    exit_code=st.integers(min_value=0, max_value=255),
    reason=reasons,
    epic_complete=st.booleans(),
    fault_class=optional_str,
    ticket_id=optional_str,
    run_id=optional_str,
    review=optional_str,
    publish=optional_publish,
    plan_status=optional_str,
    message=optional_str,
)
def test_build_envelope_normative_field_invariants(
    ok: bool,
    command: str,
    exit_code: int,
    reason: str,
    epic_complete: bool,
    fault_class: str | None,
    ticket_id: str | None,
    run_id: str | None,
    review: str | None,
    publish: dict[str, Any] | None,
    plan_status: str | None,
    message: str | None,
) -> None:
    result = envelope.build_envelope(
        ok=ok,
        command=command,
        exit_code=exit_code,
        reason=reason,
        epic_complete=epic_complete,
        fault_class=fault_class,
        ticket_id=ticket_id,
        run_id=run_id,
        review=review,
        publish=publish,
        plan_status=plan_status,
        message=message,
    )
    assert set(result) == REQUIRED_KEYS
    assert result["ok"] is ok
    assert result["command"] == command
    assert result["exit_code"] == exit_code
    assert result["reason"] == reason
    assert result["epic_complete"] is epic_complete
    assert isinstance(result["epic_complete"], bool)
    payload = envelope.envelope_json(result)
    assert "\n" not in payload
    roundtrip = json.loads(payload)
    assert roundtrip == result


@given(command=commands)
def test_success_envelope_invariants(command: str) -> None:
    result = envelope.success_envelope(command)
    assert set(result) == REQUIRED_KEYS
    assert result["ok"] is True
    assert result["exit_code"] == envelope.EXIT_SUCCESS
    assert result["reason"] == envelope.REASON_SUCCESS
    assert result["epic_complete"] is False
    assert result["command"] == command
