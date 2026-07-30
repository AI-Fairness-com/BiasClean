# Datasets Used — Justice Domain Validation

Real datasets used in the Phase 2 external validation (see `/Validations/BiasClean_External_Validation_Justice_Domain.pdf`). Where a dataset is small enough for GitHub's 25MB file limit, the exact file used is included in this folder (`data/real_datasets/Justice_Real Datasets/`); where it isn't, a link to the official source is provided instead so results can be independently reproduced.

| Dataset | Rows | In this folder? | Official source |
|---|---|---|---|
| COMPAS (ProPublica) | 7,214 | ✅ `compas_dataset.csv` | [propublica/compas-analysis](https://github.com/propublica/compas-analysis) |
| NIJ Recidivism Forecasting Challenge 2021 | 25,835 | ✅ `nij-challenge2021_full_dataset.csv` | [NIJ's Recidivism Challenge Full Dataset](https://data.ojp.usdoj.gov/Courts/NIJ-s-Recidivism-Challenge-Full-Dataset/ynf5-u8nk), data.ojp.usdoj.gov |
| UCI Communities and Crime | 1,994 | ✅ `communities_prepared.csv` | [UCI ML Repository #183](https://archive.ics.uci.edu/dataset/183/communities+and+crime) |
| North Carolina statewide traffic stops | 20,286,645 | ❌ too large (~4.9GB, exceeds GitHub's 25MB limit even compressed) | [Stanford Open Policing Project](https://openpolicing.stanford.edu/data) |
| Oklahoma City traffic stops | 945,107 | ❌ too large even compressed | [Stanford Open Policing Project](https://openpolicing.stanford.edu/data) |
| `opafy25nid.csv` | 66,662 | ⚠️ `opafy25nid.csv.zip` — included for transparency, NOT validated | Source unidentified |

For the two Stanford Open Policing Project datasets, cite: Pierson, E., Simoiu, C., Overgoor, J., Corbett-Davies, S., Jenson, D., Shoemaker, A., Ramachandran, V., Barghouty, P., Phillips, C., Shroff, R., & Goel, S. (2020). A large-scale analysis of racial disparities in police stops across the United States. *Nature Human Behaviour*, 4, 736–745.

**A note on `opafy25nid.csv`:** this is the 6th dataset attempted in Phase 2, included in this folder for transparency rather than omitted, but it was **not validated** and its results should not be relied upon. Its source and data dictionary were never identified (66,662 rows × 22,149 columns, cryptic administrative column codes like `POOFFICE`, `SORGDL`, and a wide repeated-measures structure — `TTSC1_1` through `TTSC1_111`) despite a targeted search for the filename and column names. Auto-detection could map only one column (`AGE`) to any recognizable protected feature across all 22,149 columns, and the pipeline correctly declines to treat any result from this file as meaningful. See Section 4 of the Phase 2 report for the full explanation of why this dataset was excluded.
