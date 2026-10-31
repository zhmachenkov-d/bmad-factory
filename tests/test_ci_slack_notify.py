"""Unit tests for .ci/slack_notify.collect_factors (no network)."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    """Real checkout root even when pytest runs under mutmut's mutants/ tree."""
    tests_dir = Path(__file__).resolve().parent
    parent = tests_dir.parent
    if parent.name == "mutants":
        return parent.parent
    return parent


_REPO_ROOT = _repo_root()
sys.path.insert(0, str(_REPO_ROOT / ".ci"))

import slack_notify


def test_collect_factors_semgrep_mutmut_skip_and_missing(tmp_path: Path) -> None:
    semgrep = tmp_path / "semgrep-worsen.json"
    mutmut = tmp_path / "mutmut-worsen.json"
    not_worsened = tmp_path / "ok.json"
    missing = tmp_path / "does-not-exist.json"

    semgrep.write_text(
        json.dumps(
            {
                "baseline_count": 0,
                "current_count": 1,
                "new_findings": [
                    {
                        "check_id": "python.lang.security.audit.fixture",
                        "id": "python.lang.security.audit.fixture|src/fixture.py|1",
                        "message": "fixture finding",
                        "path": "src/fixture.py",
                        "start_line": 1,
                    }
                ],
                "tool": "semgrep",
                "worsened": True,
            }
        ),
        encoding="utf-8",
    )
    # Omit threshold — Requirements: default threshold 1 when omitted.
    mutmut.write_text(
        json.dumps(
            {
                "baseline_score": 80,
                "current_score": 70,
                "drop": 10,
                "tool": "mutmut",
                "worsened": True,
            }
        ),
        encoding="utf-8",
    )
    not_worsened.write_text(
        json.dumps(
            {
                "tool": "semgrep",
                "worsened": False,
                "new_findings": [],
            }
        ),
        encoding="utf-8",
    )

    factors = slack_notify.collect_factors([semgrep, mutmut, not_worsened, missing])
    assert factors == [
        "semgrep: 1 new finding(s) vs baseline",
        "mutmut: score 80 → 70 (drop 10 ≥ 1)",
    ]
