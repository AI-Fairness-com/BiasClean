# BiasClean v2.0

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.7%2B-green)
![License](https://img.shields.io/badge/license-CC--BY--NC--SA--4.0-lightgrey)

### A domain-aware pre-processing toolkit for detecting and mitigating demographic bias in UK datasets before modelling.

BiasClean v2.0 is an evidence-based fairness cleaning engine designed to remove demographic representation bias with the same rigour traditionally applied to dirty or missing data.  
It provides a transparent, defensible, multi-domain weighting framework aligned with UK structural inequality patterns and regulatory expectations.

---

## 🎯 Key Capabilities

- **7 UK Domains:** Justice, Health, Finance, Education, Hiring, Business, Governance  
- **7 Universal Fairness Features:** Ethnicity, SocioeconomicStatus, Region, Age, Gender, DisabilityStatus, MigrationStatus  
- **Domain-Specific Weights:** Evidence-based 7×7 matrix constructed from ONS, NHS, MoJ, FCA, DfE, EHRC, BEIS sources  
- **Representation-Ratio Fairness Scoring:** Detects under- and over-representation patterns  
- **Selective Downsampling:** Controlled bias reduction (typical data loss 8–15%)  
- **Regulatory-Grade Transparency:** Clear audit trail, justification and evidence base  
- **Report Generation:** Before/after fairness comparisons for governance and audit

---

## 🔍 Why BiasClean Is Different

- **UK-aligned design:** Uses national statistics, regulatory guidance and structural inequality research  
- **Domain specificity:** Not a generic fairness tool; each domain has its own evidence-weighted feature profile  
- **Reproducible methodology:** Transparent SIW–ESW–PLW weighting framework  
- **Audit ready:** Designed for peer review and compliance teams  
- **No black box steps:** Every weight, feature and fairness measure is visible and explainable  
- **Robust feature architecture:** Seven fairness features validated in Step 1 & Step 2 technical reports  

---

## 📚 Regulatory Alignment

BiasClean supports UK requirements for transparency and fairness:

- Equality Act 2010 (protected characteristics)
- MoJ disparity monitoring (Race & CJS)
- NHS health inequality frameworks
- FCA fairness in lending and financial inclusion expectations
- DfE attainment inequality frameworks
- EHRC systemic inequality guidance
- BEIS business equity and investment disparity studies

These sources collectively inform the domain-specific weighting logic and fairness feature architecture.

---

## 📦 Installation

```bash
pip install biasclean_v2
