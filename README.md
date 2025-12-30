# 🧹 BiasClean Toolkit

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![GitHub Repository](https://img.shields.io/badge/GitHub-AI--Fairness--com%2FBiasClean-blue)](https://github.com/AI-Fairness-com/BiasClean)
![Python](https://img.shields.io/badge/python-3.7%2B-green)
![Bias Reduction](https://img.shields.io/badge/Bias%20Reduction-42.1%25-success)
![Version](https://img.shields.io/badge/Version-2.5-blue)

**A domain-aware pre-processing toolkit for detecting and mitigating demographic bias in UK datasets before modelling.**

Developed to support the **BiasClean™** fairness pre-processing framework described in the book  
**_BiasClean: Evidence-Weighted Pre-Processing for UK Fairness Audits_ (Tavakoli, 2025).**

---

## 🎯 Quick Start: COMPAS Demo
**Reproduce 42.1% bias reduction on real justice data with SVM-integrated optimization:**
1. Launch Web Interface
python biasclean.py
- Navigate to https://ai-fairness.com/ and upload data/real_datasets/compas.csv

2. Run Jupyter Demo  
jupyter notebook demos/BiasClean_v2.5_Demo.ipynb

---
### COMPAS Validation Results (v2.5):

*Overall Justice domain Bias Reduction:* **42.1%** (0.10934 → 0.06333)  
*Data Retention:* **Optimized for fairness** (accuracy normalized to 56–65% range)

#### Key Fairness Metrics (FDK Validated):
- **Composite Bias Score:** 42.1% reduction  
- **Worst Group Accuracy:** 71.5% improvement  
- **Error Rate Difference:** 100% reduction  
- **Statistical Parity Difference:** -57.2% (trade-off noted)

#### Live Production Tool: https://www.ai-fairness.com

---

### 🚀 What's New in v2.5: SVM-Integrated Fairness Optimization

### ✅ SVM with Leakage Prevention
- **Integrated bias mitigation and fairness enforcement** in a single pipeline
- **Leakage-aware SVM training** based on margin optimization
- **Feature governance** to prevent protected-attribute leakage
- **Audit-ready optimization flow** with full transparency

### ✅ 7 Domains Supported
- **Justice** - Criminal justice bias detection (COMPAS-validated)
- **Health** - Healthcare bias analysis
- **Finance** - Financial services fairness
- **Hiring** - Employment & recruitment bias
- **Education** - Educational access & attainment bias
- **Business** - Business funding & investment bias
- **Governance** - Political representation & selection bias

### ✅ Weight-Prioritized Mitigation
Each domain follows **UK 2025 Domain-Specific Weight Prioritization**:
- **Justice**: Ethnicity (0.25) > SocioeconomicStatus (0.20) > Region/Age (0.15)
- **Health**: Ethnicity (0.25) > SocioeconomicStatus (0.20) > DisabilityStatus/Gender (0.15)
- **Business**: Ethnicity (0.25) > Gender (0.20) > Region/SES (0.15) > Age/Disability (0.10)

### ✅ New Features in v2.5
- **Integrated fairness pipeline** combining hierarchical bias mitigation with leakage-aware SVM
- **Strict feature exclusion rules** preventing temporal leakage and outcome proxies
- **Independent FDK validation** across 34 fairness metrics
- **Governance-aware optimization** ensuring auditability and oversight
- **Professional report generation** with fairness dashboards and bias logs

### ✅ Professional Report Generation
- **Dual-format outputs** - HTML and PDF publication-ready reports
- **Statistical dashboards** - Executive summaries with key fairness metrics
- **Visual analytics** - Disparity comparison, fairness improvements, data integrity charts
- **Session tracking** - Unique IDs with timestamped generation
- **Complete audit trails** - Pipeline execution logs with leakage diagnostics

---

## 🌍 Overview

**BiasClean v2.5** is an evidence-based fairness cleaning engine with integrated SVM optimization, designed to remove demographic representation bias with rigorous feature governance and leakage prevention. It provides a transparent, defensible, multi-domain weighting framework aligned with **UK structural inequality patterns** and regulatory expectations, enabling the creation of fairer datasets prior to model training.

The toolkit implements a sophisticated **7×7 matrix** of UK domains and universal fairness features, each weighted using the **SIW-ESW-PLW framework** (Structural Inequality Weight, Evidence Strength Weight, Policy & Legal Relevance Weight) based on official UK statistics and regulatory guidance.

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

## 🧩 Supported Domains & Fairness Features

BiasClean operates on a 7×7 matrix of UK domains and universal fairness features, each weighted with evidence from official national sources.

### Core Domains
| Domain | Key Evidence Sources |
|:--|:--|
| **Justice** | Ministry of Justice (MoJ), HM Inspectorate of Constabulary |
| **Health** | NHS Digital, Public Health England |
| **Finance** | Financial Conduct Authority (FCA), Bank of England |
| **Education** | Department for Education (DfE), Office for Students |
| **Hiring** | Equality and Human Rights Commission (EHRC) |
| **Business** | Department for Business, Energy & Industrial Strategy (BEIS) |
| **Governance** | Office for National Statistics (ONS), Government Equalities Office |

### Universal Fairness Features
| Feature | Description | Key Data Sources |
|:--|:--|:--|
| **Ethnicity** | Racial and ethnic group representation | ONS, EHRC |
| **SocioeconomicStatus** | Income, education, occupation-based disparities | ONS, Social Mobility Commission |
| **Region** | Geographic and regional inequality | ONS, NHS |
| **Age** | Behavioural gradients affecting outcomes | ONS demographic risk profiles |
| **Gender** | Documented bias across hiring, health and leadership | EHRC, ONS gender pay gap |
| **DisabilityStatus** | Protected characteristic with consistent disadvantage | Equality Act, NHS, DWP data |
| **MigrationStatus** | Affects service access and civic participation | ONS, Electoral Commission |

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

### Hiring: Recruitment Pipeline Data
**Context**: Training data for automated CV screening system  
**Sensitive Attributes**: Gender, Age, DisabilityStatus  
**Fairness Risk**: Under-representation of female, older, and disabled applicants in technical roles  
**BiasClean Solution**: Applies hiring domain weights (Gender: 0.20, DisabilityStatus: 0.15, Age: 0.10) with industry-grade SMOTE rebalancing.

---

## ⚙️ Repository Structure

**Repository Structure:**

''' text
BiasClean/
│
├── data/ # Real datasets for validation
│ └── real_datasets/ # COMPAS dataset included
│
├── demos/ # Jupyter notebook demonstrations
│ └── BiasClean_v2.5_Demo.ipynb # SVM-integrated fairness demo
│
├── docs/ # Comprehensive documentation
│ ├── installation.md # Step-by-step installation guide
│ ├── architecture.md # System architecture details
│ ├── domains.md # Domain-specific explanations
│ ├── example_usage.md # Practical usage examples
│ └── disclaimer.md # Legal and ethical guidelines
│
├── static/ # Web interface static files
├── templates/ # Web interface templates
│
├── tests/ # Comprehensive test suite
│ └── test_biasclean_v2_5.py # SVM-integrated pipeline tests
│
├── biased_datasets_samples/ # Example biased datasets
├── examples/ # Usage examples
├── professional_viz/ # Professional visualizations
│
├── biasclean.py # Main Flask web application
├── biasclean_cli.py # Command-line interface
├── biasclean_pipeline.py # Core pipeline functions
├── biasclean_v2_5.py # BiasClean v2.5 with SVM integration
├── requirements.txt # Python dependencies
├── render.yaml # Deployment configuration
├── LICENSE # Apache 2.0 License
├── NOTICE # Copyright notices
└── README.md # Project documentation

''' text

### 🚀 Installation & Usage
Requirements
Python 3.7+

pip (Python package manager)

Install Dependencies
bash
pip install -r requirements.txt
Web Interface (Recommended)
bash
python biasclean.py
Then open http://localhost:5000 in your browser.

Command-Line Interface
bash
python biasclean_cli.py
Production Pipeline
python
from biasclean_v2_5 import biasclean_integrated_pipeline

results = biasclean_integrated_pipeline(
input_path='your_dataset.csv',
domain='justice', # or health, finance, etc.
mode='industry',
enable_svm=True
)
### 🧪 Testing & Validation
The toolkit includes comprehensive validation:

Statistical Diagnosis: Chi-square tests for distribution uniformity

Fairness Metrics: 34 FDK metrics across group fairness, error parity, robustness, and causal dimensions

Production Readiness: Dual validation with bias scores and distribution alignment

bash
#### Run production test suite
python -m pytest tests/
### ⚖️ Legal & Ethical Disclaimer
BiasClean™ is a research and educational toolkit for bias mitigation in datasets. It does not provide legal, regulatory, or compliance advice. Users are responsible for ensuring appropriate dataset preparation and domain-compliant use. Full disclaimer available in docs/disclaimer.md.

#### 📄 License
Software (BiasClean Toolkit code): Apache License 2.0
See LICENSE and NOTICE in the repository root.

Book and explanatory text: CC BY-NC-SA 4.0
The book BiasClean: Evidence-Weighted Pre-Processing for UK Fairness Audits remains under a Creative Commons licence suitable for educational and non-commercial use.

#### 📚 Citation & Credits
If you use or reference this toolkit in your research, please cite:

Tavakoli, H. (2025). BiasClean: Evidence-Weighted Pre-Processing for UK Fairness Audits. London: Apress.

For v2.5 SVM-integrated fairness optimization:
Tavakoli, H. (2025). SVM-Integrated Fairness Optimization: BiasClean v2.5 With 42.1% Validated Fairness Improvement on COMPAS.

Repository: AI-Fairness-com/BiasClean
Correspondence: info@ai-fairness.com

#### BibTeX Citation
bibtex
@software{Tavakoli2025BiasCleanv25,
  author  = {Hamid Tavakoli},
  title   = {BiasClean Toolkit v2.5: SVM-Integrated Fairness Optimization for UK Datasets},
  year    = {2025},
  url     = {https://github.com/AI-Fairness-com/BiasClean},
  version = {v2.5},
  note    = {42.1\% validated fairness improvement on COMPAS with leakage-aware SVM}
}
