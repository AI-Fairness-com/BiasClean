# BiasClean — Business Domain Sign-Off Checklist

**Purpose:** an explicit, closed definition of "done" for the Business domain, so this phase
does not become indefinite polishing. Every item below is either checked (with the evidence
that justifies it) or explicitly listed as out of scope. Once all checked items are true, the
Business domain is considered **production-ready** under the scope defined in
`LIMITATIONS_BUSINESS.md`.

## Correctness

- [x] Core bias detection and mitigation logic validated on 1 independent real-world
  dataset (the UCI Bank Marketing dataset (bank-full.csv, 45,211 rows)). *(Phase 5)*
- [x] **Bank Marketing (bank-full)** — target `y`, 45,211 → 45,211 (100% retention). Bias score: 0.0169 (1 significant feature, Age; below the 0.05 mitigation threshold, no rebalancing attempted). Features: Age (p=5.13e-36, significant, bucketed into 4 groups, min group size 10,279). SVM stage: Not applicable in the current validated result — composite stays below threshold. Confirmed matching in both native venv and Docker.
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
- [x] Delimiter auto-detection (v3.10.1) — found on this exact dataset (semicolon-delimited), which was silently loading as one giant single-column string field before the fix.
- [x] Continuous protected-attribute bucketing (v3.10.5) — directly resolved this dataset's Age-rebalancing regression, the clearest real-data example of the open item this fix was built to close.

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
- [x] User guide for non-technical operation (`USER_GUIDE_BUSINESS.md`, this phase).
- [x] Limitations note, positioning BiasClean as a screening tool rather than a compliance
  certification (`LIMITATIONS_BUSINESS.md`, this phase).
- [x] This sign-off checklist itself, as the explicit closure record for the Business domain.

## Explicitly out of scope for this sign-off

These are real, acknowledged gaps — not oversights — and are intentionally excluded from
"Business domain done" so they don't quietly expand this phase's scope:

- Validation of any dataset materially different from the one(s) listed above — see
  `LIMITATIONS_BUSINESS.md` for specifics.
- A non-interactive CLI mode for the Docker container — considered and deliberately deferred
  during Phase 4, Workstream E (shared pipeline-wide decision).
- Whether `dual_criteria_significant` should ever inform `requires_mitigation`'s actual gating
  threshold, rather than remaining a reporting-only signal — left as an open, deliberate policy
  question, not a defect (shared pipeline-wide).
- Any legal compliance determination for any specific jurisdiction or use case — permanently out
  of scope for this tool, per `DISCLAIMER.md`.

## Sign-off

Business domain: **v3.10.10**, considered production-ready under the scope above
as of this checklist's date.
