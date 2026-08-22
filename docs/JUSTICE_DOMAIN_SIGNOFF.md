# BiasClean — Justice Domain Sign-Off Checklist

**Purpose:** an explicit, closed definition of "done" for the Justice domain, so this phase does not become indefinite polishing. Every item below is either checked (with the evidence that justifies it) or explicitly listed as out of scope. Once all checked items are true, the Justice domain is considered **production-ready** under the scope defined in `LIMITATIONS_JUSTICE.md`.

## Correctness

- [x] Core bias detection and mitigation logic validated on 5 independent real-world datasets (UCI Communities & Crime, ProPublica COMPAS, Oklahoma City traffic stops, NIJ Recidivism Challenge, North Carolina statewide traffic stops), spanning 1,994 to 20,286,645 rows. *(Phase 1, Phase 2)*
- [x] Independently benchmarked, blind, against AIF360 (IBM Research), judged by Aequitas (University of Chicago), across all 5 datasets — BiasClean won 10/15 dataset-feature judgments, AIF360 4/15, 1 split. *(Phase 3)*
- [x] Overcorrection safeguards ("the Fairness Regulator") in place: proactive cap preventing rebalancing from overshooting past parity, reactive gate flagging any reversal that occurs anyway. *(Phase 1)*
- [x] Worst-group deviation tracked and reported alongside mean/composite disparity, so an improving average cannot silently hide a worsening outcome for the single most-affected group. *(Phase 3.5, Workstream C)*
- [x] Sample-size-aware statistical significance (log relative-risk confidence interval) reported alongside the existing composite threshold, guarding against both large-sample false positives and small-sample false negatives. *(Phase 3.5, Workstream B)*
- [x] 10 real bugs found, root-caused, fixed, and regression-tested across the project's history (5 in Phase 1/2, 3 in Phase 3, 2 in Phase 4/Workstream G).

## Engineering

- [x] All pipeline runtime dependencies pinned to exact versions, validated against a clean install with zero resolver errors. *(Phase 4, Workstream D)*
- [x] Reproducible containerized environment (Docker), validated against all 5 established datasets including the 20.3M-row North Carolina file. *(Phase 4, Workstream E)*
- [x] Structured, severity-filterable logging with a timestamped file record per run, replacing unstructured console output. *(Phase 4, Workstream F)*
- [x] Malformed-input audit completed; two real defects found and fixed (fully-null protected attribute columns, silent substitution on a missing target column), both validated against synthetic malformed inputs and real data with no regressions. *(Phase 4, Workstream G)*

## Documentation

- [x] Full changelog from v3.0 through v3.10.10, documenting every version's behavior, in `docs/CHANGELOG.md`.
- [x] Independent phase reports for Phase 1 (Consolidation & Regression Testing), Phase 2 (External Validation), Phase 3 (Benchmark vs. AIF360), and Phase 4 (Internal Production Hardening), in `/docs`.
- [x] Docker build/run instructions, including the North Carolina memory-tuning guidance, in `docs/DOCKER_SETUP.md`.
- [x] Methodology document (`BiasClean_Methodology.md`) covering the SIW-ESW-PLW weighting framework and its UK regulatory grounding.
- [x] User guide for non-technical operation (`USER_GUIDE_JUSTICE.md`, this phase).
- [x] Limitations note, positioning BiasClean as a screening tool rather than a compliance certification (`LIMITATIONS_JUSTICE.md`, this phase).
- [x] This sign-off checklist itself, as the explicit closure record for the Justice domain.

## Explicitly out of scope for this sign-off

These are real, acknowledged gaps — not oversights — and are intentionally excluded from "Justice domain done" so they don't quietly expand this phase's scope:

- Validation of the other 6 domains (Healthcare, Finance, Hiring, Education, Business, Governance) — scoped separately as **Phase 5**, pending real datasets for each (target: under 3GB per dataset, to keep SVM fairness enforcement practical without North Carolina-scale memory tuning).
- A non-interactive CLI mode for the Docker container — considered and deliberately deferred during Phase 4, Workstream E.
- Whether `dual_criteria_significant` (Phase 3.5) should ever inform `requires_mitigation`'s actual gating threshold, rather than remaining a reporting-only signal — left as an open, deliberate policy question, not a defect.
- Any legal compliance determination for any specific jurisdiction or use case — permanently out of scope for this tool, per `DISCLAIMER.md`.

## Sign-off

Justice domain: **v3.10.10**, considered production-ready under the scope above as of this checklist's date.
