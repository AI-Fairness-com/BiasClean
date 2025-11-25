# 🏗️ BiasClean Toolkit - System Architecture

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](https://www.apache.org/licenses/LICENSE-2.0)

This document outlines the technical architecture of BiasClean™ v2.0, detailing the evidence-weighted framework for multi-domain bias mitigation validated on the COMPAS dataset.

---

## 🌍 Overview

BiasClean implements a structured, transparent pipeline for surgical bias mitigation across seven UK domains. The architecture follows a **detect → analyze → mitigate → validate** workflow with domain-specific evidence weighting.

**Validated Performance:**
- **5.6% overall bias reduction** on COMPAS dataset
- **97.4% data retention** (7,214 → 7,029 records)
- **Multi-feature improvement** across Gender, Race, and Ethnicity

---

## 🔧 Core Architecture Components

### 1. Input Layer
**Purpose:** Dataset ingestion and validation
```python
# Supported inputs
- CSV files (primary)
- Pandas DataFrames (API)
- Web uploads (Flask interface)
Features:

Automatic protected feature detection

Data quality assessment

Domain suggestion based on feature analysis

Memory optimization for large datasets

2. Domain Configuration Layer
Purpose: Evidence-based weight application

SIW-ESW-PLW Framework:

Structural Inequality Weight (SIW): Systemic impact severity

Evidence Strength Weight (ESW): Data robustness and consistency

Policy & Legal Relevance Weight (PLW): Regulatory alignment

Justice Domain Weights (COMPAS Validated):

python
{
    'Ethnicity': 0.25,        # Strong structural disparity
    'Race': 0.25,             # Documented justice system bias
    'SocioeconomicStatus': 0.20, # Deprivation impact
    'Region': 0.15,           # Geographic inequality
    'Age': 0.15,              # Behavioral gradients
    'MigrationStatus': 0.10,  # Service access barriers
    'DisabilityStatus': 0.10, # Protected characteristic
    'Gender': 0.05            # Documented but lower weight
}
3. Bias Detection Engine
Purpose: Statistical identification of fairness disparities

Methodology:

Fisher's Exact Testing: For categorical protected features

Chi-square Tests: Distribution uniformity analysis

Outcome-based Fairness: Recidivism rate disparities

Effect Size Calculation: Practical significance assessment

COMPAS Detection Results:

text
📊 STATISTICAL SIGNIFICANCE (p < 0.000000)
• Gender: Male 47.3% vs Female 35.7% (p=0.000000)
• Race: African-American 51.4% vs Caucasian 39.4% (p=0.000000)
• Age: Range 18-96 with 1.000 max disparity (p=0.000000)
4. Mitigation Engine
Purpose: Surgical bias reduction with constrained optimization

Industry SMOTE Implementation:

python
def constrained_smote_optimization(dataset, protected_features, domain_weights):
    """
    Multi-objective optimization preserving:
    - Data utility (97.4% retention)
    - Statistical distributions
    - Domain-specific fairness constraints
    """
Optimization Constraints:

Maximum 5% data modification per iteration

Preservation of outcome variable distributions

Domain weight adherence

Feature correlation maintenance

5. Validation & Reporting Layer
Purpose: Results verification and transparent reporting

Validation Metrics:

Bias Score Reduction: Overall and feature-specific

Data Utility Preservation: Retention and distribution integrity

Statistical Significance: Pre/post mitigation testing

Visualization: Professional comparative analysis

📊 Data Flow Architecture
Phase 1: Dataset Loading & Analysis
text
Input CSV → Feature Detection → Domain Assignment → Quality Assessment
COMPAS Example:

7,214 records, 53 features loaded

Protected features detected: ['Gender', 'Age', 'Race']

Domain auto-assigned: 'justice'

Data quality: 18.6% missing values identified

Phase 2: Statistical Diagnosis
text
Protected Features → Fisher's Testing → Disparity Calculation → Bias Scoring
COMPAS Results:

Initial bias score: 0.3325

3/3 protected features showed significant disparities

Required mitigation: True

Phase 3: Multi-Objective Mitigation
text
Domain Weights → Constrained SMOTE → Feature Optimization → Bias Reduction
COMPAS Optimization:

3 features targeted: Gender, Age, Race

Industry SMOTE with 97.4% retention

Convergence achieved in single iteration

Phase 4: Results Generation
text
Mitigated Dataset → Statistical Validation → Visualization → Report Generation
COMPAS Output:

Final bias score: 0.3139 (5.6% reduction)

Feature improvements documented

Professional visualizations created

🎯 Domain-Specific Architecture
Justice Domain (COMPAS Validated)
Evidence Base:

Ministry of Justice disparity statistics

HM Inspectorate reports

Sentencing Council analyses

Technical Implementation:

python
class JusticeBiasClean(BiasClean):
    def __init__(self):
        self.weights = JUSTICE_WEIGHTS
        self.metrics = ['recidivism_parity', 'error_balance', 'predictive_equality']
        self.constraints = {'max_modification': 0.05, 'retention_threshold': 0.92}
Health Domain Architecture
Evidence Base: NHS Digital, Public Health England disparities

Technical Implementation:

python
class HealthBiasClean(BiasClean):
    def __init__(self):
        self.weights = HEALTH_WEIGHTS  # Emphasis: Ethnicity, Disability
        self.metrics = ['diagnostic_parity', 'treatment_equality', 'access_fairness']
Finance Domain Architecture
Evidence Base: FCA lending studies, Bank of England analyses

Technical Implementation:

python
class FinanceBiasClean(BiasClean):
    def __init__(self):
        self.weights = FINANCE_WEIGHTS  # Emphasis: SES, Region
        self.metrics = ['approval_parity', 'error_rate_balance', 'calibration_fairness']
🔬 Statistical Foundation
Outcome-Based Fairness
Methodology: Fisher's exact testing for recidivism prediction fairness

COMPAS Implementation:

python
def outcome_fairness_analysis(df, protected_feature, target='two_year_recid'):
    """
    Calculate outcome disparities using Fisher's exact test
    Returns: p-value, disparity ratio, effect size
    """
Multi-Objective Optimization
Constrained SMOTE Algorithm:

python
def industry_smote_with_constraints(X, y, protected_features, domain_weights):
    """
    Industry-grade SMOTE implementation with:
    - Domain weight constraints
    - Data retention guarantees
    - Feature correlation preservation
    """
Validation Framework
Statistical Rigor:

Pre/post mitigation significance testing

Effect size calculation for practical impact

Multiple comparison correction

Confidence interval reporting

🚀 Deployment Architecture
Web Interface (Flask)
python
# biasclean.py - Production web application
@app.route('/')
def upload_form():
    return render_template('upload_biasclean.html')

@app.route('/results', methods=['POST'])
def process_dataset():
    # Complete bias cleaning pipeline
    results = biasclean_full_pipeline(uploaded_file, selected_domain)
    return render_template('biasclean_result.html', results=results)
Production API
Endpoint: https://www.ai-fairness.com
Features:

No-code CSV upload and processing

7 domain selections with auto-detection

Real-time progress tracking

Professional visualization outputs

Batch Processing
python
# biasclean_pipeline.py - Industrial-scale processing
def biasclean_full_pipeline(input_path, domain, mode='industry'):
    """
    End-to-end bias cleaning for production use
    Returns: corrected DataFrame, comprehensive report, visualizations
    """
📈 Performance & Scalability
COMPAS Validation Metrics
Dataset Scale: 7,214 records, 53 features
Processing Time: < 2 minutes (standard hardware)
Memory Usage: ~13.1 MB peak
Bias Reduction: 5.6% overall with 97.4% retention

Scalability Characteristics
Linear scaling with dataset size

Constant memory per record processing

Parallelizable components for large datasets

Incremental processing support

Quality Assurance
Statistical validation at each pipeline stage

Data integrity checks throughout processing

Reproducible results with random state control

Comprehensive logging for audit trails

🔮 Architecture Evolution
v2.0 Current Implementation
Evidence-weighted multi-domain framework

COMPAS-validated justice domain

Industrial SMOTE with constraints

Production web interface

Future Roadmap
v2.1: AIF360 integration, expanded metrics

v2.2: Interactive visualization dashboard

v2.3: Real-time bias monitoring

v2.4: Certified auditing modules

📚 References
Ministry of Justice (2024) - Race and the Criminal Justice System

Equality and Human Rights Commission - UK Equality Act Guidance

ProPublica COMPAS Analysis - Methodology and Findings

NHS Digital - Health Inequality Statistics

Financial Conduct Authority - Fair Lending Guidelines

*BiasClean Toolkit v2.0.0 - Architecture Documentation*
COMPAS Validated: 5.6% Bias Reduction Achieved
