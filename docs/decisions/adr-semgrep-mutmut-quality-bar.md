# ADR: Semgrep + mutmut as the product quality bar

**Context:** Epic `epic-cli-contract` Done when #4 and AGENTS.md required AST-diff analysis, mutation testing with SARIF, owner notify on worsen, and Hypothesis when earned, without naming tools in the architecture spine.

**Decision:** Use Semgrep (diff-aware) for AST-diff findings and mutmut for mutation testing; publish both as SARIF from product-repo CI; compare against in-repo baselines under `.ci/baselines/`; notify the repository owner via Slack incoming-webhook on worsen; keep Hypothesis as a declared test dependency and add property-based tests only when earned (envelope invariants shipped first).

**Why:** Recorded in story-6 plan Design Notes / Intent (`story-ci-ast-diff-mutation-sarif-hypothesis-plan.md`): mature standalone tools, no earn-green dependency, PR mutmut as SARIF signal with schedule owning mutation-score baseline + Slack, Semgrep worsen on PR/push. Landed in product commit `2463da1` (`feat(ci): wire Semgrep mutmut SARIF and Hypothesis quality bar`).
