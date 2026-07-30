# BiasClean™ Methodology: Safety, Security, and Evidence Base

**AI Fairness CIO — Hamid Tavakoli**
**Version documented: 3.6.9 · July 2026**

---

## Purpose

This document explains how BiasClean™ is designed to protect the people whose lives, jobs, income, liberty, and access to services may be shaped by decisions a dataset audited or de-biased with BiasClean goes on to inform. It is written for anyone who needs to trust that judgment before relying on it — deployers, auditors, affected communities, and regulators — not just engineers.

Every mechanism described below is illustrated with a real example from BiasClean's own consolidation and regression-testing history (Phase 1) or its external validation against six real datasets (Phase 2), not a hypothetical. Where a limitation exists, it is stated plainly rather than omitted — a safety document that only lists what works is not one a careful reader should trust.

---

## The Two-Layer Safety Design: Thermostats and Fuses

BiasClean's mitigation safeguards follow one deliberate design principle, introduced in v3.4.0 and used as the organizing frame for this whole document:

> A **thermostat** is proactive — it continuously regulates a correction *before* it can go wrong, the same way a thermostat cuts the heat the instant a room reaches its setpoint rather than overshooting into overheating.
>
> A **fuse** is reactive — a last-resort check that trips and halts when something the thermostat couldn't see gets through anyway, flagging it for human review rather than either hiding it or guessing at a fix.

Neither layer cares which group ends up disadvantaged. Both trigger on the problem itself — bias is bias regardless of who it currently favors — and both are designed to fail toward caution: when in doubt, BiasClean flags for manual review rather than silently deciding on the user's behalf.

---

## The Thermostats (Proactive Safeguards)

### Overcorrection prevention
Every automatic rebalancing correction is capped at the point where it reaches parity — it is mathematically prevented from continuing past that point into reversing which group is disadvantaged. **Real example:** on real COMPAS data, rebalancing without this cap flipped the Age feature's disadvantaged group from the oldest bracket to the youngest — the correction had overshot past the target it was aiming for. This is the exact finding that led to the cap being built.

### Minimum group-size floor
No group with fewer than 50 samples is automatically rebalanced — it is excluded and flagged for manual review instead, regardless of how disparate its rate looks. Statistical corrections computed on a handful of data points are not reliable, and BiasClean does not treat them as if they were. **Real example:** in Phase 2's validation against UCI Communities and Crime, 31 of 35 state-level groups (89%) fell below this floor and were correctly excluded rather than corrected on unreliable evidence.

### Cardinality guard on protected-feature selection
A column with as many distinct values as it has rows — a free-text location field, a raw identifier — is not a real category, and cannot be treated as one no matter how confidently its name matches a keyword pattern. BiasClean now rejects such columns before they can be selected as a protected feature. **Real example:** found in Phase 2 when a `location` field with 204,447 near-unique values across 945,107 real traffic-stop records was initially selected over a genuinely categorical column, corrupting the result and causing a multi-hour computation on statistically meaningless groups.

### Target-coverage guard
A column is not accepted as a valid outcome to measure bias against unless both of its categories are backed by real data (minimum 50 samples each) — a column with almost no data behind it is rejected rather than silently scored as if it meant something. **Real example:** found in Phase 2 on an undocumented dataset where a column with only 2 real values out of 66,662 rows had been accepted as a target, producing a report that looked complete while measuring nothing.

### Statistical, name-independent leakage detection
Rather than relying only on a list of known-risky column names, BiasClean directly checks whether any remaining column predicts the outcome with near-perfect purity (98%+) using its value alone — a strong signal that the column is a hidden encoding of the target itself, not a genuine predictor. **Real example:** this is what caught a North Carolina traffic-stop dataset where three columns turned out to be alternate encodings of the same decision as the target, none of which matched any name-based rule tuned on prior datasets.

---

## The Fuses (Reactive Safeguards)

