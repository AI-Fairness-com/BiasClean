# BiasClean — Limitations Note (Justice Domain)

**One-page scope statement, to be read alongside `DISCLAIMER.md`.**

## What BiasClean's Justice-domain pipeline is

A screening tool. It flags statistically measurable disparities in outcome rates between groups in a criminal-justice dataset, and offers one specific, transparent, auditable way of narrowing them (weight-prioritized rebalancing, with an optional additional SVM fairness-enforcement stage). Every number it produces is reproducible and inspectable in `audit_trail.json`.

## What it is not

- **Not a legal compliance certification.** A "GREEN" traffic light, a positive bias-score improvement, or a clean report does not mean a dataset or a model trained on it complies with the Equality Act 2010, US anti-discrimination law, GDPR, the EU AI Act, or any other regulation. BiasClean does not adjudicate discrimination claims.
- **Not a substitute for domain expertise.** Every reversal, near-parity finding, or flagged concern in a report is a statistical observation, not a verdict. This project's own working principle, unchanged since Phase 1, applies here as much as anywhere: *"Is the disparity real and meaningful? Does it reflect a legitimate pattern or bias? Can you explain the change to affected communities? Have you documented your reasoning?"* — BiasClean surfaces the first question's evidence; it cannot answer the other three.
- **Not validated beyond what's been tested.** The Justice-domain pipeline has been validated against five real-world datasets (UCI Communities & Crime, ProPublica COMPAS, Oklahoma City traffic stops, the NIJ Recidivism Challenge, North Carolina statewide traffic stops) spanning 1,994 to 20,286,645 rows. Results on a dataset with materially different characteristics — a different outcome type, a different set of protected attributes, extreme class imbalance beyond what's been seen, or data quality issues not resembling any of the five validation datasets — have not been specifically tested and should be reviewed with proportionally more scrutiny.
- **Not a claim about causation.** A statistical association between a protected attribute and an outcome, however significant, is not itself evidence of *why* that association exists. BiasClean measures the gap; it does not explain its origin.

## What a "no significant bias found" or fully-corrected result means, specifically

It means: given the protected attributes BiasClean was able to map with sufficient confidence and sample size, the measured statistical gap in outcome rate either did not clear this domain's significance threshold, or was narrowed by rebalancing to within that threshold. It does not mean the dataset or downstream model is fair in any broader sense, nor that no disparity exists on a dimension the pipeline didn't measure (an unmapped column, an intersectional effect across two protected attributes at once, or a protected attribute not present in the dataset at all).

## Known operating constraints (Justice domain, as of v3.10.10)

- SVM fairness enforcement must remain disabled for very large datasets (North Carolina's 20.3M rows, specifically) on machines with less than approximately 32GB of available memory — a hardware constraint, not a correctness one.
- Auto-detection of the target/outcome column can be ambiguous when several columns plausibly represent the same underlying outcome (e.g. multiple recidivism-window definitions); the pipeline surfaces this ambiguity but resolves it by column order, not by domain judgment — reviewing the mapping confirmation step is worthwhile when this occurs.

For the underlying legal and ethical framing this note sits inside, see `DISCLAIMER.md`.
