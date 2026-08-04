# BiasClean — Governance Domain Sign-Off Checklist

**Purpose:** an explicit, closed definition of "done" for the Governance domain, so this phase
does not become indefinite polishing. Every item below is either checked (with the evidence
that justifies it) or explicitly listed as out of scope. Once all checked items are true, the
Governance domain is considered **production-ready** under the scope defined in
`LIMITATIONS_GOVERNANCE.md`.

## Correctness

- [x] Core bias detection and mitigation logic validated on 1 independent real-world
  dataset (Folktables ACS Public Coverage, Washington State 2018 (24,312 rows) — real US Census ACS PUMS data). *(Phase 5)*
- [x] **ACS Public Coverage (Washington, 2018)** — target `PUBCOV`, 24,312 → 24,377 (100.3% retention). Bias score: 0.2036 → 0.1310 (+35.7% improvement) — the single most consequential result in Phase 5. Features: Ethnicity (race, excluded from rebalancing by the fuse, reverted), Gender (sex, significant, 7.8pp→6.0pp), SocioeconomicStatus (income, quantile-bucketed, 23.8pp→6.1pp), DisabilityStatus (43.8pp→2.7pp), MigrationStatus (citizenship, 14.3pp→8.8pp), Age (excluded from rebalancing by the fuse, reverted). SVM stage: Applied, REJECTED — classifier collapsed to a single constant prediction across all rows and introduced 5 new disadvantaged-group reversals; final predictions correctly fell back to the rebalanced stage. Confirmed matching in both native venv and Docker.
- [x] Overcorrection safeguards (the fairness regulator / rebalance-stage fuse) confirmed
  operating correctly wherever this domain's data exercised it — any feature whose rebalancing
  would reverse the disadvantaged group is excluded and reverted, not silently delivered.
  *(v3.10.5, cross-domain fix)*
- [x] Sample-size-aware statistical significance (dual-criteria: p-value plus practical
  significance) reported alongside the composite threshold for every mapped feature.
- [x] Both a native-environment and a packaged-Docker validation pass completed for every
  dataset above, confirmed matching (or with any divergence root-caused and explained).
  *(v3.10.10 full re-validation sweep)*
- [x] Real bugs found during this domain's validation, root-caused, fixed, and re-confirmed
  against real data:
- [x] Rebalance-stage fuse (v3.10.5) — found on this exact dataset; the disadvantaged group reversed for Ethnicity, Age, and SocioeconomicStatus after rebalancing, and the pre-fix pipeline delivered the reversed result as final despite flagging it. Now excluded and reverted automatically.
- [x] Continuous protected-attribute bucketing (v3.10.5) — found on this dataset; income as 859 raw near-continuous values produced an illegible chart and a nonsensical single-row 'disadvantaged group' after SVM. Now cleanly bucketed.
- [x] 'Why this recommendation' wording gap (item 9, closed v3.10.6) — no longer cites rejected SVM-stage reversals as though they applied to the delivered result.
- [x] Collateral-drift post-hoc check (item 10, closed v3.10.6) — catches fuse-excluded features that drift as a side effect of other features' resampling.
- [x] composite_bias_score / worst_case_subgroup_performance conflation and an all-or-nothing small-subgroup exclusion defect were also found and fixed during this domain's FDK-side review, applying the same soft-exclusion policy used elsewhere.

## Engineering

- [x] All pipeline runtime dependencies pinned to exact versions, validated against a clean
  install with zero resolver errors. *(shared pipeline infrastructure)*
- [x] Reproducible containerized environment (Docker), validated against this domain's dataset(s)
  above.
- [x] Structured, severity-filterable logging with a timestamped file record per run.
- [x] Malformed-input safeguards (fully-null protected-attribute columns, silent substitution on
  a missing target column) validated pipeline-wide, applicable to this domain.

## Documentation

- [x] Full changelog from v3.0 through v3.10.10, documenting every version's
  behavior, in `docs/CHANGELOG.md`.
- [x] `BiasClean_Phase5_Six_Domain_Validation_Report.docx` — this domain's full per-dataset
  results, findings, and caveats, in the shared Phase 5 report.
- [x] Methodology document (`BiasClean_Methodology.md`) covering the SIW-ESW-PLW weighting
  framework and its UK regulatory grounding, applicable to this domain's own weight table.
- [x] User guide for non-technical operation (`USER_GUIDE_GOVERNANCE.md`, this phase).
- [x] Limitations note, positioning BiasClean as a screening tool rather than a compliance
  certification (`LIMITATIONS_GOVERNANCE.md`, this phase).
- [x] This sign-off checklist itself, as the explicit closure record for the Governance domain.

## Explicitly out of scope for this sign-off

These are real, acknowledged gaps — not oversights — and are intentionally excluded from
"Governance domain done" so they don't quietly expand this phase's scope:

- Validation of any dataset materially different from the one(s) listed above — see
  `LIMITATIONS_GOVERNANCE.md` for specifics.
- A non-interactive CLI mode for the Docker container — considered and deliberately deferred
  during Phase 4, Workstream E (shared pipeline-wide decision).
- Whether `dual_criteria_significant` should ever inform `requires_mitigation`'s actual gating
  threshold, rather than remaining a reporting-only signal — left as an open, deliberate policy
  question, not a defect (shared pipeline-wide).
- Any legal compliance determination for any specific jurisdiction or use case — permanently out
  of scope for this tool, per `DISCLAIMER.md`.

## Sign-off

Governance domain: **v3.10.10**, considered production-ready under the scope above
as of this checklist's date.
