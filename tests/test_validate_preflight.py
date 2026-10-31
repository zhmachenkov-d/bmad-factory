"""Validate preflight I/O matrix: invalid-mode, method-floor, dual, bad --path."""

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

FORBIDDEN_REASONS = frozenset({"store-auth", "store-incompatible"})

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "validate"


def _parse_single_json_object(stdout: str) -> dict[object, object]:
    text = stdout.removesuffix("\n")
    assert "\n" not in text, "stdout must be exactly one JSON object"
    data = json.loads(text)
    assert isinstance(data, dict)
    return data


def _assert_preflight_reject(
    data: dict[object, object],
    *,
    reason: str,
) -> None:
    assert data["ok"] is False
    assert data["command"] == "validate"
    assert data["exit_code"] == 40
    assert data["reason"] == reason
    assert data["reason"] not in FORBIDDEN_REASONS
    assert data["epic_complete"] is False
    for field in NULLABLE_FIELDS:
        assert data[field] is None


@pytest.mark.parametrize(
    "fixture_name",
    [
        "invalid-mode-stories",
        "invalid-mode-sprint",
        "invalid-mode-epics",
    ],
)
def test_invalid_mode_json(
    fixture_name: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = FIXTURES / fixture_name
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(path)])

    assert exc_info.value.code == 40
    captured = capsys.readouterr()
    assert captured.err == ""
    data = _parse_single_json_object(captured.out)
    _assert_preflight_reject(data, reason="invalid-mode")


@pytest.mark.parametrize(
    "relative",
    [
        "below-floor/empty",
        "below-floor/bad-toml",
        "below-floor/blank-slug",
        "below-floor/missing-epic-dir",
        "below-floor/missing-md",
    ],
)
def test_method_floor_json(
    relative: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = FIXTURES / relative
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(path)])

    assert exc_info.value.code == 40
    captured = capsys.readouterr()
    assert captured.err == ""
    data = _parse_single_json_object(captured.out)
    _assert_preflight_reject(data, reason="method-floor")


def test_in_floor_happy_path_json(capsys: pytest.CaptureFixture[str]) -> None:
    path = FIXTURES / "in-floor"
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(path)])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    data = _parse_single_json_object(captured.out)
    assert data["ok"] is True
    assert data["command"] == "validate"
    assert data["exit_code"] == 0
    assert data["reason"] == "success"
    assert data["reason"] not in FORBIDDEN_REASONS
    assert data["epic_complete"] is False
    for field in NULLABLE_FIELDS:
        assert data[field] is None


def test_in_floor_with_broken_sibling_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = FIXTURES / "in-floor-with-broken"
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(path)])

    assert exc_info.value.code == 0
    data = _parse_single_json_object(capsys.readouterr().out)
    assert data["reason"] == "success"


def test_dual_signals_invalid_mode_wins(capsys: pytest.CaptureFixture[str]) -> None:
    path = FIXTURES / "dual-signals"
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(path)])

    assert exc_info.value.code == 40
    data = _parse_single_json_object(capsys.readouterr().out)
    _assert_preflight_reject(data, reason="invalid-mode")


@pytest.mark.parametrize(
    "relative",
    [
        "invalid-mode-stories",
        "below-floor/empty",
        "dual-signals",
    ],
)
def test_preflight_without_json_no_stdout_json(
    relative: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = FIXTURES / relative
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--path", str(path)])

    assert exc_info.value.code == 40
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "{" not in captured.out


def test_bad_path_missing_exits_60(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(missing)])

    assert exc_info.value.code == 60
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err
    assert "error" in captured.err.lower() or "usage" in captured.err.lower()


def test_bad_path_not_directory_exits_60(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "not-a-dir.txt"
    file_path.write_text("x\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(file_path)])

    assert exc_info.value.code == 60
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err
    assert "error" in captured.err.lower() or "usage" in captured.err.lower()


def test_empty_slug_key_missing_is_method_floor(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    initiative = tmp_path / "initiative-demo"
    tickets = initiative / "tickets"
    tickets.mkdir(parents=True)
    (initiative / "initiative-demo.md").write_text("# demo\n", encoding="utf-8")
    (tickets / "tickets.toml").write_text(
        '[[epic]]\ntitle = "no slug key"\n',
        encoding="utf-8",
    )
    (tickets / "epic-cli-contract").mkdir()

    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(tmp_path)])

    assert exc_info.value.code == 40
    data = _parse_single_json_object(capsys.readouterr().out)
    _assert_preflight_reject(data, reason="method-floor")


@pytest.mark.parametrize(
    "epic_slug",
    [".", "..", "a/b", "a\\b", "/tmp", "../tickets"],
)
def test_unsafe_epic_slug_is_method_floor(
    epic_slug: str,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    initiative = tmp_path / "initiative-demo"
    tickets = initiative / "tickets"
    tickets.mkdir(parents=True)
    (initiative / "initiative-demo.md").write_text("# demo\n", encoding="utf-8")
    # Valid sibling so a naive Path join could resolve to an existing dir.
    (tickets / "epic-cli-contract").mkdir()
    (tickets / "tickets.toml").write_text(
        f'[[epic]]\nslug = "{epic_slug}"\ntitle = "unsafe"\n',
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(tmp_path)])

    assert exc_info.value.code == 40
    data = _parse_single_json_object(capsys.readouterr().out)
    _assert_preflight_reject(data, reason="method-floor")
