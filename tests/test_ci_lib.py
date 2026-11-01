"""Unit tests for .ci/lib.py Semgrep findings and mutation_score helpers."""

from __future__ import annotations

import sys

import pytest

from tests.repo_root import repo_root

_REPO_ROOT = repo_root()
sys.path.insert(0, str(_REPO_ROOT / ".ci"))

import lib


def test_finding_id_format() -> None:
    assert (
        lib.finding_id("python.lang.x", "src/a.py", 12) == "python.lang.x|src/a.py|12"
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
            "id": "same.rule|src/a.py|1",
            "check_id": "same.rule",
            "path": "src/a.py",
            "start_line": 1,
            "message": "a",
        },
        {
            "id": "same.rule|src/b.py|1",
            "check_id": "same.rule",
            "path": "src/b.py",
            "start_line": 1,
            "message": "b",
        },
    ]


def test_findings_from_semgrep_json_empty() -> None:
    assert lib.findings_from_semgrep_json({"results": []}) == []
    assert lib.findings_from_semgrep_json({}) == []


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
