# BiasClean — Finance Domain Sign-Off Checklist

**Purpose:** an explicit, closed definition of "done" for the Finance domain, so this phase
does not become indefinite polishing. Every item below is either checked (with the evidence
that justifies it) or explicitly listed as out of scope. Once all checked items are true, the
Finance domain is considered **production-ready** under the scope defined in
`LIMITATIONS_FINANCE.md`.

## Correctness

- [x] Core bias detection and mitigation logic validated on 2 independent real-world
  datasets (HMDA (Home Mortgage Disclosure Act public data, Washington State extract, 180,056 rows) and German Credit (UCI Statlog German Credit dataset, 1,000 rows)). *(Phase 5)*
- [x] **HMDA (Washington State, race cut)** — target `loan_approved`, 180,056 → 180,056 (100% retention; no rebalancing triggered). Bias score: 0.0179 (unchanged, below the 0.05 mitigation threshold). Features: Ethnicity (derived_race, 0.25 weight, significant), Gender (derived_sex, 0.05 weight, significant). SVM stage: Not applied — composite stayed below the mitigation threshold. Confirmed matching in both native venv and Docker.
- [x] **German Credit (Statlog)** — target `CreditRisk`, 1,000 → 1,000 (100% retention). Bias score: 0.0505 → 0.0158 (+69% improvement). Features: SocioeconomicStatus (Property, 81% confidence, significant), Gender (significant), Age (bucketed, significant). SVM stage: Applied — zero fuse exclusions needed, rebalance gate accepted. Confirmed matching in both native venv and Docker.
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
- [x] CamelCase/PascalCase column-name tokenization (v3.10.2) — found on German Credit, where column names like AgeInYears and ForeignWorker mapped to nothing at all because the pipeline had no word-boundary logic for unseparated case transitions.
- [x] SES keyword coverage + p-value-based column selection (v3.10.3→v3.10.4) — found on German Credit, where the pipeline was only recognizing a loan-structuring ratio as SocioeconomicStatus while the dataset's genuine wealth columns (Property, Savings, Housing, Employment, Job) went unrecognized.
- [x] Continuous protected-attribute bucketing (v3.10.5) — benefits German Credit's Age column, cleanly bucketed into 4 quantile groups instead of raw per-year values.
- [x] features-key omission (v3.10.8) — found via HMDA re-validation; silently broke mapping-tie winner-naming and p-value transparency in every report since v3.10.4. Fixed.

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
- [x] User guide for non-technical operation (`USER_GUIDE_FINANCE.md`, this phase).
- [x] Limitations note, positioning BiasClean as a screening tool rather than a compliance
  certification (`LIMITATIONS_FINANCE.md`, this phase).
- [x] This sign-off checklist itself, as the explicit closure record for the Finance domain.

## Explicitly out of scope for this sign-off

These are real, acknowledged gaps — not oversights — and are intentionally excluded from
"Finance domain done" so they don't quietly expand this phase's scope:

- Validation of any dataset materially different from the one(s) listed above — see
  `LIMITATIONS_FINANCE.md` for specifics.
- A non-interactive CLI mode for the Docker container — considered and deliberately deferred
  during Phase 4, Workstream E (shared pipeline-wide decision).
- Whether `dual_criteria_significant` should ever inform `requires_mitigation`'s actual gating
  threshold, rather than remaining a reporting-only signal — left as an open, deliberate policy
  question, not a defect (shared pipeline-wide).
- Any legal compliance determination for any specific jurisdiction or use case — permanently out
  of scope for this tool, per `DISCLAIMER.md`.

## Sign-off

Finance domain: **v3.10.10**, considered production-ready under the scope above
as of this checklist's date.
