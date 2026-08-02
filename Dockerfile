# BiasClean — reproducible environment (Phase 4, Workstream E)
# Internal use only: no auth, no multi-tenancy, no external-facing
# deployment concerns (see Phase 4 SOP, Scope).

FROM python:3.9.6-slim

WORKDIR /app

# --- Dependencies first: an early, cacheable layer so rebuilds after a
# code-only change don't re-resolve dependencies (Workstream E design).
# requirements-dev.txt (aequitas, aif360) is intentionally NOT installed
# here — it's dev/benchmarking tooling, not a runtime dependency of the
# pipeline itself (see Workstream D / requirements-dev.txt).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Pipeline code
COPY biasclean_v3_5_1_terminal.py .

# --- Datasets: NOT baked into the image. The real Justice_Real Datasets/
# folder (NC alone is 4.87GB) is mounted as a volume at runtime instead —
# see the `docker run` usage note below.
# Small reference datasets can still be copied in if desired; left out
# here since Hamid's decision was to keep the container itself lean and
# mount data at run time regardless of size.

# --- Entrypoint: preserves the pipeline's existing interactive prompt.
# Per Hamid's decision, no non-interactive CLI mode is added — this
# container is meant to be run with `docker run -it`, exactly like the
# native venv experience today.
ENTRYPOINT ["python3", "biasclean_v3_5_1_terminal.py"]
