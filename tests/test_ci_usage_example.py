"""Artifact checks for examples/ci-usage (no subprocess CLI invokes)."""

from __future__ import annotations

import re

from tests.repo_root import repo_root

REPO_ROOT = repo_root()
EXAMPLES = REPO_ROOT / "examples" / "ci-usage"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def test_ci_usage_example_files_mention_install_validate_status() -> None:
    readme = EXAMPLES / "README.md"
    workflow = EXAMPLES / "github-workflow.yml"
    fixture = EXAMPLES / "fixtures" / "invalid-mode" / "stories.yaml"

    assert readme.is_file()
    assert workflow.is_file()
    assert fixture.is_file()

    readme_text = readme.read_text(encoding="utf-8").lower()
    workflow_text = workflow.read_text(encoding="utf-8").lower()
    combined = f"{readme_text}\n{workflow_text}"

    assert "install" in combined or "uv sync" in combined or "uvx" in combined
    assert "validate" in combined
    assert "status" in combined
    assert "uv" in combined


def test_no_operator_bmad_usage_workflow_under_github() -> None:
    """Non-quality workflows must not claim Operator BMAD as product CI."""
    assert WORKFLOWS.is_dir()

    quality_name = re.compile(r"^quality-.*\.yml$")
    for path in sorted(WORKFLOWS.glob("*.yml")):
        if quality_name.match(path.name):
            continue
        text = path.read_text(encoding="utf-8").lower()
        mentions_product = "bmad-factory" in text
        documents_usage = (
            "validate" in text
            and "status" in text
            and ("install" in text or "uv sync" in text or "uvx" in text)
        )
        assert not mentions_product and not documents_usage, (
            f"Operator BMAD usage must not live under .github/workflows/: {path.name}"
        )
