# ADR: Method floor passes on any one in-floor initiative

**Context:** Story-2 `validate` must fail closed with `method-floor` when the target is structurally below the BMAD ≥ 6.13-next ticket-tree floor, without a live Store client. Multi-initiative roots can mix valid and broken `initiative-*` directories.

**Decision:** Structural Method floor succeeds when **at least one** top-level `initiative-<slug>/` meets the floor (initiative md + `tickets/tickets.toml` with non-empty valid `[[epic]]` and matching epic dirs). Broken sibling initiatives do not fail validate.

**Why:** Recorded in story-2 plan Design Notes (`story-validate-rejects-sprint-modes-and-below-method-floor-plan.md`): “one valid initiative suffices,” with fixture coverage for `in-floor-with-broken`. Trade-off favors a usable preflight for mixed trees over requiring every initiative to pass. Landed in product commit `71c43ce` (`feat: validate rejects sprint modes and below method floor`).
