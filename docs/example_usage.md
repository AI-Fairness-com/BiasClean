# 🧪 BiasClean Toolkit - Example Usage Guide

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](https://www.apache.org/licenses/LICENSE-2.0)

This guide provides practical examples of using BiasClean™ for bias detection and mitigation across domains.  
The examples follow the upload → domain selection → bias analysis → mitigation → results workflow.

---

## 🌍 Overview

BiasClean™ operates on a consistent pattern:

1. Upload a **CSV dataset**
2. Select **domain** (justice, health, finance, education, hiring, business, governance)
3. BiasClean automatically detects:
   - Protected features (Gender, Age, Race, Ethnicity, etc.)
   - Statistical bias patterns
   - Domain-specific fairness risks
4. Run **bias mitigation** with Industry SMOTE
5. Receive **bias reduction report** with before/after comparisons

---

## 🚀 Jupyter Notebook Demo - Justice Domain

### 📓 COMPAS Dataset Demo Available

Access our comprehensive Justice domain validation:

```bash
demos/BiasClean_Demo.ipynb
🎯 Demo Features:

Complete bias analysis pipeline on COMPAS dataset

5.6% overall bias reduction demonstrated

Feature-specific improvement tracking

Professional visualizations

Statistical significance testing

🔬 COMPAS Results Achieved:

Overall Bias Reduction: 5.6% (0.3325 → 0.3139)

Data Retention: 97.4% (7,214 → 7,029 records)

Key Improvements:

Gender: 49.5% improvement

Race: 11.4% improvement

Ethnicity: 11.4% improvement

Age: 1.1% improvement

📊 Real Dataset Integration

python
# The COMPAS dataset is automatically loaded in the demo
# Located at: data/real_datasets/compas.csv

from biasclean_v2 import BiasClean
import pandas as pd

# Load COMPAS data (7,214 real-world records)
df = pd.read_csv('data/real_datasets/compas.csv')

# Initialize BiasClean with justice domain
bc = BiasClean(df, domain='justice')

# Run comprehensive bias analysis and mitigation
corrected_df, bias_report = bc.clean()

print(f"Bias Reduction: {bias_report['overall_reduction']}%")
print(f"Features Improved: {bias_report['features_improved']}")
Dataset Information

COMPAS Dataset: 7,214 real-world recidivism risk assessment records

Source: ProPublica COMPAS Analysis

Use Case: Justice domain bias mitigation validation

Protected Features: Gender, Age, Race, Ethnicity, Region

Jupyter Demo Access
The complete analysis is available in: demos/BiasClean_Demo.ipynb

The demo includes:

Real COMPAS dataset loading and preprocessing

Multi-feature bias detection with statistical testing

Industry SMOTE mitigation with constrained optimization

Before/after bias score comparisons

Professional visualization outputs

1️⃣ Web Interface - Complete Workflow
📁 Uploading Your Dataset
Launch the web interface:

bash
python biasclean.py
Navigate to http://localhost:5000

Upload your CSV file

Supported: Any CSV with demographic columns

Recommended: Include protected features (gender, age, race, etc.)

Select your domain from the 7 available options

🔍 Automatic Feature Detection
BiasClean automatically identifies:

Protected demographic features

Statistical bias patterns

Domain-specific risk factors

Data quality issues

⚙️ Running Bias Mitigation
Click "Run BiasClean" to execute:

Bias Detection: Statistical analysis of fairness disparities

Bias Mitigation: Industry SMOTE with multi-objective optimization

Results Generation: Comprehensive bias reduction report

📊 Example Results Output
Bias Reduction Report:

text
🎯 BIAS CLEANING RESULTS
• Overall Bias Reduction: 5.6%
• Data Retention: 97.4%
• Statistical Significance: p < 0.000000

📈 FEATURE IMPROVEMENTS:
• Gender: 49.5% improvement
• Race: 11.4% improvement
• Ethnicity: 11.4% improvement
• Age: 1.1% improvement
• Migration Status: 11.4% improvement
• Disability Status: 1.1% improvement
2️⃣ Command Line Interface
Basic Usage
bash
python biasclean_cli.py --input your_dataset.csv --domain justice
Advanced Options
bash
python biasclean_cli.py \
  --input data/real_datasets/compas.csv \
  --domain justice \
  --output corrected_compas.csv \
  --retention 0.95 \
  --visualize
Python API Integration
python
from biasclean_pipeline import biasclean_full_pipeline

# Run complete bias cleaning pipeline
results = biasclean_full_pipeline(
    input_path='your_dataset.csv',
    domain='justice',  # or health, finance, education, etc.
    mode='industry',
    output_path='cleaned_dataset.csv'
)

print(f"Bias reduced: {results['bias_reduction']}%")
print(f"Final bias score: {results['final_bias_score']}")
3️⃣ Domain-Specific Examples
🏥 Health Domain
Use Case: Medical diagnostic dataset

python
# Health domain emphasizes ethnicity and disability status
results = biasclean_full_pipeline(
    input_path='medical_data.csv',
    domain='health',
    mode='industry'
)
💰 Finance Domain
Use Case: Loan application data

python
# Finance domain emphasizes socioeconomic status and region
results = biasclean_full_pipeline(
    input_path='loan_applications.csv',
    domain='finance', 
    mode='industry'
)
🎓 Education Domain
Use Case: Student performance data

python
# Education domain emphasizes ethnicity and socioeconomic status
results = biasclean_full_pipeline(
    input_path='student_records.csv',
    domain='education',
    mode='industry'
)
🎯 Key Workflow Takeaways
Consistent Interface: Same workflow across all 7 domains

Domain-Aware: Different fairness weights per domain

Transparent: Full statistical reporting and visualization

Practical: Industry SMOTE maintains data utility

Validated: COMPAS dataset demonstrates real-world effectiveness

Live Production Tool: https://www.ai-fairness.com

## New Multi-Objective Optimization

# Old approach (sequential - limited to 7.5% reduction)
cleaner = BiasClean().fit('justice')
df_fixed = cleaner.transform_industry(df, diagnostics)

# New approach (multi-objective - achieves 16.1% reduction)  
cleaner = BiasCleanJustice()  # Domain-specialized
df_fixed = cleaner.multi_objective_optimize(df, diagnostics)

📬 Contact
For demonstration datasets, academic usage, or domain-specific questions:
info@ai-fairness.com
