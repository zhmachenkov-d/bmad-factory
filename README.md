# bmad-factory

Deterministic CI orchestrator for BMAD ticket trees. Operators embed the CLI in
their own GitHub-like workflows; the product ships a CLI contract and a usage
example — not production Action YAML.

## Install

Requires CPython 3.14 and [uv](https://docs.astral.sh/uv/).

From a checkout (until the package is on public PyPI):

```bash
uv sync
uv run bmad-factory --help
```

Or one-shot without a sync:

```bash
uvx --from . bmad-factory --help
```

## CI usage example

Operator paste path (install, validate, status): [`examples/ci-usage/`](examples/ci-usage/).
