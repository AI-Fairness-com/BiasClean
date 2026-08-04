# BiasClean — Limitations Note (Education Domain)

**One-page scope statement, to be read alongside `DISCLAIMER.md`.**

## What BiasClean's Education-domain pipeline is

A screening tool. It flags statistically measurable disparities in outcome rates between
groups in an education dataset, and offers one specific, transparent, auditable way of
narrowing them (weight-prioritized rebalancing, with an optional additional SVM
fairness-enforcement stage). Every number it produces is reproducible and inspectable in
`audit_trail.json`.

This domain's protected-attribute ontology currently recognizes:

- SocioeconomicStatus (weighted highest in this domain, 0.25)
- Ethnicity
- Gender
- Age
- Region
- DisabilityStatus

## What it is not

- **Not a legal compliance certification.** A "GREEN" traffic light, a positive bias-score
  improvement, or a clean report does not mean a dataset or a model trained on it complies with
  the Equality Act 2010, US anti-discrimination law, GDPR, the EU AI Act, or any other
  regulation. BiasClean does not adjudicate discrimination claims.
- **Not a substitute for domain expertise.** Every reversal, near-parity finding, or flagged
  concern in a report is a statistical observation, not a verdict. This project's own working
  principle applies here as much as anywhere: *"Is the disparity real and meaningful? Does it
  reflect a legitimate pattern or bias? Can you explain the change to affected communities? Have
  you documented your reasoning?"* — BiasClean surfaces the first question's evidence; it cannot
  answer the other three.
- **Not validated beyond what's been tested.** The Education-domain pipeline has been
  validated against real, publicly sourced data:
  - **Bar Pass Prediction (LSAC)** — target column `pass_bar`, 22,407 → 22,407 rows
  - **studentInfo (OULAD)** — target column `completed (binarized from final_result via Pass/Distinction)`, 32,593 → 32,614 rows
  Results on a dataset with materially different characteristics — a different outcome type, a
  different set of protected attributes, extreme class imbalance beyond what's been seen, or
  data quality issues not resembling either validation dataset — have not been specifically
  tested and should be reviewed with proportionally more scrutiny.
- **Not a claim about causation.** A statistical association between a protected attribute and
  an outcome, however significant, is not itself evidence of *why* that association exists.
  BiasClean measures the gap; it does not explain its origin.

## What a "no significant bias found" or fully-corrected result means, specifically

It means: given the protected attributes BiasClean was able to map with sufficient confidence
and sample size, the measured statistical gap in outcome rate either did not clear this domain's
significance threshold, or was narrowed by rebalancing to within that threshold. It does not
mean the dataset or downstream model is fair in any broader sense, nor that no disparity exists
on a dimension the pipeline didn't measure (an unmapped column, an intersectional effect across
two protected attributes at once, or a protected attribute not present in the dataset at all).

## Known operating constraints (Education domain, as of v3.10.10)

- Bar Pass's raw 'age' column (the losing candidate in its Age mapping tie) buckets into non-sensical negative ranges — likely a derived/normalized variable, not literal age. It does not affect the delivered result but is worth a manual look if you ever need that specific column.
- Only two datasets have been validated for this domain (bar exam outcomes and university course completion). Other Education use cases — school admissions, financial aid allocation, standardized test scoring — have not been specifically tested.
- SVM fairness enforcement (fair_reduction / ExponentiatedGradient) has an inherent, unseeded
  stochastic training step at the library level; the pipeline's own validation gate
  independently accepts or rejects each SVM-stage result before it can become the delivered
  output, so a non-deterministic training run cannot silently degrade the final result — but
  minor run-to-run variance in the *accepted* case remains architecturally possible.
- Auto-detection of the target/outcome column has been removed pipeline-wide as of v3.10.1; the
  target column must now be specified explicitly.

For the underlying legal and ethical framing this note sits inside, see `DISCLAIMER.md`.
