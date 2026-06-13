# 🧹 BiasClean Toolkit v3.0

**Production-ready audit-first fairness pipeline with traffic light governance for algorithmic decision systems.**

Developed to support the **BiasClean™** fairness framework described in  
**_BiasClean: Audit-First Fairness Pipeline for Algorithmic Governance_ (Tavakoli, 2026).**

---

## 🚦 Traffic Light Governance System (v3.0)

**Pre-Mitigation Audit Performed Before Any Intervention – Safety First**

| Color | Meaning | Action Required |
|-------|---------|-----------------|
| 🟢 **GREEN** | Safe to proceed with bias mitigation | Continue monitoring; no immediate intervention required |
| 🟡 **YELLOW** | Review required before proceeding | Operational Fairness Committee review; document findings |
| 🔴 **RED** | Do not deploy – address data quality issues first | Escalate to Technical Review Board; suspend deployment |

**Source:** Chapter 33.3, p. 296–297; Chapter 8.6, p. 126–128

---

## 🎯 Quick Start

### For Non-Technical Users (Interactive)

from biasclean_v3_production import run_biasclean_interactive
run_biasclean_interactive()

### For Data Analysts (Programmatic)

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

### Quick Audit (No Mitigation)

from biasclean_v3_production import quick_audit
results = quick_audit('my_data.csv', domain='justice', target='outcome')

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| DISCLAIMER.md | Legal and ethical disclaimer – BiasClean is not a legal compliance tool |
| docs/thresholds.md | GREEN/YELLOW/RED threshold rationale with exact values |
| docs/weighting.md | Domain-specific weighting framework (SIW-ESW-PLW) with 7 domain tables |
| docs/tradeoffs.md | Ethical boundaries, risks, and four questions before remediation |
| examples/compas_biasclean_demo.ipynb | Complete COMPAS workflow with all 4 execution modes |
| examples/basic_usage.ipynb | Basic usage example |
| examples/custom_dataset.ipynb | Custom dataset example |
| examples/multi_domain_test.ipynb | Multi-domain testing |

**Source for all documentation:** Tavakoli, H. (2026). *BiasClean: Audit-First Fairness Pipeline for Algorithmic Governance*. Chapters 8, 33, 34, 36, 37.

---

## 🔍 What's New in v3.0: Audit-First Architecture

### ✅ Traffic Light Governance
- **Pre-mitigation safety checks** before any intervention
- **Clear deployment recommendations** (🟢🟡🔴) for decision-makers
- **Vulnerable subgroup detection** identifies at-risk groups early
- **Conditional mitigation** only proceeds if audit approves

### ✅ Multi-Domain Production Support
- **7 supported domains** with UK regulatory-aligned weights
- **Domain-specific configurations** for justice, health, finance, hiring, education, business, governance
- **Jurisdiction-ready weights** based on Equality Act 2010 framework
- **Empirically validated thresholds** from v2.7 research

### ✅ User-Centric Design
- **Interactive no-code interface** for non-technical users
- **Three operating modes**: audit_first (recommended), audit_only, legacy (v2.7)
- **Quick audit mode** for instant fairness diagnosis
- **Professional reports** with executive summaries

### ✅ Production Readiness
- **Single-file distribution** (181KB, 4,420 lines, 11 classes, 80 functions)
- **No test code, no Colab dependencies** – 100% production code
- **Standard libraries only** (pandas, numpy, scikit-learn, matplotlib, seaborn)
- **Cross-platform compatibility** (Windows, Mac, Linux, Python 3.8+)

### ✅ Enhanced Safety & Governance
- **Harm prevention** blocks mitigation if critical issues detected
- **Transparent decision rationale** for all traffic light assignments
- **Complete audit trails** documenting all findings and actions
- **Human-in-the-loop design** requires expert review for YELLOW scenarios

---

## 🏗️ The Four Execution Modes

| Mode | Governance Gate | Mitigation | SVM Enforcement | Primary Output |
|------|----------------|------------|-----------------|----------------|
| Audit-Only | ✅ Yes | ❌ No | ❌ No | Audit log only |
| Audit-First | ✅ Yes | ✅ Yes (conditional) | ❌ No | Corrected dataset + report |
| Legacy (No SVM) | ❌ No | ✅ Yes | ❌ No | Corrected dataset + report |
| Legacy (+ SVM) | ❌ No | ✅ Yes | ✅ Yes | Corrected dataset + model outputs |

**Source:** Chapter 33.3, Table 33.1, p. 297

---

## 🌍 Domain-Specific Weighting (7 Domains)

BiasClean uses evidence-based weights aligned with UK regulatory priorities (Equality Act 2010).

