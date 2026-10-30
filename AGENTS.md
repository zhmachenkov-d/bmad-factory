<!-- bmad:context -->
<!-- Verified 2026-10-30 against bf9284c. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## bmad-factory

Product repository for bmad-factory. Python 3.14 with uv. Planning and BMad artifacts live in the polyrepo workspace that owns this worktree (`bmad-factory.specs/_bmad-output/`), not in this repo.

## Policy

- Never push commits directly to `main`; land changes only via pull request.
- Use Conventional Commits for every commit subject, PR title, and merge/squash subject.
- Never commit secrets or `.env` (`.env` is gitignored; still do not force-add it).
- New code ships with tests. Add Hypothesis property-based tests when they earn their keep (invariants, parsing, generators) — not by default for every change.
- CI (and local hooks where practical) must run AST-diff analysis and mutation testing, and publish both as SARIF for GitHub code scanning / check annotations — do not ship a pipeline that only runs unit tests. Prefer mature standalone tools; do not depend on earn-green until it is ready.

## Where things are

- This checkout is a worktree under the BMad workspace; open agent sessions from the workspace root when plans and code must be in one session.
- Product source and tooling will land in this repository once initialized — there is no application tree yet.

## Running and verifying

- Stack decision: Python 3.14 + uv. After `pyproject.toml` exists, prefer `uv run …` over bare tool invocations; treat exact commands below as TODO until verified on refresh.
- TODO: document and verify `uv run ruff`, `uv run mypy`, and `uv run pytest` (or the project's chosen test entry) once the project is initialized.
- TODO: choose and wire AST-diff and mutation-testing tools into CI/hooks with SARIF upload to GitHub; document exact invocations on refresh (candidates later — not earn-green until ready).
- Until CI/hooks enforce them, run ruff and mypy on changed Python before opening a PR.

## Conventions that differ from defaults

- Format and lint with ruff; typecheck with mypy — do not substitute other formatters/typecheckers for project Python.
- Property-based tests use Hypothesis when added.

<!-- /bmad:context -->
