"""Unit tests for .ci/lib.py Semgrep findings and mutation_score helpers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tests.repo_root import repo_root

_REPO_ROOT = repo_root()
sys.path.insert(0, str(_REPO_ROOT / ".ci"))

import lib


def test_finding_id_format() -> None:
    assert (
        lib.finding_id("python.lang.x", "src/a.py", "msg")
        == "python.lang.x|src/a.py|msg"
    )


def test_findings_from_semgrep_json_multi_sorted() -> None:
    # Same check_id, different paths: sort-by-check_id would keep input order
    # (b then a); sort-by-id must put src/a.py before src/b.py.
    payload = {
        "results": [
            {
                "check_id": "same.rule",
                "path": "src/b.py",
                "start": {"line": 1},
                "extra": {"message": "b"},
            },
            {
                "check_id": "same.rule",
                "path": "src/a.py",
                "start": {"line": 1},
                "extra": {"message": "a"},
            },
        ]
    }
    findings = lib.findings_from_semgrep_json(payload)
    assert findings == [
        {
            "id": "same.rule|src/a.py|a",
            "check_id": "same.rule",
            "path": "src/a.py",
            "start_line": 1,
            "message": "a",
        },
        {
            "id": "same.rule|src/b.py|b",
            "check_id": "same.rule",
            "path": "src/b.py",
            "start_line": 1,
            "message": "b",
        },
    ]


def test_findings_line_shift_same_id() -> None:
    """Same check/path/message at different start_line → same fingerprint id."""
    base = {
        "check_id": "rule.x",
        "path": "src/a.py",
        "extra": {"message": "msg"},
    }
    at_10 = lib.findings_from_semgrep_json(
        {"results": [{**base, "start": {"line": 10}}]}
    )
    at_11 = lib.findings_from_semgrep_json(
        {"results": [{**base, "start": {"line": 11}}]}
    )
    assert at_10[0]["id"] == at_11[0]["id"] == "rule.x|src/a.py|msg"
    assert at_10[0]["start_line"] == 10
    assert at_11[0]["start_line"] == 11
    baseline_ids = {at_10[0]["id"]}
    assert at_11[0]["id"] in baseline_ids


def test_findings_from_semgrep_json_empty() -> None:
    assert lib.findings_from_semgrep_json({"results": []}) == []
    assert lib.findings_from_semgrep_json({}) == []


def test_empty_sarif_mutmut_has_information_uri() -> None:
    sarif = lib.empty_sarif("mutmut")
    driver = sarif["runs"][0]["tool"]["driver"]
    assert driver["name"] == "mutmut"
    assert driver["informationUri"] == "https://github.com/boxed/mutmut"


def test_empty_sarif_non_mutmut_omits_information_uri() -> None:
    sarif = lib.empty_sarif("semgrep")
    driver = sarif["runs"][0]["tool"]["driver"]
    assert driver["name"] == "semgrep"
    assert "informationUri" not in driver


@pytest.mark.parametrize(
    ("stats", "expected"),
    [
        ({"total": 10, "skipped": 2, "killed": 6, "timeout": 1}, 87),
        ({"total": 4, "skipped": 0, "killed": 0, "timeout": 2}, 50),
        ({"total": 3, "skipped": 0, "killed": 3, "timeout": 0}, 100),
        ({"total": 5, "skipped": 5, "killed": 3, "timeout": 0}, 0),
        ({"total": 0, "skipped": 0, "killed": 0, "timeout": 0}, 0),
        ({"total": 3, "skipped": 5, "killed": 1, "timeout": 0}, 0),
    ],
)
def test_mutation_score(stats: dict[str, int], expected: int) -> None:
    assert lib.mutation_score(stats) == expected


_MINIMAL_PYPROJECT = """\
[project]
name = "tmp"
version = "0.0.0"

[tool.mutmut]
paths_to_mutate = ["src/"]
"""


def _write_temp_pyproject(tmp_path: Path) -> Path:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(_MINIMAL_PYPROJECT, encoding="utf-8")
    return pyproject


def test_temporary_only_mutate_restores_on_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pyproject = _write_temp_pyproject(tmp_path)
    original = pyproject.read_text(encoding="utf-8")
    monkeypatch.setattr(lib, "PYPROJECT", pyproject)

    with lib.temporary_only_mutate(["src/a.py"]):
        mid = pyproject.read_text(encoding="utf-8")
        assert "only_mutate" in mid
        assert '["src/a.py"]' in mid or "src/a.py" in mid

    assert pyproject.read_text(encoding="utf-8") == original


def test_temporary_only_mutate_restores_on_exception(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pyproject = _write_temp_pyproject(tmp_path)
    original = pyproject.read_text(encoding="utf-8")
    monkeypatch.setattr(lib, "PYPROJECT", pyproject)

    with (
        pytest.raises(RuntimeError, match="boom"),
        lib.temporary_only_mutate(["src/a.py"]),
    ):
        assert "only_mutate" in pyproject.read_text(encoding="utf-8")
        raise RuntimeError("boom")

    assert pyproject.read_text(encoding="utf-8") == original


def test_temporary_only_mutate_restores_on_system_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pyproject = _write_temp_pyproject(tmp_path)
    original = pyproject.read_text(encoding="utf-8")
    monkeypatch.setattr(lib, "PYPROJECT", pyproject)

    with (
        pytest.raises(SystemExit) as exc_info,
        lib.temporary_only_mutate(["src/a.py"]),
    ):
        assert "only_mutate" in pyproject.read_text(encoding="utf-8")
        raise SystemExit(1)

    assert exc_info.value.code == 1
    assert pyproject.read_text(encoding="utf-8") == original


def test_temporary_only_mutate_restores_on_called_process_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pyproject = _write_temp_pyproject(tmp_path)
    original = pyproject.read_text(encoding="utf-8")
    monkeypatch.setattr(lib, "PYPROJECT", pyproject)

    with (
        pytest.raises(subprocess.CalledProcessError),
        lib.temporary_only_mutate(["src/a.py"]),
    ):
        assert "only_mutate" in pyproject.read_text(encoding="utf-8")
        raise subprocess.CalledProcessError(1, ["mutmut", "run"])

    assert pyproject.read_text(encoding="utf-8") == original
