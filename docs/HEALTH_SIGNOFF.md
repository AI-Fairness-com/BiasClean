# BiasClean — Health Domain Sign-Off Checklist

**Purpose:** an explicit, closed definition of "done" for the Health domain, so this phase
does not become indefinite polishing. Every item below is either checked (with the evidence
that justifies it) or explicitly listed as out of scope. Once all checked items are true, the
Health domain is considered **production-ready** under the scope defined in
`LIMITATIONS_HEALTH.md`.

## Correctness

- [x] Core bias detection and mitigation logic validated on 2 independent real-world
  datasets (UCI Diabetes 130-US Hospitals (99,492 rows) and the UCI Cleveland Heart Disease dataset (303 rows)). *(Phase 5)*
- [x] **Diabetes 130-US Hospitals** — target `readmitted_30d`, 99,492 → 99,492 (100% retention; no rebalancing triggered). Bias score: 0.0163 (unchanged — both features genuinely non-significant). Features: Ethnicity (p=0.180, not significant), Gender (p=0.349, not significant). SVM stage: Not applied — no significant bias found, nothing to mitigate. Confirmed matching in both native venv and Docker.
- [x] **Heart Disease (UCI Cleveland)** — target `heart_disease (binarized from the original 5-category target column)`, 303 → 303 (100% retention). Bias score: 0.0852 → 0.0301 (+65% improvement). Features: Gender (p=1.26e-06, significant, 97.7% improvement after rebalancing), Age (p=1.86e-05, significant, bucketed into 4 ranges, excluded from rebalancing by the fairness fuse). SVM stage: Applied, REJECTED (plain composite-score regression 0.0301→0.0345 — no collapse, no new reversal; rebalanced stage used as final result). Confirmed matching in both native venv and Docker.
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
- [x] Continuous protected-attribute bucketing (v3.10.5) — Age on Heart Disease bucketed into 4 clean ranges (min group size 70) instead of raw per-year values.
- [x] Rebalance-stage fuse (v3.10.5) — third real-data cross-domain confirmation on Heart Disease, correctly excluding Age's reversed rebalancing.
- [x] Report-narrative rounding fix (v3.10.10) — found on Heart Disease; the 'Why this recommendation' text was always showing the SVM-rejected score as unchanged ('from 0.030 to 0.030') regardless of true magnitude. Now correctly shows the real value ('from 0.030 to 0.034').

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
- [x] User guide for non-technical operation (`USER_GUIDE_HEALTH.md`, this phase).
- [x] Limitations note, positioning BiasClean as a screening tool rather than a compliance
  certification (`LIMITATIONS_HEALTH.md`, this phase).
- [x] This sign-off checklist itself, as the explicit closure record for the Health domain.

## Explicitly out of scope for this sign-off

These are real, acknowledged gaps — not oversights — and are intentionally excluded from
"Health domain done" so they don't quietly expand this phase's scope:

- Validation of any dataset materially different from the one(s) listed above — see
  `LIMITATIONS_HEALTH.md` for specifics.
- A non-interactive CLI mode for the Docker container — considered and deliberately deferred
  during Phase 4, Workstream E (shared pipeline-wide decision).
- Whether `dual_criteria_significant` should ever inform `requires_mitigation`'s actual gating
  threshold, rather than remaining a reporting-only signal — left as an open, deliberate policy
  question, not a defect (shared pipeline-wide).
- Any legal compliance determination for any specific jurisdiction or use case — permanently out
  of scope for this tool, per `DISCLAIMER.md`.

## Sign-off

Health domain: **v3.10.10**, considered production-ready under the scope above
as of this checklist's date.
