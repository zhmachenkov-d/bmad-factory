"""Resolve the real checkout root when tests run under mutmut's mutants/ tree."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Real checkout root even when pytest runs under mutmut's mutants/ tree.

    mutmut copies tests into mutants/tests/ but not examples/, .ci/, or .github/.
    """
    tests_dir = Path(__file__).resolve().parent
    parent = tests_dir.parent
    if parent.name == "mutants":
        return parent.parent
    return parent
