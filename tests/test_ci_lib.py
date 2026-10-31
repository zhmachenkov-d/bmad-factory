"""Unit tests for .ci/lib.py Semgrep findings and mutation_score helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


def _repo_root() -> Path:
    """Real checkout root even when pytest runs under mutmut's mutants/ tree."""
    tests_dir = Path(__file__).resolve().parent
    parent = tests_dir.parent
    if parent.name == "mutants":
        return parent.parent
    return parent


_REPO_ROOT = _repo_root()
sys.path.insert(0, str(_REPO_ROOT / ".ci"))

import lib


def test_finding_id_format() -> None:
    assert (
        lib.finding_id("python.lang.x", "src/a.py", 12) == "python.lang.x|src/a.py|12"
    )


def test_findings_from_semgrep_json_multi_sorted() -> None:
    payload = {
        "results": [
            {
                "check_id": "z.check",
                "path": "src/b.py",
                "start": {"line": 2},
                "extra": {"message": "second"},
            },
            {
                "check_id": "a.check",
                "path": "src/a.py",
                "start": {"line": 1},
                "extra": {"message": "first"},
            },
        ]
    }
    findings = lib.findings_from_semgrep_json(payload)
    assert [f["id"] for f in findings] == [
        "a.check|src/a.py|1",
        "z.check|src/b.py|2",
    ]
    assert findings == sorted(findings, key=lambda f: f["id"])


def test_findings_from_semgrep_json_empty() -> None:
    assert lib.findings_from_semgrep_json({"results": []}) == []
    assert lib.findings_from_semgrep_json({}) == []


@pytest.mark.parametrize(
    ("stats", "expected"),
    [
        ({"total": 10, "skipped": 2, "killed": 6, "timeout": 1}, 87),
        ({"total": 5, "skipped": 5, "killed": 3, "timeout": 0}, 0),
        ({"total": 0, "skipped": 0, "killed": 0, "timeout": 0}, 0),
        ({"total": 3, "skipped": 5, "killed": 1, "timeout": 0}, 0),
    ],
)
def test_mutation_score(stats: dict[str, int], expected: int) -> None:
    assert lib.mutation_score(stats) == expected
