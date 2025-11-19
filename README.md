# BiasClean v2.0

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.7%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Domain-Specific Bias Detection and Mitigation Toolkit

BiasClean v2.0 is an open-source bias-cleaning pre-processing toolkit designed to treat demographic bias with the same rigour as dirty data. It uses domain-specific, region-specific weighted fairness features for UK datasets.

## 🎯 Key Features

- **7 UK Domains**: Justice, Health, Finance, Education, Hiring, Business, Governance
- **7 Universal Fairness Features**: Ethnicity, SocioeconomicStatus, Region, Age, Gender, DisabilityStatus, MigrationStatus
- **Evidence-Based Weights**: Derived from ONS, NHS, MoJ, FCA, DfE, EHRC, BEIS
- **Mathematical Rigor**: Representation ratio-based disparity measurement
- **Selective Downsampling**: Bias reduction with controlled data loss (8-15%)

## 📊 Performance Summary

| Metric | Result |
|--------|--------|
| Average Bias Reduction | 1.95% |
| Average Data Loss | 8.00% |
| Most Biased Domain | Governance |
| Least Biased Domain | Finance |
| Domains Supported | 7 |

## 🚀 Quick Start

```python
from biasclean_v2 import BiasClean, generate_synthetic_data

# Initialize and test
bias_clean = BiasClean()
bias_clean.fit('health')

df = generate_synthetic_data('health', n_samples=1000)
bias_score = bias_clean.score(df)
df_corrected = bias_clean.transform(df, mode='soft')
report = bias_clean.report(df, df_corrected)
