"""Unit tests for .ci/slack_notify.collect_factors (no network)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tests.repo_root import repo_root

_REPO_ROOT = repo_root()
sys.path.insert(0, str(_REPO_ROOT / ".ci"))

import slack_notify


def test_collect_factors_semgrep_mutmut_skip_and_missing(tmp_path: Path) -> None:
    semgrep = tmp_path / "semgrep-worsen.json"
    mutmut = tmp_path / "mutmut-worsen.json"
    not_worsened = tmp_path / "ok.json"
    missing = tmp_path / "does-not-exist.json"

    # current_count deliberately diverges from len(new_findings); n must use len.
    semgrep.write_text(
        json.dumps(
            {
                "baseline_count": 0,
                "current_count": 5,
                "new_findings": [
                    {
                        "check_id": "python.lang.security.audit.fixture",
                        "id": "python.lang.security.audit.fixture|src/fixture.py|1",
                        "message": "fixture finding",
                        "path": "src/fixture.py",
                        "start_line": 1,
                    },
                    {
                        "check_id": "python.lang.security.audit.other",
                        "id": "python.lang.security.audit.other|src/other.py|2",
                        "message": "other finding",
                        "path": "src/other.py",
                        "start_line": 2,
                    },
                ],
                "tool": "semgrep",
                "worsened": True,
            }
        ),
        encoding="utf-8",
    )
    # Omit threshold — Requirements: default threshold 1 when omitted.
    # drop deliberately diverges from baseline_score - current_score.
    mutmut.write_text(
        json.dumps(
            {
                "baseline_score": 80,
                "current_score": 70,
                "drop": 3,
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
        "semgrep: 2 new finding(s) vs baseline",
        "mutmut: score 80 → 70 (drop 3 ≥ 1)",
    ]


def test_collect_factors_mutmut_explicit_threshold(tmp_path: Path) -> None:
    mutmut = tmp_path / "mutmut-worsen.json"
    mutmut.write_text(
        json.dumps(
            {
                "baseline_score": 90,
                "current_score": 80,
                "drop": 10,
                "threshold": 5,
                "tool": "mutmut",
                "worsened": True,
            }
        ),
        encoding="utf-8",
    )

    assert slack_notify.collect_factors([mutmut]) == [
        "mutmut: score 90 → 80 (drop 10 ≥ 5)",
    ]
