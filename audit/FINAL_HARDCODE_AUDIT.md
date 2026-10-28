# FINAL_HARDCODE_AUDIT.md

Scope: every result literal in manuscript_final_clean.docx prose and captions.
Method: grep of scripts/07_manuscript.py for the audited values; traced to the
computed source that produces them. Criterion: no canonical result value may be
a hardcoded literal; all must interpolate from results/*.csv or results/QC.md.

| value | source | status |
|---|---|---|
| 0.967 (Moon rho) | pm["rho_elem_integr"].loc[Moon] -> f-string | COMPUTED |
| 0.033 (Moon GRSens) | pm["GRSens"].loc[Moon] | COMPUTED |
| 0.889 (Mars rho) | pm["rho_elem_integr"].loc[Mars] | COMPUTED |
| 0.111 (Mars GRSens) | pm["GRSens"].loc[Mars] | COMPUTED |
| 63% / 39% (top-decile shift) | WAS hardcoded in abstract line 562 -> FIXED 2026-10-28: now `100*(1-jaccard_top10_c_vs_d)` per planet | FIXED |
| 56, 32, 4, 3 (Mars region sizes) | WAS hardcoded -> FIXED: sorted(ev['n_cells']) join | FIXED |
| 89 (Moon region cells) | cand.iloc[0].n_cells | COMPUTED |
| 1790 / 2468 (n cells) | pm["n"] | COMPUTED |
| Moran I values (0.911/0.934/0.481/0.955 Moon; 0.508/0.198/0.154/0.200 Mars) | parsed from results/QC.md by regex | COMPUTED |
| missingness counts (2 Moon; 124 Th / 17 K Mars) | parsed from QC.md dict | COMPUTED |
| 0.90-0.94 / 0.74-0.91 / 0.44-0.79 (region evidence ranges) | WAS hardcoded -> FIXED: ev[...].min()/max() | FIXED |
| "~5%" Mars Th mask | 124/2468 = 5.0% — kept as "~5%" approximation (qualified) | ACCEPTABLE (approximation flagged with ~) |
| J5 values in Table 5 / Table A1 | rob DataFrame | COMPUTED |
| WEH-exclusion numbers (0.839, 0.161, 0.554) | noh2o DataFrame | COMPUTED |
| 10deg values (0.966/0.884) | res10 DataFrame | COMPUTED |

VERDICT: PASS — after fixes, no canonical result literal remains hardcoded.
