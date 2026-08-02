# BiasClean — Docker Setup

This note documents how to build and run BiasClean in Docker, and captures a few
setup issues hit during Phase 4 (Workstream E) so they don't need to be
rediscovered from scratch later.

## Prerequisites

- Docker Desktop installed and running (the background whale-icon process
  must be up before any `docker` command will work).
- The three files below present together at the repo root:
  `Dockerfile`, `.dockerignore`, `requirements.txt`.
- The `Justice_Real Datasets/` folder present locally (not committed to the
  repo — GitHub's size limits mean the large files, e.g. North Carolina at
  4.87GB, are never checked in; see `data/real_datasets` README for sourcing).

## Build

From the repo root:

```bash
docker build -t biasclean:3.10.1 .
```

Only needs re-running if `Dockerfile` or `requirements.txt` change. Ordinary
code edits to `biasclean_v3_5_1_terminal.py` also require a rebuild (it's
copied into the image, not mounted), but this rebuilds fast since the
dependency-install layer is cached separately.

## Run

The container's entrypoint preserves the pipeline's interactive terminal
prompt — this was a deliberate decision (no non-interactive `--file`/`--mode`
CLI flags were added in Phase 4). Run it with `-it` and two volume mounts:
one for your datasets, one so `biasclean_results/` (reports, audit trails)
lands back on your Mac instead of disappearing when the container exits.

```bash
docker run -it \
  -v "/path/to/BiasClean_V3_API/Justice_Real Datasets:/app/Justice_Real Datasets" \
  -v "/path/to/BiasClean_V3_API/biasclean_results:/app/biasclean_results" \
  biasclean:3.10.1
```

Inside the container, dataset paths are entered exactly as they'd normally be
typed at the pipeline's prompt, e.g.:

```
Justice_Real Datasets/nc_statewide_2020_04_01.csv
```

## Memory allocation (important for North Carolina)

Docker Desktop's default memory limit (often 8GB) is **not enough** to load
North Carolina's 20.3-million-row file — the raw DataFrame alone occupies
roughly 22GB in memory before any rebalancing step even begins. Attempting
NC at a low memory limit will kill the container with exit code `137`
(Docker's out-of-memory signal), not a Python error.

Fix: **Docker Desktop → Settings → Resources → Advanced → Memory limit.**
On a 36GB-RAM machine, raising this to ~30GB (leaving headroom for macOS
itself) was sufficient — actual peak usage observed was ~26–29GB. If your
machine has less total RAM, scale down proportionally, but Communities &
Crime / COMPAS / OK City / NIJ (all well under 1M rows) run comfortably even
at Docker's default allocation — only NC needs this adjustment.

**SVM fairness enforcement must stay disabled for North Carolina**,
regardless of environment (native venv or Docker) — this has been a
documented constraint since Phase 1/2 due to the added memory burden SVM
training places on top of an already-large dataset.

## Known gotcha: dotfiles and GitHub's web upload

If uploading `.dockerignore` via GitHub's drag-and-drop web UI, check that it
actually lands as `.dockerignore` (with the leading dot) and not `dockerignore`
— the upload interface can silently strip the leading dot. Docker only
recognizes the file with the dot present; without it, it has no effect at
all, silently. If this happens, the fix is to open the file on GitHub, use
the edit (pencil) icon, and change the filename field directly rather than
re-uploading.

## Validation record

All 5 established datasets were run inside `biasclean:3.10.1` and reproduced
their on-record `bias_scores` exactly (see `docs/CHANGELOG.md`, entry
`[3.10.2]`, for the full figures): Communities & Crime, COMPAS, Oklahoma
City, NIJ, and North Carolina.
