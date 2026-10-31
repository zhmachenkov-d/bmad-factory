"""Happy-path validate --json I/O matrix (in-floor fixture)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bmad_factory.cli.main import main

NULLABLE_FIELDS = (
    "fault_class",
    "ticket_id",
    "run_id",
    "review",
    "publish",
    "plan_status",
    "message",
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "validate"
IN_FLOOR = FIXTURES / "in-floor"


def _parse_single_json_object(stdout: str) -> dict[object, object]:
    text = stdout.removesuffix("\n")
    assert "\n" not in text, "stdout must be exactly one JSON object"
    data = json.loads(text)
    assert isinstance(data, dict)
    return data


def test_validate_json_happy_path(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(IN_FLOOR)])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    data = _parse_single_json_object(captured.out)

    assert data["ok"] is True
    assert data["command"] == "validate"
    assert data["exit_code"] == 0
    assert data["reason"] == "success"
    assert data["epic_complete"] is False
    for field in NULLABLE_FIELDS:
        assert data[field] is None
