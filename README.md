# 🧹 BiasClean Toolkit v3.10.10

[![GitHub Repository](https://img.shields.io/badge/GitHub-AI--Fairness--com%2FBiasClean-blue)](https://github.com/AI-Fairness-com/BiasClean)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![Version](https://img.shields.io/badge/Version-3.10.10-blue)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Domains](https://img.shields.io/badge/Domains-7%20Supported-brightgreen)

**Production-ready audit-first fairness pipeline with traffic light governance for algorithmic decision systems.**

Developed to support the **BiasClean™** fairness framework described in  
**_BiasClean: Audit-First Fairness Pipeline for Algorithmic Governance_ (Tavakoli, 2026).**

---

## 🎯 Quick Start: Audit-First Fairness Pipeline

**Audit your data with traffic light governance before any mitigation:**
1. For Non-Technical Users
from biasclean_v3_production import run_biasclean_interactive
run_biasclean_interactive()

2. For Data Analysts  
from biasclean_v3_production import UniversalBiasClean
pipeline = UniversalBiasClean(domain='justice', mode='audit_first')

---
### Traffic Light Governance System (v3.0):

*Pre-Mitigation Audit Performed Before Any Intervention:* **Safety First**  
*Governance Decision Based on Data Quality & Baseline Fairness:* **🟢🟡🔴 Recommendations**

#### Traffic Light Meanings:
- **🟢 GREEN:** Safe to proceed with bias mitigation
- **🟡 YELLOW:** Review required before proceeding
- **🔴 RED:** Do not deploy - address data quality issues first

#### Cross-Domain Validation:
- **Justice:** Re-validated against 6 real datasets (COMPAS, NC & Oklahoma City traffic stops, NIJ Recidivism Challenge, UCI Communities & Crime) — see [BiasClean External Validation in Justice Domain](Validations/BiasClean_External_Validation_Justice_Domain.pdf). (A companion *Phase 1: Consolidation & Regression Testing* report also exists — link to be added once it's uploaded to this repo.)
- **MIMIC-IV (Healthcare):** All features functional
- **German Credit (Finance):** No regressions from v2.7
- **OULAD (Education):** Harm detection working
- **Resume Callback (Hiring):** All weights validated

<!-- Note: Healthcare/Finance/Education/Hiring bullets above are from the
     original v3.0 release and have not been independently re-checked with
     the same real-data rigor as Justice. -->

#### Live Production Tool
Not yet live for BiasClean; pending Technical Director sign-off (same status as the FDK Toolkit).
<!-- TODO(Hamid): flagged previously as stale — confirm whether this URL is
     currently accurate before this update is published; leaving as-is rather
     than guessing at a replacement. -->

---

**A note on the datasets behind the Justice validation:** the real datasets used (North Carolina traffic stops is ~4.9GB; Oklahoma City traffic stops also exceeds the limit even compressed) are larger than GitHub's 25MB file size limit and are not included in this repository. They are drawn from public sources — the Stanford Open Policing Project (NC/OK City stops), the National Institute of Justice's Recidivism Forecasting Challenge, and the UCI Machine Learning Repository (Communities and Crime) — and the full methodology and results are in the validation report linked above.


## 📚 Documentation

| Document | Description |
|----------|-------------|
| [BiasClean_Methodology.md](BiasClean_Methodology.md) | Safety design (thermostats/fuses), evidence-based weighting framework, and citations |
| [DISCLAIMER.md](DISCLAIMER.md) | Legal and ethical disclaimer – BiasClean is not a legal compliance tool |
| [BiasClean_Methodology.md § Thresholds](BiasClean_Methodology.md) | GREEN/YELLOW/RED threshold rationale with exact values |
| [BiasClean_Methodology.md § Weighting](BiasClean_Methodology.md) | Domain-specific weighting framework (SIW-ESW-PLW) with 7 domain tables |
| [README.md § Four Questions Before Remediation](#four-questions-before-remediation) | Ethical boundaries, risks, and four questions before remediation |
| [examples/compas_biasclean_demo.ipynb](examples/compas_biasclean_demo.ipynb) | Complete COMPAS workflow with all 4 execution modes |
| [examples/basic_usage.ipynb](examples/basic_usage.ipynb) | Basic usage example |
| [examples/custom_dataset.ipynb](examples/custom_dataset.ipynb) | Custom dataset example |
| [examples/multi_domain_test.ipynb](examples/multi_domain_test.ipynb) | Multi-domain testing |


**Source for all documentation:** Tavakoli, H. (2026). *BiasClean: Audit-First Fairness Pipeline for Algorithmic Governance*. Chapters 8, 33, 34, 36, 37.

---

### 🔍 What's New in v3.0: Audit-First Architecture

#### ✅ Traffic Light Governance
- **Pre-mitigation safety checks** before any intervention
- **Clear deployment recommendations** (🟢🟡🔴) for decision-makers
- **Vulnerable subgroup detection** identifies at-risk groups early
- **Conditional mitigation** only proceeds if audit approves

#### ✅ Multi-Domain Production Support
- **7 supported domains** with UK regulatory-aligned weights
- **Domain-specific configurations** for justice, health, finance, hiring, education, business, governance
- **Jurisdiction-ready weights** based on Equality Act 2010 framework
- **Empirically validated thresholds** from v2.7 research

#### ✅ User-Centric Design
- **Interactive no-code interface** for non-technical users
- **Three operating modes**: audit_first (recommended), audit_only, legacy (v2.7)
- **Quick audit mode** for instant fairness diagnosis
- **Professional reports** with executive summaries

#### ✅ Production Readiness
- **Single-file distribution** (~529KB, 10,044 lines, 15 classes, 119 functions)
- **No test code, no Colab dependencies** - 100% production code
- **Standard libraries only** (pandas, numpy, scikit-learn, matplotlib, seaborn)
- **Cross-platform compatibility** (Windows, Mac, Linux, Python 3.8+)

#### ✅ Enhanced Safety & Governance
- **Harm prevention** blocks mitigation if critical issues detected
- **Transparent decision rationale** for all traffic light assignments
- **Complete audit trails** documenting all findings and actions
- **Human-in-the-loop design** requires expert review for YELLOW scenarios

---

## 🏗️ The Four Execution Modes

| Mode | Governance Gate | Mitigation | SVM Enforcement | Primary Output |
|------|----------------|------------|-----------------|----------------|
| **Audit-Only** | ✅ Yes | ❌ No | ❌ No | Audit log only |
| **Audit-First** | ✅ Yes | ✅ Yes (conditional) | ❌ No | Corrected dataset + report |
| **Legacy (No SVM)** | ❌ No | ✅ Yes | ❌ No | Corrected dataset + report |
| **Legacy (+ SVM)** | ❌ No | ✅ Yes | ✅ Yes | Corrected dataset + model outputs |

**Source:** Chapter 33.3, Table 33.1

---

## 🌍 Overview

**BiasClean v3.10.10** is a production-ready audit-first fairness pipeline with traffic light governance, designed to prevent harm by auditing datasets before any bias mitigation is applied. It provides a transparent, defensible, multi-domain weighting framework aligned with **UK structural inequality patterns** and regulatory expectations, enabling safe fairness assessment and conditional mitigation.

The toolkit implements an **audit-first architecture** with clear traffic light recommendations (🟢🟡🔴), preventing deployment of bias mitigation on unsuitable datasets and ensuring human oversight for borderline cases.

---

## 🏗️ System Architecture

BiasClean follows a structured, evidence-weighted pipeline for surgical bias mitigation with integrated SVM optimization:

<img width="1112" height="405" alt="BiasClean v2.5 Architecture" src="https://github.com/user-attachments/assets/e00f7153-c937-4cf3-904e-fddc48452ded" />

## 🔍 Why BiasClean Is Different

BiasClean is specifically engineered for the UK context, moving beyond generic fairness tools.

| Feature | BiasClean Approach | Generic Fairness Tools |
|:--|:--|:--|
| **Regulatory Alignment** | Designed around UK Equality Act, MoJ, NHS, FCA guidelines | Often US-centric or generic |
| **Methodology** | Transparent SIW-ESW-PLW evidence-weighted framework with SVM integration | Often in-processing "black boxes" |
| **Domain Specificity** | 7 UK domains with custom evidence matrices | One-size-fits-all |
| **Leakage Prevention** | Strict feature governance and exclusion rules | Often overlook temporal/proxy leakage |
| **Output** | Bias-mitigated dataset & full audit trail | Model metrics only |
| **Transparency** | Every weight and decision is explainable | Opaque adjustments |

### ✅ 7 Domains Supported with UK Regulatory Weights

| Domain | Primary Weights | Key Use Cases | Regulatory Alignment |
|--------|----------------|---------------|----------------------|
| **Justice** | Ethnicity (0.25), SES (0.20) | Recidivism, bail, sentencing | Ministry of Justice, HM Inspectorate |
| **Healthcare** | Ethnicity (0.25), Disability (0.15) | Diagnosis, triage, treatment | NHS Digital, Public Health England |
| **Finance** | SES (0.30), Ethnicity (0.20) | Credit, loans, insurance | Financial Conduct Authority, Bank of England |
| **Hiring** | Gender (0.20), Ethnicity (0.25) | Recruitment, promotions, offers | Equality & Human Rights Commission |
| **Education** | SES (0.25), Disability (0.15) | Admissions, grading, outcomes | Department for Education |
| **Business** | Ethnicity (0.25), Gender (0.20) | Funding, contracts, procurement | BEIS, Social Mobility Commission |
| **Governance** | Gender (0.20), Ethnicity (0.25) | Elections, appointments, representation | ONS, Electoral Commission |

*Weights reflect UK regulatory priorities under Equality Act 2010 and can be adapted for other jurisdictions.*

## 🏥 Real-World Use Cases

### Healthcare: Diagnostic AI Access
**Context**: AI system for prioritizing specialist referrals  
**Sensitive Attributes**: Ethnicity, SocioeconomicStatus, Region  
**Fairness Risk**: Lower referral rates for minority ethnic groups and deprived regions, potentially exacerbating health inequalities  
**BiasClean Solution**: Applies health domain weights (Ethnicity: 0.25, SES: 0.20) to rebalance dataset, ensuring equitable representation before model training.

### Justice: Risk Assessment Training Data
**Context**: Algorithm predicting recidivism risk using historical data  
**Sensitive Attributes**: Ethnicity, Age, Region  
**Fairness Risk**: Over-representation of young minority defendants creating biased training data  
**BiasClean Solution**: Uses justice domain weights (Ethnicity: 0.25, Age: 0.15, Region: 0.15) to surgically rebalance dataset composition.

### Hiring: Resume Screening Fairness (v3.0 Validated)
**Context**: Training data for automated CV screening system (4,870 OpenIntro resume records) 
**Sensitive Attributes**: Gender, Ethnicity, Age  
**Fairness Risk**: Under-representation of minority ethnic and female applicants in technical roles  
**BiasClean v3.0 Solution**: Audit-first approach checks data quality first, then applies hiring domain weights (Ethnicity: 0.25, Gender: 0.20) with traffic light governance ensuring safe deployment.

---

## ⚙️ Package Structure

BiasClean is distributed as a single-file pipeline plus a lightweight web service wrapper:

```
BiasClean/
│
├── biasclean_v3_5_1_terminal.py    # MAIN PIPELINE (v3.10.10 internally — see docs/CHANGELOG.md)
│   ├── UniversalBiasClean (core orchestration class)
│   ├── run_biasclean_interactive() / run_interactive_pipeline() (no-code entry points)
│   └── quick_audit() (diagnostics without mitigation)
│
├── biasclean_server.py             # Web service wrapper (see Procfile / render.yaml)
├── biasclean_app.py                # Flask application
├── docs/CHANGELOG.md               # Full version history
├── DISCLAIMER.md                   # Legal and ethical disclaimer
└── Validations/                    # Real-dataset validation reports (Justice domain)

*Output Directory (created after running):*

biasclean_results/
├── corrected_dataset.csv           # Bias-mitigated data
├── audit_trail.json                # Full machine-readable results
└── report.pdf                      # Plain-language summary + technical detail
```

### 🚀 Installation & Usage

**Requirements**

Python 3.8+

pip (Python package manager)

Install Dependencies
pip install pandas numpy scipy scikit-learn matplotlib seaborn fairlearn reportlab

Download BiasClean
Download `biasclean_v3_5_1_terminal.py` from this repository

Interactive Interface (Recommended for non-coders)
from biasclean_v3_5_1_terminal import run_biasclean_interactive
run_biasclean_interactive()

Programmatic Usage
from biasclean_v3_5_1_terminal import UniversalBiasClean
import pandas as pd

df = pd.read_csv('your_data.csv')

pipeline = UniversalBiasClean(
    domain='justice',
    mode='audit_first',
    enable_svm=False
)

results = pipeline.process_dataset(
    df=df,
    target_column='outcome',
    auto_approve_threshold=0.80
)

print(f"Traffic Light: {results['audit']['recommendation']['traffic_light']}")

Quick Audit (No Mitigation)
from biasclean_v3_5_1_terminal import quick_audit
results = quick_audit('my_data.csv', domain='justice', target='outcome')

### 🧪 Testing & Validation
The toolkit includes comprehensive validation:

Statistical Diagnosis: Chi-square tests for distribution uniformity

Fairness Metrics: 158 FDK metrics across seven domains, spanning group fairness, error parity, robustness, and causal dimensions

Production Readiness: Dual validation with bias scores and distribution alignment


#### Run production test suite
python -m pytest tests/
### ⚖️ Legal & Ethical Disclaimer

**BiasClean™ is a technical bias detection and mitigation toolkit. It is NOT a legal compliance tool.**

- Does not determine legal compliance with Equality Act 2010, GDPR, EU AI Act, or any other regulation
- Does not adjudicate discrimination claims
- Does not replace human judgment or organizational governance
- Traffic light indicators represent statistical thresholds, not legal verdicts

**Before remediation, ask four questions (Source: Chapter 37.2):**
1. Is the disparity real and meaningful?
2. Does the disparity reflect a legitimate pattern or bias?
3. Can you explain the change to affected communities?
4. Have you documented your reasoning?

Full disclaimer available in [DISCLAIMER.md](DISCLAIMER.md).

#### 📄 License
Software (BiasClean Toolkit code): Apache License 2.0
See LICENSE and NOTICE in the repository root.

Book and explanatory text: CC BY-NC-SA 4.0
The book BiasClean: Evidence-Weighted Pre-Processing for UK Fairness Audits remains under a Creative Commons licence suitable for educational and non-commercial use.

<!-- TODO(Hamid): the citation block below still says v3.0/v3.0.0. Left as-is
     rather than guessing whether a formal citation should track every patch
     release or stay pinned to the v3.x line — worth a deliberate decision,
     since anyone already citing v3.0.0 shouldn't have that reference silently
     invalidated by an unannounced bump. -->

#### 📚 Citation & Credits
If you use or reference BiasClean v3.0 in your research or production, please cite:

Tavakoli, H. (2026). BiasClean: Audit-First Fairness Pipeline for Algorithmic Governance (v3.10.10).

Related Publication:
Tavakoli, H. (2026). BiasClean: An Audit-First, No-Code Methodology for Fairness Monitoring and Governance-Aware Bias Mitigation. IEEE Transactions on Artificial Intelligence and Society.

Repository: AI-Fairness-com/BiasClean
Correspondence: h.tavakoli@ai-fairness.com

#### BibTeX Citation
@software{BiasClean2026,
  author  = {Hamid Tavakoli},
  title   = {BiasClean Toolkit: Production-Ready Audit-First Fairness Pipeline with Traffic Light Governance},
  year    = {2026},
  url     = {https://github.com/AI-Fairness-com/BiasClean},
  version = {v3.10.10},
  note    = {Audit-first architecture with traffic light governance for 7 UK domains}
}
