# 🧹 BiasClean Toolkit v3.0

[![GitHub Repository](https://img.shields.io/badge/GitHub-AI--Fairness--com%2FBiasClean-blue)](https://github.com/AI-Fairness-com/BiasClean)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![Version](https://img.shields.io/badge/Version-3.0.0-blue)
![License](https://img.shields.io/badge/license-Open%20Source-green)
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
- **COMPAS (Justice):** Traffic lights accurate, thresholds correct
- **MIMIC-IV (Healthcare):** All features functional
- **German Credit (Finance):** No regressions from v2.7
- **OULAD (Education):** Harm detection working
- **Resume Callback (Hiring):** All weights validated

#### Live Production Tool: https://www.ai-fairness.com

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DISCLAIMER.md](DISCLAIMER.md) | Legal and ethical disclaimer – BiasClean is not a legal compliance tool |
| [docs/thresholds.md](docs/thresholds.md) | GREEN/YELLOW/RED threshold rationale with exact values |
| [docs/weighting.md](docs/weighting.md) | Domain-specific weighting framework (SIW-ESW-PLW) with 7 domain tables |
| [docs/tradeoffs.md](docs/tradeoffs.md) | Ethical boundaries, risks, and four questions before remediation |
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
- **Single-file distribution** (181KB, 4,420 lines, 11 classes, 80 functions)
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

**Source:** Chapter 33.3, Table 33.1, p. 297

---

## 🌍 Overview

**BiasClean v3.0** is a production-ready audit-first fairness pipeline with traffic light governance, designed to prevent harm by auditing datasets before any bias mitigation is applied. It provides a transparent, defensible, multi-domain weighting framework aligned with **UK structural inequality patterns** and regulatory expectations, enabling safe fairness assessment and conditional mitigation.

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

## ⚙️ Production Package Structure

BiasClean v3.0 is distributed as a **complete production-ready package**:

```
BiasClean_v3_Production_Package/
│
├── biasclean_v3_production.py       # MAIN PIPELINE (181KB, 4,420 lines)
│   ├── 11 classes, 80 functions
│   ├── No test code, no Colab dependencies
│   └── 100% production-ready
│
├── README_BiasClean_v3.md          # Complete documentation (11KB)
├── QUICKSTART.md                   # 30-second start guide (3.3KB)
├── RELEASE_NOTES_v3.0.md           # What's new in v3.0 (7KB)
├── DEPLOYMENT_PACKAGE_SUMMARY.txt  # Quick overview
└── START_HERE.txt                  # Getting started guide

*Output Directory (created after running):*

biasclean_results/
├── corrected_dataset.csv           # Bias-mitigated data (if approved)
├── pipeline_summary.json           # Complete results in JSON
├── biasclean_report.html          # Visual dashboard (open in browser)
├── disparity_comparison.png       # Before/after fairness charts
├── fairness_improvements.png      # Feature-level improvements
└── data_integrity.png            # Quality check visualizations
```

### 🚀 Installation & Usage

**Requirements**

Python 3.8+

pip (Python package manager)

Install Dependencies
pip install pandas numpy scipy scikit-learn matplotlib seaborn

Download BiasClean v3.0
Simply download biasclean_v3_production.py from the release package

Interactive Interface (Recommended for non-coders)
from biasclean_v3_production import run_biasclean_interactive
run_biasclean_interactive()

Programmatic Usage
from biasclean_v3_production import UniversalBiasClean
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
from biasclean_v3_production import quick_audit
results = quick_audit('my_data.csv', domain='justice', target='outcome')

### 🧪 Testing & Validation
The toolkit includes comprehensive validation:

Statistical Diagnosis: Chi-square tests for distribution uniformity

Fairness Metrics: 34 FDK metrics across group fairness, error parity, robustness, and causal dimensions

Production Readiness: Dual validation with bias scores and distribution alignment


#### Run production test suite
python -m pytest tests/
### ⚖️ Legal & Ethical Disclaimer

**BiasClean™ is a technical bias detection and mitigation toolkit. It is NOT a legal compliance tool.**

- Does not determine legal compliance with Equality Act 2010, GDPR, EU AI Act, or any other regulation
- Does not adjudicate discrimination claims
- Does not replace human judgment or organizational governance
- Traffic light indicators represent statistical thresholds, not legal verdicts

**Before remediation, ask four questions (Source: Chapter 37.2, p. 333):**
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

#### 📚 Citation & Credits
If you use or reference BiasClean v3.0 in your research or production, please cite:

Tavakoli, H. (2026). BiasClean: Audit-First Fairness Pipeline for Algorithmic Governance.

Related Publication:
Tavakoli, H. (2026). BiasClean: An Audit-First, No-Code Methodology for Fairness Monitoring and Governance-Aware Bias Mitigation. IEEE Transactions on Artificial Intelligence and Society.

Repository: AI-Fairness-com/BiasClean
Correspondence: h.tavakoli@ai-fairness.com

#### BibTeX Citation
@software{BiasClean2026v30,
  author  = {Hamid Tavakoli},
  title   = {BiasClean Toolkit v3.0: Production-Ready Audit-First Fairness Pipeline with Traffic Light Governance},
  year    = {2026},
  url     = {https://github.com/AI-Fairness-com/BiasClean},
  version = {v3.0.0},
  note    = {Audit-first architecture with traffic light governance for 7 UK domains}
}