### The rebalancing gate
Even with the thermostat's cap in place, a reversal can still occur through interaction effects the cap alone cannot see — for example, one feature's correction reshuffling the rows underlying another feature that was already corrected. When this happens, BiasClean does not auto-revert it (undoing one feature's specific row changes after several features have already been rebalanced with overlapping rows is not a safe, reversible operation) — it flags it explicitly for manual review. **Real example:** in Phase 2, North Carolina's rebalancing stage triggered exactly this gate for three of four protected features, including a reversal implicating the state's second-most-populous county — flagged, not hidden, and not silently trusted.

### The SVM validation gate
Before any machine-learning-based fairness enforcement result is accepted, its outcome is checked against the same metrics a human reviewer would use: does it make the composite bias score worse than the simpler correction that came before it, or does it introduce a new group reversal that wasn't already present? If either is true, the result is rejected outright and BiasClean falls back to the safer, simpler correction. **Real example:** this gate rejected the SVM-stage result on real COMPAS data — twice, independently, across two separate validation rounds — for introducing new reversals in Gender and Ethnicity that were not present after simple rebalancing.

### Degenerate-classifier detection
If the machine-learning model collapses to predicting the same outcome for every single row — a real failure mode observed directly in this codebase's own testing — it is rejected regardless of what its score otherwise appears to say, since a classifier with no discriminative power cannot meaningfully assess fairness.

---

## The Evidence-Based Weighting Framework

BiasClean assigns different weight to different protected characteristics within each domain, reflecting that not every form of disadvantage carries equal structural weight in every context. This is not an arbitrary or purely statistical choice — it follows a documented, three-part evaluative framework:

- **Structural Inequality Weight (SIW)** — the degree of systemic impact a characteristic has within a domain
- **Evidence Strength Weight (ESW)** — the consistency and robustness of the national data supporting that impact
- **Policy & Legal Relevance Weight (PLW)** — alignment with equality legislation and regulatory priorities

Each of the seven fairness features below was scored against all three criteria and normalized so every domain's weights sum to 1.00:

| Feature | What it captures |
|---|---|
| Region | Postcode-linked opportunity and service inequality |
| Ethnicity | The strongest structural disparity across multiple domains |
| Age | Behavioural gradients affecting outcomes |
| Gender | Documented bias across hiring, health, and leadership |
| DisabilityStatus | A protected characteristic with consistent disadvantage |
| SocioeconomicStatus (SES) | A key driver of multi-domain deprivation |
| MigrationStatus | Affects service access, representation, and civic participation |

**Justice domain weights** (the domain validated in Phase 2): Ethnicity 0.25, SocioeconomicStatus 0.20, Region 0.15, Age 0.15, MigrationStatus 0.10, DisabilityStatus 0.10, Gender 0.05.

### ⚠️ This weighting is UK-specific — read this before applying it elsewhere

The evidence base behind these weights — ONS Census and labour market statistics, Ministry of Justice race and criminal justice system reports, NHS/MHRA/Public Health England disparity data, FCA and Bank of England lending fairness studies, Department for Education and Sutton Trust analyses, BEIS and British Business Bank inequality reports, Electoral Commission civic engagement data, and EHRC statutory guidance — reflects **United Kingdom** structural inequality patterns, and the Policy & Legal Relevance criterion is scored against the **Equality Act 2010** specifically.

This matters concretely: five of the six real datasets used in Phase 2's validation were US-sourced. Applying UK-derived weights to them means the *relative prioritization* across features — Ethnicity weighted more than four times as heavily as Gender for Justice, for instance — reflects UK evidence, not necessarily the evidence base or legal framework of the jurisdiction the data was actually drawn from.

**What this does and does not affect:** every safeguard described above — the caps, the floors, the gates, the leakage detection — operates on the *statistical relationship* between a protected feature and an outcome, independent of that feature's assigned weight. None of them are weakened by using UK-derived weights on non-UK data. What *is* affected is the **composite bias score** and any claim about which feature matters most in a given domain — those should be read as a considered UK default, not an evidence-matched assessment for every jurisdiction. Organizations deploying BiasClean outside the UK should treat the weighting as a reasonable, transparent starting point, and are encouraged to commission an equivalent evidence review for their own jurisdiction rather than assume the UK ordering transfers directly.

---

## Methodological Foundations

BiasClean's core bias-mitigation mechanisms are not novel inventions — they implement, and are gated by validation against, established, peer-reviewed methods from the algorithmic fairness literature:

**Reweighing** (BiasClean's default rebalancing method, in use across every dataset validated in Phase 2) computes a per-group correction ratio that mathematically targets exact convergence to the population mean, from:
> Kamiran, F., & Calders, T. (2012). Data preprocessing techniques for classification without discrimination. *Knowledge and Information Systems*, 33(1), 1–33. https://doi.org/10.1007/s10115-011-0463-8

**SVM fairness enforcement** wraps a classifier in an in-processing method that optimizes accuracy subject to an explicit fairness constraint, rather than optimizing for accuracy alone, from:
> Agarwal, A., Beygelzimer, A., Dudík, M., Langford, J., & Wallach, H. (2018). A reductions approach to fair classification. *Proceedings of the 35th International Conference on Machine Learning*, PMLR 80, 60–69. https://arxiv.org/abs/1803.02453

The default fairness constraint used, **equalized odds**, is defined in:
> Hardt, M., Price, E., & Srebro, N. (2016). Equality of opportunity in supervised learning. *Advances in Neural Information Processing Systems*, 29, 3323–3331. https://arxiv.org/abs/1610.02413

The domain weighting framework's legal grounding is:
> Equality Act 2010 (c. 15), United Kingdom. https://www.legislation.gov.uk/ukpga/2010/15/contents

Both mitigation algorithms are implemented via [Fairlearn](https://fairlearn.org), an open-source toolkit maintained for exactly this purpose.

---

## Validated Track Record

BiasClean's mechanisms are not asserted correct — they are tested against real data and revised when real data finds a gap. This document does not repeat those findings in full; see:

- ***BiasClean Justice Domain — Phase 1: Consolidation & Regression Testing*** — the record of 15 releases (v3.0.0 → v3.6.1), each driven by a specific, root-caused finding, almost all surfaced on real data rather than synthetic test cases alone.
- ***BiasClean External Validation in Justice Domain*** (Phase 2) — external validation against six real datasets under a strict non-technical-user policy (every run used the pipeline's own defaults, nothing was hand-configured to produce a better-looking result), which itself found and fixed three further defects before any dataset's result was accepted as valid.

Across both documents, the pattern is consistent: safeguards exist because a real defect was found, not in anticipation of one, and every fix was verified against the same real data that surfaced the problem before being considered resolved.

---

## Known Limitations

A confidence document that omits its own limitations is not trustworthy. These are current, open, and not hidden:

- **Same-pattern column ties still resolve by file order.** When multiple columns matching the *identical* keyword pattern at *identical* confidence and *identical* validation quality are candidates for the same role, selection falls back to whichever appears first in the file — a documented last resort, not eliminated. Confirmed still open during Phase 2's validation (NIJ's four `Recidivism_*` columns; three genuinely distinct disability sub-type columns collapsed into one `DisabilityStatus` slot, since the weighting framework allocates only one).
- **The weighting framework is UK-specific**, as detailed above — this is a known, stated design choice, not an oversight, but users applying it to other jurisdictions should understand what that means for their results.
- **SVM enforcement has less real-data coverage than rebalancing.** Across Phase 2's five validated datasets, SVM enforcement was meaningfully exercised in only two (rejected on COMPAS, accepted on Communities and Crime) — the other three either skipped it by necessity at scale or never triggered it. This mechanism's real-world behavior is less thoroughly tested than the rebalancing path.
- **BiasClean cannot validate a dataset it cannot understand.** When a dataset arrives with undocumented, cryptic column encodings and no data dictionary, BiasClean's honest behavior is to fail loudly or map almost nothing — and it now does so correctly — but this is a limit on what any tool can respons­ibly claim about data whose meaning is unknown, not something more automation can solve.
- **This document, and the two it summarizes, cover the Justice domain only.** The same weighting framework and mitigation mechanisms apply to BiasClean's other six domains (Healthcare, Finance, Education, Hiring, Business, Governance), but the depth of real-data validation described here has not yet been repeated for each of them.

---

## References

1. Kamiran, F., & Calders, T. (2012). Data preprocessing techniques for classification without discrimination. *Knowledge and Information Systems*, 33(1), 1–33. https://doi.org/10.1007/s10115-011-0463-8
2. Agarwal, A., Beygelzimer, A., Dudík, M., Langford, J., & Wallach, H. (2018). A reductions approach to fair classification. *ICML 2018*, PMLR 80, 60–69. https://arxiv.org/abs/1803.02453
3. Hardt, M., Price, E., & Srebro, N. (2016). Equality of opportunity in supervised learning. *NeurIPS 2016*, 29, 3323–3331. https://arxiv.org/abs/1610.02413
4. Equality Act 2010 (c. 15), United Kingdom. https://www.legislation.gov.uk/ukpga/2010/15/contents
5. Fairlearn (open-source toolkit). https://fairlearn.org
6. Office for National Statistics — Census, Index of Multiple Deprivation, and labour market statistics. https://www.ons.gov.uk
7. Ministry of Justice — Race and the Criminal Justice System reports; Sentencing Council analyses. https://www.gov.uk/government/organisations/ministry-of-justice
8. NHS England, Medicines and Healthcare products Regulatory Agency (MHRA), and Public Health England — health disparity datasets. https://www.england.nhs.uk
9. Financial Conduct Authority and Bank of England — lending fairness studies. https://www.fca.org.uk
10. Department for Education, Sutton Trust, and Education Policy Institute analyses. https://www.gov.uk/government/organisations/department-for-education
11. Department for Business, Energy & Industrial Strategy (BEIS) and British Business Bank — business and investment inequality reports.
12. Electoral Commission and House of Commons Library — civic engagement data. https://www.electoralcommission.org.uk
13. Equality and Human Rights Commission (EHRC) — statutory guidance and systemic inequality reviews. https://www.equalityhumanrights.com
14. *BiasClean v2.0 — Evidence Base & Methodology Appendix (UK Edition)* (Tavakoli, internal, 2026) — primary source for the weighting framework described above.
15. Tavakoli, H. (2026). *The AI Fairness Diagnostic Kit: From Principle to Practice in No-Code AI Fairness Auditing.* Apress/Springer Nature.
