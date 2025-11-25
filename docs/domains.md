# 🧩 BiasClean Toolkit - Domain Specifications

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](https://www.apache.org/licenses/LICENSE-2.0)

This document details the seven UK domains supported by BiasClean™, their evidence-based weighting matrices, and domain-specific implementation guidelines.

---

## 🌍 Overview

BiasClean operates on a sophisticated 7×7 matrix of UK domains and universal fairness features. Each domain employs evidence-based weights derived from official UK statistics, regulatory guidance, and structural inequality patterns.

**COMPAS Validation:** The Justice domain has been validated with **5.6% bias reduction** on real-world data.

---

## ⚖️ 1. Justice Domain

### 🎯 Domain Focus
Criminal justice risk assessments, sentencing data, policing outcomes, and recidivism predictions.

### 📊 Evidence Base
- **Ministry of Justice:** Race and Criminal Justice System statistics
- **HM Inspectorate of Constabulary:** Policing disparity reports  
- **Sentencing Council:** Demographic analysis of sentencing outcomes
- **ProPublica COMPAS:** Recidivism algorithm fairness analysis

### ⚙️ Weight Matrix
```python
JUSTICE_WEIGHTS = {
    'Ethnicity': 0.25,        # Strongest structural disparity evidence
    'Race': 0.25,             # Documented systemic bias in CJS
    'SocioeconomicStatus': 0.20, # Deprivation and justice system interaction
    'Region': 0.15,           # Geographic policing and sentencing variations
    'Age': 0.15,              # Youth justice and behavioral gradient impacts
    'MigrationStatus': 0.10,  # Foreign national and migrant disparities
    'DisabilityStatus': 0.10, # Vulnerability and access to justice issues
    'Gender': 0.05            # Documented but relatively lower impact
}
✅ COMPAS Validation Results
Overall Bias Reduction: 5.6% (0.3325 → 0.3139)

Feature Improvements:

Gender: 49.5% improvement

Race: 11.4% improvement

Ethnicity: 11.4% improvement

Data Retention: 97.4% (7,214 → 7,029 records)

🚀 Use Cases
Recidivism prediction training data

Policing outcome analysis

Sentencing recommendation systems

Probation and parole assessments

🏥 2. Health Domain
🎯 Domain Focus
Healthcare access, diagnostic outcomes, treatment allocation, and clinical risk predictions.

📊 Evidence Base
NHS Digital: Health inequality statistics

Public Health England: Disparity reports

MHRA: Medical device bias guidelines

Clinical commissioning group data

⚙️ Weight Matrix
python
HEALTH_WEIGHTS = {
    'Ethnicity': 0.25,        # Significant health outcome disparities
    'SocioeconomicStatus': 0.20, # Strong deprivation-health linkage
    'DisabilityStatus': 0.15,  # Healthcare access and outcome disparities
    'Gender': 0.15,           # Diagnostic and treatment gender gaps
    'Region': 0.10,           # Regional healthcare resource variations
    'Age': 0.10,              # Age-based treatment and access issues
    'MigrationStatus': 0.05,  # Migrant health access challenges
    'Race': 0.00              # Covered under ethnicity in health context
}
🚀 Use Cases
Diagnostic AI training data

Treatment prioritization systems

Healthcare resource allocation

Clinical trial participant selection

💰 3. Finance Domain
🎯 Domain Focus
Credit scoring, loan approvals, insurance risk assessment, and financial service access.

📊 Evidence Base
Financial Conduct Authority: Fair lending studies

Bank of England: Financial inclusion research

FCA Consumer Duty: Regulatory requirements

UK Finance industry data

⚙️ Weight Matrix
python
FINANCE_WEIGHTS = {
    'SocioeconomicStatus': 0.30, # Primary driver of financial exclusion
    'Region': 0.20,           # Geographic lending and insurance variations
    'Ethnicity': 0.20,        # Documented lending disparities
    'Age': 0.10,              # Age-based credit and insurance pricing
    'Gender': 0.10,           # Gender-based financial product differences
    'DisabilityStatus': 0.05, # Disability income and financial access
    'MigrationStatus': 0.05,  # Migrant banking and credit access
    'Race': 0.00              # Covered under ethnicity in finance context
}
🚀 Use Cases
Credit scoring model training

Loan application processing

Insurance risk assessment

Financial product recommendation systems

🎓 4. Education Domain
🎯 Domain Focus
Student admissions, academic outcomes, resource allocation, and educational attainment predictions.

📊 Evidence Base
Department for Education: Attainment gap statistics

Office for Students: Access and participation data

Sutton Trust: Social mobility research

Education Policy Institute analyses

⚙️ Weight Matrix
python
EDUCATION_WEIGHTS = {
    'SocioeconomicStatus': 0.25, # Strongest predictor of educational outcomes
    'Ethnicity': 0.20,        # Significant attainment gaps by ethnicity
    'DisabilityStatus': 0.15,  # Special educational needs and accessibility
    'Region': 0.15,           # Regional funding and resource variations
    'Gender': 0.10,           # Subject and attainment gender differences
    'Age': 0.10,              # Age-stage appropriate interventions
    'MigrationStatus': 0.05,  # EAL and migrant student support
    'Race': 0.00              # Covered under ethnicity in education context
}
🚀 Use Cases
University admissions algorithms

Student performance predictions

Educational resource allocation

Special educational needs assessments

💼 5. Hiring Domain
🎯 Domain Focus
Recruitment screening, promotion decisions, pay equity, and career progression predictions.

📊 Evidence Base
Equality and Human Rights Commission: Employment discrimination data

ONS Gender Pay Gap: Mandatory reporting statistics

ACAS: Workplace equality guidance

Industry diversity reports

⚙️ Weight Matrix
python
HIRING_WEIGHTS = {
    'Gender': 0.20,           # Significant pay and progression gaps
    'Ethnicity': 0.25,        # Employment and pay ethnicity disparities
    'DisabilityStatus': 0.15,  # Disability employment and pay gaps
    'Age': 0.10,              # Age discrimination in hiring
    'SocioeconomicStatus': 0.15, # Social background and career progression
    'Region': 0.10,           # Regional employment opportunity variations
    'MigrationStatus': 0.05,  # Migrant employment barriers
    'Race': 0.00              # Covered under ethnicity in employment context
}
🚀 Use Cases
CV screening algorithms

Recruitment shortlisting systems

Promotion recommendation engines

Pay equity analysis

🏢 6. Business Domain
🎯 Domain Focus
Customer service outcomes, marketing targeting, product recommendations, and business analytics.

📊 Evidence Base
Department for BEIS: Business disparity research

British Business Bank: SME diversity analysis

Industry consumer protection data

Market research findings

⚙️ Weight Matrix
python
BUSINESS_WEIGHTS = {
    'Ethnicity': 0.25,        # Market access and service outcome disparities
    'Gender': 0.20,           # Gender-based marketing and service differences
    'Region': 0.15,           # Regional market variations
    'SocioeconomicStatus': 0.15, # Customer value and service tiering
    'Age': 0.10,              # Age-based product and service targeting
    'DisabilityStatus': 0.10,  # Accessibility and service adaptation
    'MigrationStatus': 0.05,  # Migrant consumer access
    'Race': 0.00              # Covered under ethnicity in business context
}
🚀 Use Cases
Customer segmentation algorithms

Service outcome predictions

Marketing campaign targeting

Product recommendation systems

🏛️ 7. Governance Domain
🎯 Domain Focus
Public service access, benefit eligibility, civic participation, and government resource allocation.

📊 Evidence Base
Office for National Statistics: Public service usage data

Electoral Commission: Voter participation statistics

Government Equalities Office: Public sector equality data

Local authority service data

⚙️ Weight Matrix
python
GOVERNANCE_WEIGHTS = {
    'Ethnicity': 0.25,        # Public service access disparities
    'Gender': 0.20,           # Gender-based service usage variations
    'Region': 0.15,           # Regional service provision differences
    'SocioeconomicStatus': 0.15, # Benefit uptake and service access
    'MigrationStatus': 0.10,  # Migrant access to public services
    'DisabilityStatus': 0.10,  # Disability service adaptations
    'Age': 0.05,              # Age-based service eligibility
    'Race': 0.00              # Covered under ethnicity in governance context
}
🚀 Use Cases
Benefit eligibility systems

Public service recommendation engines

Civic engagement platforms

Government resource allocation algorithms

🔬 Methodology Notes
Weight Assignment Framework
All domain weights follow the SIW-ESW-PLW framework:

Structural Inequality Weight (SIW): Systemic impact severity

Evidence Strength Weight (ESW): Data robustness and consistency

Policy & Legal Relevance Weight (PLW): Regulatory alignment

Domain Adaptation
Weights are dynamically adjustable based on:

Dataset characteristics

Regional specificities

Temporal evidence updates

Organizational risk appetite

Validation Requirements
Each domain implementation requires:

Statistical significance testing

Real-world impact assessment

Domain expert validation

Legal compliance review

📊 Performance Summary
Justice Domain (COMPAS Validated):

✅ 5.6% overall bias reduction

✅ 97.4% data retention

✅ Multi-feature improvement demonstrated

✅ Statistical significance proven (p < 0.000000)

Other Domains:

🔄 Ready for similar validation studies

🔄 Evidence-based weight matrices implemented

🔄 Production pipelines available

🔄 Web interface integration complete

📚 Evidence Sources
Ministry of Justice (2024) - Disparity Analysis

NHS Digital - Health Inequalities Dataset

Financial Conduct Authority - Fair Lending Review

Department for Education - Attainment Gap Report

Equality and Human Rights Commission - Employment Statistics

Office for National Statistics - Census and Survey Data

*BiasClean Toolkit v2.0.0 - Domain Specifications*
*Justice Domain: COMPAS-Validated with 5.6% Bias Reduction*
