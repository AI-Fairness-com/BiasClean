# 🧹 BiasClean Toolkit

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![GitHub Repository](https://img.shields.io/badge/GitHub-AI--Fairness--com%2FBiasClean-blue)](https://github.com/AI-Fairness-com/BiasClean)
![Python](https://img.shields.io/badge/python-3.7%2B-green)
![Bias Reduction](https://img.shields.io/badge/Bias%20Reduction-5.6%25-success)

**A domain-aware pre-processing toolkit for detecting and mitigating demographic bias in UK datasets before modelling.**

Developed to support the **BiasClean™** fairness pre-processing framework described in the book  
**_BiasClean: Evidence-Weighted Pre-Processing for UK Fairness Audits_ (Tavakoli, 2025).**

---

## 🎯 Quick Start: Reproduce COMPAS Results

**Experience 5.6% bias reduction on real justice data:**

```bash
# 1. Launch Web Interface
python biasclean.py
# Navigate to http://localhost:5000 and upload data/real_datasets/compas.csv

# 2. Run Jupyter Demo
jupyter notebook demos/BiasClean_Demo.ipynb
# Execute all cells to see full statistical analysis
COMPAS Validation Results:

Overall Bias Reduction: 5.6% (0.3325 → 0.3139)

Data Retention: 97.4% (7,214 → 7,029 records)

Key Feature Improvements:

🎯 Gender: 49.5% improvement

🎯 Race: 11.4% improvement

🎯 Ethnicity: 11.4% improvement

🌍 Overview
BiasClean v2.0 is an evidence-based fairness cleaning engine designed to remove demographic representation bias with the same rigour traditionally applied to dirty or missing data. It provides a transparent, defensible, multi-domain weighting framework aligned with UK structural inequality patterns and regulatory expectations, enabling the creation of fairer datasets prior to model training.

The toolkit implements a sophisticated 7×7 matrix of UK domains and universal fairness features, each weighted using the SIW-ESW-PLW framework (Structural Inequality Weight, Evidence Strength Weight, Policy & Legal Relevance Weight) based on official UK statistics and regulatory guidance.

🏗️ System Architecture
BiasClean follows a structured, evidence-weighted pipeline for surgical bias mitigation:

<img width="1112" height="405" alt="Screenshot 2025-11-25 at 08 13 56" src="https://github.com/user-attachments/assets/e00f7153-c937-4cf3-904e-fddc48452ded" />
🔍 Why BiasClean Is Different
BiasClean is specifically engineered for the UK context, moving beyond generic fairness tools.

Feature	BiasClean Approach	Generic Fairness Tools
Regulatory Alignment	Designed around UK Equality Act, MoJ, NHS, FCA guidelines	Often US-centric or generic
Methodology	Transparent SIW-ESW-PLW evidence-weighted framework	Often in-processing "black boxes"
Domain Specificity	7 UK domains with custom evidence matrices	One-size-fits-all
Output	Bias-mitigated dataset & full audit trail	Model metrics only
Transparency	Every weight and decision is explainable	Opaque adjustments
🧩 Supported Domains & Fairness Features
BiasClean operates on a 7×7 matrix of UK domains and universal fairness features, each weighted with evidence from official national sources.

Core Domains
Domain	Key Evidence Sources
Justice	Ministry of Justice (MoJ), HM Inspectorate of Constabulary
Health	NHS Digital, Public Health England
Finance	Financial Conduct Authority (FCA), Bank of England
Education	Department for Education (DfE), Office for Students
Hiring	Equality and Human Rights Commission (EHRC)
Business	Department for Business, Energy & Industrial Strategy (BEIS)
Governance	Office for National Statistics (ONS), Government Equalities Office
Universal Fairness Features
Feature	Description	Key Data Sources
Ethnicity	Racial and ethnic group representation	ONS, EHRC
SocioeconomicStatus	Income, education, occupation-based disparities	ONS, Social Mobility Commission
Region	Geographic and regional inequality	ONS, NHS
Age	Behavioural gradients affecting outcomes	ONS demographic risk profiles
Gender	Documented bias across hiring, health and leadership	EHRC, ONS gender pay gap
DisabilityStatus	Protected characteristic with consistent disadvantage	Equality Act, NHS, DWP data
MigrationStatus	Affects service access and civic participation	ONS, Electoral Commission
🏥 Real-World Use Cases
Healthcare: Diagnostic AI Access
Context: AI system for prioritizing specialist referrals
Sensitive Attributes: Ethnicity, SocioeconomicStatus, Region
Fairness Risk: Lower referral rates for minority ethnic groups and deprived regions, potentially exacerbating health inequalities
BiasClean Solution: Applies health domain weights (Ethnicity: 0.25, SES: 0.20) to rebalance dataset, ensuring equitable representation before model training.

Justice: Risk Assessment Training Data ✅ COMPAS-VALIDATED
Context: Algorithm predicting recidivism risk using historical data
Sensitive Attributes: Ethnicity, Age, Region
Fairness Risk: Over-representation of young minority defendants creating biased training data
BiasClean Solution: Uses justice domain weights (Ethnicity: 0.25, Age: 0.15, Region: 0.15) to surgically rebalance dataset composition.
Results: 5.6% overall bias reduction with 49.5% gender fairness improvement on 7,214 COMPAS records.

Hiring: Recruitment Pipeline Data
Context: Training data for automated CV screening system
Sensitive Attributes: Gender, Age, DisabilityStatus
Fairness Risk: Under-representation of female, older, and disabled applicants in technical roles
BiasClean Solution: Applies hiring domain weights (Gender: 0.20, DisabilityStatus: 0.15, Age: 0.10) with industry-grade SMOTE rebalancing.

⚙️ Repository Structure
text
BiasClean/
│
├── data/                           # Real datasets for validation
│   └── real_datasets/              # COMPAS dataset included
│
├── demos/                          # Jupyter notebook demonstrations
│   └── BiasClean_Demo.ipynb        # COMPAS-validated demo
│
├── docs/                           # Comprehensive documentation
│   ├── installation.md            # Step-by-step installation guide
│   ├── architecture.md            # System architecture details
│   ├── domains.md                 # Domain-specific explanations
│   ├── example_usage.md           # Practical usage examples
│   └── disclaimer.md              # Legal and ethical guidelines
│
├── static/                        # Web interface static files
├── templates/                     # Web interface templates
│
├── tests/                         # Comprehensive test suite
│   └── [Test files to be added]   # [To be populated]
│
├── biased_datasets_samples/       # Example biased datasets
├── examples/                      # Usage examples
├── professional_viz/              # Professional visualizations
│
├── biasclean.py                   # Main Flask web application
├── biasclean_cli.py               # Command-line interface
├── biasclean_pipeline.py          # Core pipeline functions
├── biasclean_v2.py                # Main BiasClean algorithm
├── requirements.txt               # Python dependencies
├── render.yaml                    # Deployment configuration
├── LICENSE                        # Apache 2.0 License
├── NOTICE                         # Copyright notices
└── README.md                      # Project documentation
🚀 Installation & Usage
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

Production Web Interface
Live Tool: https://www.ai-fairness.com

No-code CSV upload and bias analysis

7 UK domain selections

Professional visualizations

Production-quality API

Command-Line Interface
bash
python biasclean_cli.py
Production Pipeline
python
from biasclean_pipeline import biasclean_full_pipeline

results = biasclean_full_pipeline(
    input_path='your_dataset.csv',
    domain='health',  # or justice, finance, etc.
    mode='industry'
)
🧪 Testing & Validation
COMPAS Dataset Validation ✅ PEER REVIEW READY
Real Dataset: 7,214 COMPAS records with documented bias patterns

Statistical Rigor: Fisher's exact testing (p < 0.000000)

Results: 5.6% bias reduction with 97.4% data retention

Feature Improvements: Gender (49.5%), Race (11.4%), Ethnicity (11.4%)

The toolkit includes comprehensive validation:

Statistical Diagnosis: Chi-square tests for distribution uniformity

Industry Metrics: Data retention ≥92%, meaningful fairness gains

Production Readiness: Dual validation with bias scores and distribution alignment

bash
# Run production test suite
python -m pytest tests/
⚖️ Legal & Ethical Disclaimer
BiasClean™ is a research and educational toolkit for bias mitigation in datasets. It does not provide legal, regulatory, or compliance advice. Users are responsible for ensuring appropriate dataset preparation and domain-compliant use. Full disclaimer available in docs/disclaimer.md.

📄 License
Software (BiasClean Toolkit code): Apache License 2.0
See LICENSE and NOTICE in the repository root.

Book and explanatory text: CC BY-NC-SA 4.0
The book BiasClean: Evidence-Weighted Pre-Processing for UK Fairness Audits remains under a Creative Commons licence suitable for educational and non-commercial use.

📚 Citation & Credits
If you use or reference this toolkit in your research, please cite:

Tavakoli, H. (2025). BiasClean: Evidence-Weighted Pre-Processing for UK Fairness Audits. London: Apress.

Repository: https://github.com/AI-Fairness-com/BiasClean
Live Tool: https://www.ai-fairness.com
Correspondence: info@ai-fairness.com

BibTeX Citation
bibtex
@software{Tavakoli2025BiasClean,
  author  = {Hamid Tavakoli},
  title   = {BiasClean Toolkit: Evidence-Based Bias Mitigation for UK Datasets},
  year    = {2025},
  url     = {https://github.com/AI-Fairness-com/BiasClean},
  version = {v2.0.0}
}
🔬 COMPAS Validation Results
Justice Domain Analysis on 7,214 Records:

text
📊 OVERALL PERFORMANCE:
• Bias Reduction: 5.6% (0.3325 → 0.3139)
• Data Retention: 97.4% (7,214 → 7,029 records)
• Statistical Significance: p < 0.000000

🎯 FEATURE-SPECIFIC IMPROVEMENTS:
• Gender: 49.5% improvement (0.1399 → 0.0706)
• Race: 11.4% improvement (0.2318 → 0.2055)
• Ethnicity: 11.4% improvement (0.2318 → 0.2055)
• Migration Status: 11.4% improvement (0.2318 → 0.2055)
• Age: 1.1% improvement (0.3475 → 0.3439)
• Disability Status: 1.1% improvement (0.3475 → 0.3439)

📈 METHODOLOGY:
• Outcome-based fairness with Fisher's exact testing
• Justice domain weights applied (Ethnicity: 0.25, Race: 0.25, Age: 0.15)
• Industry SMOTE for data rebalancing
• Multi-objective constrained optimization
