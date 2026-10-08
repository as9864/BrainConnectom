# CLAUDE.md

Cross-species transferability of connectome wiring principles (C. elegans + Drosophila → human), split out of the BrainConnectom repo's `sc_prior_experiment`. Start with `README.md`; the full rationale, hypotheses (H1–H3), methods and current results live in `docs/methodology_transferability.md`.

## Running

- Python 3.12+ (`requirements.txt` pins need it). Run everything from this folder: `python -m sctransfer.<module>`.
- Main analysis: `python -m sctransfer.run_transfer --human hcp_group` (~4 min; downloads ENIGMA HCP CSVs into `data/hcp_enigma/raw/` on first run). `--density 0.04` for the density-matched sensitivity run.
- There is no test suite; verify changes by re-running `run_transfer` / `run_pilot` and comparing against the numbers recorded in `docs/methodology_transferability.md`.

## Conventions

- User-facing docs are written in Korean; code, docstrings and commit messages in English.
- All cross-species comparisons use null-normalized statistics on binarized graphs (`normalized.py`); never compare raw values across species.
- Transfer index is only reported when the oracle reliably and non-negligibly beats the null (`_print_ti` in `run_transfer.py`).
- When reading result CSVs with pandas, pass `keep_default_na=False` — the condition label `null` is otherwise parsed as NaN.

## Data rules

- HCP data (group or individual) is under the HCP Open Access Data Use Terms: never commit HCP-derived matrices (`data/hcp_enigma/raw/`, `data/hcp/` are gitignored). Individual subjects are provided by the user (`docs/hcp_data_guide.md`).
- `data/hemibrain/circuits/` is committed (CC BY 4.0) and reproducible with `python -m sctransfer.hemibrain --build`.
- Cite data sources as listed in each `data/*/README.md`.

## Current status

- Part 1 (descriptive) done on real HCP group SC: direction conserved for all four principles; only modularity transfers quantitatively; degree heterogeneity does not.
- Part 2 (FC→SC utility) only validated on the synthetic cohort; blocked on per-subject HCP SC/FC pairs.
- Paper draft in `docs/paper/` still uses the original (pre-pivot) framing.
