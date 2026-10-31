#!/usr/bin/env python3
"""Build one aggregated Slack incoming-webhook payload; --dry-run never posts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from lib import OUT_DIR, ensure_out_dir, load_json, write_json


def build_payload(*, factors: list[str], run_url: str) -> dict[str, Any]:
    lines = ["*bmad-factory quality worsen*", f"Run: {run_url}", "Factors:"]
    for factor in factors:
        lines.append(f"• {factor}")
    text = "\n".join(lines)
    return {"text": text}


def collect_factors(worsen_paths: list[Path]) -> list[str]:
    factors: list[str] = []
    for path in worsen_paths:
        if not path.is_file():
            continue
        data = load_json(path)
        if not data.get("worsened"):
            continue
        tool = data.get("tool", path.stem)
        if tool == "semgrep":
            n = len(data.get("new_findings", []))
            factors.append(f"semgrep: {n} new finding(s) vs baseline")
        elif tool == "mutmut":
            factors.append(
                f"mutmut: score {data.get('baseline_score')} → {data.get('current_score')} "
                f"(drop {data.get('drop')} ≥ {data.get('threshold', 1)})"
            )
        else:
            factors.append(f"{tool}: worsened")
    return factors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--worsen",
        nargs="*",
        type=Path,
        default=[],
        help="Paths to worsen JSON files from Semgrep/mutmut helpers",
    )
    parser.add_argument(
        "--factor",
        action="append",
        default=[],
        help="Explicit factor string (repeatable); used with fixtures",
    )
    parser.add_argument(
        "--run-url",
        default="https://example.invalid/actions/runs/0",
        help="Workflow run URL (placeholder for dry-run)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write payload to stdout and .ci/out/slack-payload.json; do not POST",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUT_DIR / "slack-payload.json",
    )
    args = parser.parse_args(argv)
    ensure_out_dir()

    factors = list(args.factor)
    factors.extend(collect_factors(args.worsen))
    # de-dupe preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for f in factors:
        if f not in seen:
            seen.add(f)
            unique.append(f)

    if not unique:
        print("No worsen factors; skipping Slack payload")
        write_json(args.output, {"skipped": True, "reason": "no_factors"})
        return 0

    payload = build_payload(factors=unique, run_url=args.run_url)
    write_json(args.output, payload)
    rendered = json.dumps(payload, indent=2)
    print(rendered)
    if args.dry_run:
        print(f"[dry-run] wrote {args.output}; not posting to Slack")
        return 0

    # Live post is owned by slackapi/slack-github-action in workflows.
    # This script only prepares the payload file for that action.
    print(f"Wrote Slack payload for workflow action: {args.output}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
