# Datasets Used — Justice Domain Validation

Real datasets used in the Phase 2 external validation (see `/Validations/BiasClean_External_Validation_Justice_Domain.pdf`). Where a dataset is small enough for GitHub's 25MB file limit, the exact file used is included in this folder; where it isn't, a link to the official source is provided instead so results can be independently reproduced.

| Dataset | Rows | In this folder? | Official source |
|---|---|---|---|
| COMPAS (ProPublica) | 7,214 | ✅ `compas-scores-two-years.csv` | [propublica/compas-analysis](https://github.com/propublica/compas-analysis) |
| NIJ Recidivism Forecasting Challenge 2021 | 25,835 | *(add your local copy)* | [NIJ's Recidivism Challenge Full Dataset](https://data.ojp.usdoj.gov/Courts/NIJ-s-Recidivism-Challenge-Full-Dataset/ynf5-u8nk), data.ojp.usdoj.gov |
| UCI Communities and Crime | 1,994 | *(add your local copy)* | [UCI ML Repository #183](https://archive.ics.uci.edu/dataset/183/communities+and+crime) |
| North Carolina statewide traffic stops | 20,286,645 | ❌ too large (~4.9GB, exceeds GitHub's 25MB limit even compressed) | [Stanford Open Policing Project](https://openpolicing.stanford.edu/data) |
| Oklahoma City traffic stops | 945,107 | ❌ too large even compressed | [Stanford Open Policing Project](https://openpolicing.stanford.edu/data) |

For the two Stanford Open Policing Project datasets, cite: Pierson, E., Simoiu, C., Overgoor, J., Corbett-Davies, S., Jenson, D., Shoemaker, A., Ramachandran, V., Barghouty, P., Phillips, C., Shroff, R., & Goel, S. (2020). A large-scale analysis of racial disparities in police stops across the United States. *Nature Human Behaviour*, 4, 736–745.

`opafy25nid.csv` (the 6th dataset attempted in Phase 2) is not listed here — its source was never identified and it was excluded from the validation entirely; see the Phase 2 report for details.
