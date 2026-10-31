# CI usage example (not a product Action)

Copy and adapt these files into **your** GitHub-like workflow. This directory is a
usage example only — **not** a shipped production GitHub Action. Product-repo
quality CI (`.github/workflows/quality-*.yml`) is unrelated.

Pasteable skeleton: [`github-workflow.yml`](./github-workflow.yml) — one job:
install → `validate --json` → `status --json`.

## Install

Until `bmad-factory` is on public PyPI, install from **bmad-factory package
sources** (path or git) — not from an Operator ticket-tree alone. A plain
`uv sync` in a foreign ticket-tree repo does not install this CLI.

**Foreign ticket-tree / CI (path or git URL to the package):**

```bash
uvx --from ./path-or-git-to-bmad-factory bmad-factory --help
# e.g. uvx --from git+https://github.com/EXAMPLE/bmad-factory.git bmad-factory --help
```

**Same-repo product checkout demo only:**

```bash
uv sync
uv run bmad-factory --help
# or: uvx --from . bmad-factory --help
```

After PyPI publish you can use `uvx bmad-factory` / `pipx run bmad-factory` the
same way — no publish gate is required to follow this example.

See [`github-workflow.yml`](./github-workflow.yml) for the pasteable one-job
skeleton (`BMAD_FACTORY_FROM` + optional second checkout).

## Validate preflight (`--json`)

Run validate against a ticket-tree root (or a fixture path for demos):

```bash
uvx --from ./path-or-git-to-bmad-factory bmad-factory validate --json --path <ticket-tree-or-fixture>
# same-repo demo: uv run bmad-factory validate --json --path <…>
```

CI should branch on the process exit code and the JSON `reason` field — do not
scrape human logs.

### Reject demo: `invalid-mode` (exit 40)

This tree includes a tiny self-contained fixture so you can exercise the reject
path without depending on `tests/fixtures`:

```bash
# From a product checkout (same-repo demo):
uv run bmad-factory validate --json --path examples/ci-usage/fixtures/invalid-mode
```

Expected: **exit 40**, JSON `reason` = `invalid-mode` (top-level `stories.yaml`
marks unsupported sprint/stories mode).

### Other exit-40 reason: `method-floor` (docs only)

`validate` also exits **40** with `reason` = `method-floor` when the context is
below the BMAD ≥ 6.13-next ticket-tree Store/layout floor (no runnable second
fixture in this example). Treat both `invalid-mode` and `method-floor` as
preflight rejects in your workflow branching.

## Status viewer (`--json`)

Status-only — not a full TUI:

```bash
uvx --from ./path-or-git-to-bmad-factory bmad-factory status --json
# same-repo demo: uv run bmad-factory status --json
```

Expected: **exit 0**, JSON `command` = `status` on the success path.

## Workflow notes

- Keep the paste to **one job** for this skeleton: install → validate → status.
- Later Invokes (`build`, `resume` / `resolve`, `finalize-on-merge`, `epic-close`)
  belong in **your** adapted workflow; they appear only as comments in
  `github-workflow.yml`, never as stub runnable steps here.
- Do not treat product-repo `quality-*.yml` workflows as the Operator usage example.
