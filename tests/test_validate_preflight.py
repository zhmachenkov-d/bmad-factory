"""Validate preflight I/O matrix: invalid-mode, method-floor, dual, bad --path."""

from __future__ import annotations

import json
import os
import shutil
import stat
from pathlib import Path

import pytest
from bmad_factory.cli.main import main


def _symlink_or_skip(link: Path, target: Path | str) -> None:
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlinks unavailable: {exc}")


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
        "below-floor/empty-epic-list",
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


def test_bad_path_missing_exits_60(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
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


@pytest.mark.parametrize("blank", ["", " ", "\t", "\n"])
def test_empty_path_exits_60(
    blank: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--path", blank])

    assert exc_info.value.code == 60
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err
    assert "must not be empty" in captured.err


def test_empty_path_json_exits_60_empty_stdout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", ""])

    assert exc_info.value.code == 60
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err
    assert "must not be empty" in captured.err


def test_path_with_nul_exits_60(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", "bad\0path"])

    assert exc_info.value.code == 60
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err
    assert "error" in captured.err.lower()


def _patch_unreadable_scandir(
    monkeypatch: pytest.MonkeyPatch,
    resolved: Path,
) -> list[bool]:
    """Force OSError on listability probe for ``resolved``; record hits."""
    hits = [False]
    real_scandir = os.scandir

    def fake_scandir(path: object) -> object:
        candidate = Path(path) if not isinstance(path, Path) else path
        if candidate.resolve() == resolved:
            hits[0] = True
            raise OSError("Permission denied")
        return real_scandir(path)

    monkeypatch.setattr(os, "scandir", fake_scandir)
    return hits


def test_unreadable_root_exits_60(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "unreadable"
    root.mkdir()
    hits = _patch_unreadable_scandir(monkeypatch, root.resolve())

    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--path", str(root)])

    assert hits[0] is True
    assert exc_info.value.code == 60
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "not readable" in captured.err


def test_unreadable_root_json_exits_60_empty_stdout(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "unreadable"
    root.mkdir()
    hits = _patch_unreadable_scandir(monkeypatch, root.resolve())

    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(root)])

    assert hits[0] is True
    assert exc_info.value.code == 60
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "not readable" in captured.err


_MARKER_NAMES = ("stories.yaml", "sprint-status.yaml", "epics.md")


@pytest.mark.parametrize("marker", _MARKER_NAMES)
@pytest.mark.parametrize(
    "target",
    [pytest.param(None, id="absolute"), pytest.param("missing-target", id="relative")],
)
def test_dangling_marker_symlink_is_invalid_mode(
    marker: str,
    target: str | None,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    link_target: Path | str = tmp_path / "missing-target" if target is None else target
    _symlink_or_skip(tmp_path / marker, link_target)

    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(tmp_path)])

    assert exc_info.value.code == 40
    captured = capsys.readouterr()
    assert captured.err == ""
    data = _parse_single_json_object(captured.out)
    _assert_preflight_reject(data, reason="invalid-mode")


@pytest.mark.parametrize("marker", _MARKER_NAMES)
def test_directory_marker_symlink_not_invalid_mode(
    marker: str,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    target = tmp_path / "real-dir"
    target.mkdir()
    _symlink_or_skip(tmp_path / marker, target)

    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(tmp_path)])

    assert exc_info.value.code == 40
    data = _parse_single_json_object(capsys.readouterr().out)
    assert data["reason"] != "invalid-mode"
    _assert_preflight_reject(data, reason="method-floor")


@pytest.mark.parametrize("marker", _MARKER_NAMES)
def test_dangling_marker_with_in_floor_sibling_is_invalid_mode(
    marker: str,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    shutil.copytree(FIXTURES / "in-floor", tmp_path, dirs_exist_ok=True)
    _symlink_or_skip(tmp_path / marker, "missing-target")

    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(tmp_path)])

    assert exc_info.value.code == 40
    data = _parse_single_json_object(capsys.readouterr().out)
    _assert_preflight_reject(data, reason="invalid-mode")


@pytest.mark.parametrize("marker", _MARKER_NAMES)
def test_fifo_marker_is_invalid_mode(
    marker: str,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    fifo = tmp_path / marker
    try:
        os.mkfifo(fifo, mode=stat.S_IRUSR | stat.S_IWUSR)
    except (AttributeError, OSError, NotImplementedError) as exc:
        pytest.skip(f"mkfifo unavailable: {exc}")

    with pytest.raises(SystemExit) as exc_info:
        main(["validate", "--json", "--path", str(tmp_path)])

    assert exc_info.value.code == 40
    data = _parse_single_json_object(capsys.readouterr().out)
    _assert_preflight_reject(data, reason="invalid-mode")


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
