<!-- bmad:context -->
<!-- Verified 2026-11-01 against c1b46d5761ff3fba8bb6d6e14732ffa420ff49a9. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## bmad-factory

Product repository for bmad-factory. Python 3.14 with uv. Planning and BMad artifacts live in the polyrepo workspace that owns this worktree (`bmad-factory.specs/_bmad-output/`), not in this repo.

## Policy

- Never push commits directly to `main`; land changes only via pull request.
- Use Conventional Commits for every commit subject, PR title, and merge/squash subject.
- Never commit secrets or `.env` (`.env` is gitignored; still do not force-add it).
- New code ships with tests. Add Hypothesis property-based tests when they earn their keep (invariants, parsing, generators) — not by default for every change.
- CI must run AST-diff analysis and mutation testing and publish both as SARIF for GitHub code scanning / check annotations; local hooks where practical run the same analysis without uploading — do not ship a pipeline that only runs unit tests. Prefer mature standalone tools; do not depend on earn-green until it is ready.

## Where things are

- This checkout is a worktree under the BMad workspace; open agent sessions from the workspace root when plans and code must be in one session.
- Package layout: `src/bmad_factory/` (cli, application, …), tests under `tests/`, quality glue under `.ci/` (not importable product code).

## Running and verifying

- Stack: Python 3.14 + uv. Prefer `uv run …` over bare tool invocations.
- Before committing Python changes, fix lint/format (do not skip even if hooks are installed):
  - `uv run ruff check --fix src tests`
  - `uv run ruff format src tests`
- Lint / type / unit+property tests (CI / verify; check-only, no autofix):
  - `uv run ruff check src tests`
  - `uv run ruff format --check src tests`
  - `uv run mypy src`
  - `uv run pytest`
- AST-diff (Semgrep, diff-aware when a base commit is known):
  - Local / hooks: `uv run python .ci/run_semgrep.py`
  - With PR base: `uv run python .ci/run_semgrep.py --baseline-commit <base-sha>`
  - Compare vs in-repo baseline: `uv run python .ci/run_semgrep.py --compare-baseline`
- Mutation testing (mutmut):
  - Diff-scoped (changed `src/` only; survivors do not fail): `uv run python .ci/run_mutmut_diff.py` (CI: add `--base-ref <base-sha>`)
  - Full suite vs baseline: `uv run python .ci/run_mutmut_full.py --compare-baseline`
- SARIF upload (CI only — GitHub code scanning): workflows call `github/codeql-action/upload-sarif` on `.ci/out/semgrep.sarif`, `.ci/out/mutmut-diff.sarif`, and `.ci/out/mutmut-full.sarif`. Locally, the same analysis commands write those SARIF files under `.ci/out/` without uploading.
- Owner notify on worsen: one aggregated Slack payload via `.ci/slack_notify.py` + `slackapi/slack-github-action` incoming-webhook (`SLACK_WEBHOOK_URL`). Dry-run / HITL fixture: `uv run python .ci/run_worsen_fixture.py`.
- Baseline bump rule: see `.ci/README.md` — only bump `.ci/baselines/` when intentionally accepting a new Semgrep finding or a lower mutmut score.
- Pre-commit: `uv run pre-commit install` then hooks run ruff check --fix, ruff format, Semgrep, and diff-scoped mutmut on Python changes.
- Further Hypothesis PBTs: add only when earned (invariants / parsing / generators); envelope field invariants already have an earned module in `tests/test_envelope_properties.py`.

## Conventions that differ from defaults

- Format and lint with ruff; typecheck with mypy — do not substitute other formatters/typecheckers for project Python.
- Property-based tests use Hypothesis when added.
- Quality CI lives in this product repo’s `.github/workflows/` (not Operator BMAD Action YAML).

<!-- /bmad:context -->
