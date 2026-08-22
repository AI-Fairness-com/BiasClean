# BiasClean — User Guide (Justice Domain)

This guide covers running BiasClean's Justice-domain pipeline (v3.10.10) as a non-technical user, on your own dataset, and reading the resulting report. It assumes no coding background.

## What this tool does

BiasClean audits a criminal-justice dataset (arrests, citations, recidivism, sentencing, etc.) for disparities in outcome rates across groups defined by protected attributes — Ethnicity, Gender, Age, Region — and, where the disparity is real and correctable, produces a rebalanced version of the dataset alongside a full record of what changed and why.

It does **not** decide whether a disparity is discrimination, does **not** certify legal compliance, and does **not** replace a human reviewer's judgment. See `LIMITATIONS_JUSTICE.md` for the full scope of what this tool is (and isn't) for.

## Running it

Two ways to run BiasClean, both equivalent:

### Option A — Docker (recommended, no local Python setup needed)

```bash
docker build -t biasclean:3.10.10 .
docker run -it \
  -v "/path/to/your/data:/app/Justice_Real Datasets" \
  -v "/path/to/your/output:/app/biasclean_results" \
  biasclean:3.10.10
```

See `docs/DOCKER_SETUP.md` for full setup details, including memory allocation guidance for large files.

### Option B — Native Python (venv)

```bash
source venv/bin/activate
python3 biasclean_v3_5_1_terminal.py
```

Both produce identical results — Docker is recommended because it avoids any local dependency setup entirely.

## Walking through a run

The pipeline asks you a short series of questions. For a first run, the safe default is almost always to just press Enter and accept the suggestion:

1. **Data source** — choose "Upload your own CSV file" and give the path.
2. **Target column** — press Enter to let auto-detection find the outcome column (e.g. `arrest_made`, `citation_issued`, `recidivism`). Only type a column name yourself if you know exactly which outcome you want audited and auto-detection might guess differently (e.g. a dataset with several plausible outcome columns).
3. **Auto-approval threshold** — press Enter for the default (80%). This controls how confident the pipeline must be before automatically using a column as a protected attribute.
4. **Domain** — choose Justice (option 1).
5. **Mode** — choose Legacy (option 2) for a straightforward audit-and-correct run. Audit-First runs a pre-mitigation safety check first; Audit-Only diagnoses without correcting anything.
6. **SVM fairness enforcement** — leave this at the default (N/disabled) unless you specifically want the additional model-level fairness step. It adds meaningful runtime and, for very large datasets, meaningful memory use.

## Reading the results

Every run produces three files in `biasclean_results/`:

- **`report.pdf`** — start here. A plain-language summary (bias score, what changed, why) followed by a technical detail section for anyone who wants the full statistics.
- **`corrected_dataset.csv`** — the rebalanced dataset, if any correction was applied.
- **`audit_trail.json`** — every number behind the report, in machine-readable form, for reproducibility or further analysis.
- **`run_<timestamp>.log`** — a full timestamped log of everything the pipeline did during that run, for troubleshooting.

The report's headline number is the **bias score** (0 = no gap, lower is better) shown before and after correction. A "Mapping ties detected" or "Fairness Regulator Flag" box, if present, is not an error — it's the pipeline telling you something worth a second look before you rely on the result. Read those boxes; they exist specifically so you don't have to dig through the technical detail to know when extra care is warranted.

## Getting help

For anything this guide doesn't cover, the technical detail section of `report.pdf` and `audit_trail.json` together contain the full picture of what the pipeline did. `docs/CHANGELOG.md` documents every version's behavior in detail.
