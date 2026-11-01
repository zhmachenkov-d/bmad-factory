"""Unit tests for mutmut→SARIF properties.status via collect_results path."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tests.repo_root import repo_root

_REPO_ROOT = repo_root()
sys.path.insert(0, str(_REPO_ROOT / ".ci"))

import mutmut_to_sarif

# Exit codes → expected properties.status (Requirements / Finding 12).
_CASES: list[tuple[str, int | None, str]] = [
    ("key-0", 0, "survived"),
    ("key-1", 1, "killed"),
    ("key-3", 3, "killed"),
    ("key-5", 5, "no_tests"),
    ("key-33", 33, "no_tests"),
    ("key-34", 34, "skipped"),
    ("key-36", 36, "timeout"),
    ("key-none", None, "not_checked"),
    ("key-unknown", 99, "suspicious"),
]


def test_collect_results_status_and_mutant_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(mutmut_to_sarif, "REPO_ROOT", tmp_path)

    meta_dir = tmp_path / "mutants" / "src"
    meta_dir.mkdir(parents=True)
    meta_path = meta_dir / "sample.py.meta"
    exit_code_by_key = {key: code for key, code, _ in _CASES}
    meta_path.write_text(
        json.dumps({"exit_code_by_key": exit_code_by_key}),
        encoding="utf-8",
    )

    results = mutmut_to_sarif.collect_results(None)
    assert len(results) == len(_CASES)

    by_mutant = {r["properties"]["mutant"]: r for r in results}
    for key, _code, expected_status in _CASES:
        assert key in by_mutant
        props = by_mutant[key]["properties"]
        assert props["status"] == expected_status
        assert props["mutant"] == key

    sarif = mutmut_to_sarif.build_sarif()
    sarif_results = sarif["runs"][0]["results"]
    assert len(sarif_results) == len(_CASES)
    for result in sarif_results:
        assert result["properties"]["mutant"] in {key for key, _, _ in _CASES}
        expected = next(
            status for key, _, status in _CASES if key == result["properties"]["mutant"]
        )
        assert result["properties"]["status"] == expected