| Domain | Primary Weights | Key Use Cases | Regulatory Alignment |
|--------|----------------|---------------|----------------------|
| Justice | Ethnicity (0.25), SES (0.20) | Recidivism, bail, sentencing | Ministry of Justice |
| Healthcare | Ethnicity (0.25), Disability (0.15) | Diagnosis, triage, treatment | NHS Digital |
| Finance | SES (0.30), Ethnicity (0.20) | Credit, loans, insurance | Financial Conduct Authority |
| Hiring | Gender (0.20), Ethnicity (0.25) | Recruitment, promotions | Equality & Human Rights Commission |
| Education | SES (0.25), Disability (0.15) | Admissions, grading, outcomes | Department for Education |
| Business | Ethnicity (0.25), Gender (0.20) | Funding, contracts, procurement | BEIS |
| Governance | Gender (0.20), Ethnicity (0.25) | Elections, appointments | ONS, Electoral Commission |

**Source:** Chapter 34, pp. 303–307

---

## 🏥 Real-World Use Cases

### Healthcare: Diagnostic AI Access
**Context:** AI system for prioritizing specialist referrals  
**Sensitive Attributes:** Ethnicity, SocioeconomicStatus, Region  
**BiasClean Solution:** Applies health domain weights to rebalance dataset before model training.

### Justice: Risk Assessment Training Data
**Context:** Algorithm predicting recidivism risk using historical data  
**Sensitive Attributes:** Ethnicity, Age, Region  
**BiasClean Solution:** Uses justice domain weights to surgically rebalance dataset composition.

### Hiring: Resume Screening Fairness (v3.0 Validated)
**Context:** Training data for automated CV screening system  
**Sensitive Attributes:** Gender, Ethnicity, Age  
**BiasClean v3.0 Solution:** Audit-first approach with traffic light governance ensuring safe deployment.

**Source:** Chapter 36, pp. 323–329

---

## ⚙️ Output Artifacts

After running BiasClean (in modes that produce outputs), the following files are generated in `biasclean_results/`:

biasclean_results/
├── corrected_dataset.csv           # Bias-mitigated data (if approved)
├── pipeline_summary.json           # Complete results in JSON
├── biasclean_report.html          # Visual dashboard (open in browser)
├── disparity_comparison.png       # Before/after fairness charts
├── fairness_improvements.png      # Feature-level improvements
└── data_integrity.png            # Quality check visualizations

---

## 🚀 Installation

### Requirements
- Python 3.8+
- pip (Python package manager)

### Install Dependencies

pip install pandas numpy scipy scikit-learn matplotlib seaborn

### Download BiasClean v3.0

Simply download `biasclean_v3_production.py` from the repository.

---

## 🧪 Testing & Validation

The toolkit includes comprehensive validation:

| Test | Description |
|------|-------------|
| Statistical Diagnosis | Chi-square tests for distribution uniformity |
| Fairness Metrics | 34 FDK metrics across group fairness, error parity, robustness |
| Production Readiness | Dual validation with bias scores and distribution alignment |
| Cross-Domain Validation | COMPAS (Justice), MIMIC-IV (Healthcare), German Credit (Finance), OULAD (Education), Resume Callback (Hiring) |

---

## ⚖️ Legal & Ethical Disclaimer

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

Full disclaimer available in DISCLAIMER.md.

---

## 📄 License

| Component | License |
|-----------|---------|
| Software (BiasClean Toolkit code) | Apache License 2.0 |
| Book and explanatory text | CC BY-NC-SA 4.0 |

See LICENSE and NOTICE in the repository root.

---

## 📚 Citation & Credits

If you use or reference BiasClean v3.0 in your research or production, please cite:

@software{BiasClean2026v30,
    author = {Hamid Tavakoli},
    title = {BiasClean Toolkit v3.0: Production-Ready Audit-First Fairness Pipeline with Traffic Light Governance},
    year = {2026},
    url = {https://github.com/AI-Fairness-com/BiasClean},
    version = {v3.0.0},
    note = {Audit-first architecture with traffic light governance for 7 UK domains}
}

**Related Publication:** Tavakoli, H. (2026). BiasClean: An Audit-First, No-Code Methodology for Fairness Monitoring and Governance-Aware Bias Mitigation. *IEEE Transactions on Artificial Intelligence and Society*.

**Repository:** github.com/AI-Fairness-com/BiasClean

**Correspondence:** h.tavakoli@ai-fairness.com

---

## About

Domain-Specific Bias Detection and Mitigation Toolkit – UK-Focused Fairness Engine for Structured Data Pre-processing