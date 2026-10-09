# moon-mars-radiogenic

From elemental abundance to exploration priority: radiogenic-resource prospectivity on the Moon and Mars — a preregistered, fully reproducible cross-planet prospectivity framework.

## Layout
- `docs/` — protocol (frozen v1), novelty assessment, method decisions, claim calibration, journal positioning, references, limitations, hostile review, final audit, handoff.
- `metadata/` — DATA_PROVENANCE.md, DATA_MANIFEST.csv (sha256 of every raw file), EVIDENCE_DICTIONARY.csv.
- `scripts/01…07_*.py` — end-to-end pipeline: acquire→layers→models→figures→tables→QC→manuscript.
- `data_raw/` — raw mission data (NOT in git; 2.4 GB; recover from manifest URLs + checksums).
- `data_interim/`, `data_processed/` — harmonised 5° equal-area cell tables.
- `results/` — primary metrics, candidate regions, robustness battery, QC diagnostics.
- `figures/`, `tables/` — Figures 1–7 + supplemental context map; Tables 1–5.
- `manuscript/` — manuscript_clean.docx, manuscript_inline_figures.docx; `supplement/supplement.docx`.
- `submission/` — journal-ready package.

## Reproduce
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
# restore data_raw/ per metadata/DATA_MANIFEST.csv, then:
.venv/bin/python scripts/01_build_layers.py
.venv/bin/python scripts/02_spatial_join.py
.venv/bin/python scripts/03_models.py
.venv/bin/python scripts/04_figures.py
.venv/bin/python scripts/05_tables.py
.venv/bin/python scripts/06_qc.py
.venv/bin/python scripts/07_manuscript.py
```

## Key constraints (protocol)
- Within-planet rank comparisons only; never cross-body absolute claims.
- Candidate regions are neutral prioritisation labels — no deposit/reserve/mineability claims.
- Negative results preserved and reported.
