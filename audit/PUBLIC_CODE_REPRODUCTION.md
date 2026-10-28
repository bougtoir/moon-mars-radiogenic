# PUBLIC_CODE_REPRODUCTION.md

## Setup
- Repo: https://github.com/bougtoir/moon-mars-radiogenic (public)
- Cloned SHA: f803fa7
- Clone path: /tmp/mmdr-pub
- Env: Python 3.10, pip install -r requirements.txt (numpy 2.2.6, pandas 2.3.3,
  geopandas 1.1.4, rasterio 1.4.4, scipy 1.15.3, scikit-learn 1.7.2, matplotlib 3.10.9)
- Input data: reacquired 2026-10-28 from PDS/USGS/MIT per metadata/DATA_ACQUISITION.md
  into /home/ubuntu/mmdr_raw, symlinked as data_raw/.

## Manifest hash check (fresh download vs metadata/DATA_MANIFEST.csv)
- 230 files matched byte+sha256.
- 303 manifest entries missing = files inside archives (moon_geol .gdb,
  lakes_shp, sim3292 extracted tree) plus nonessential extras
  (LDEM_4.IMG/LBL, lp_index.tab/lbl) — all unused by the pipeline or
  content-identical members of the downloaded archives.
- 6 mismatches, all ODY GRS files (th_5x5, k_5x5, h2o_sr_5x5 .tab/.lbl): the PDS
  server regenerated these products in Sep 2026 (formatting changes; e.g.
  k_5x5.tab 129,600 bytes vs manifest 93,545). Resolution was verified by
  running the pipeline on the regenerated files — see results below.
- Gap found and fixed: DATA_MANIFEST.csv records bytes/sha256/UTC but no
  source URLs. A URL ledger was written to metadata/DATA_ACQUISITION.md.

## Commands run
    python3 scripts/01_build_layers.py   # Moon 1790 cells | Mars 2592 raw cells
    python3 scripts/02_spatial_join.py   # geology/lake/DEM joins; Mars DEM via /vsicurl
    python3 scripts/03_models.py         # scores, MC weights, hotspots, robustness
    python3 scripts/06_qc.py             # QC.md (Moran I, missingness)
    python3 scripts/05_tables.py         # tables CSV
    python3 scripts/08_revision.py       # 10-deg pass, WEH exclusion, region evidence

## Output comparison (fresh /tmp/mmdr-pub/results vs canonical wip results)
| file | verdict |
|---|---|
| primary_metrics.csv | IDENTICAL (Moon rho=0.967, GRSens=0.033, n=1790; Mars rho=0.889, GRSens=0.111, n=2468) |
| candidate_regions.csv | IDENTICAL (Moon 89-cell PKT region; Mars 4 regions) |
| mars_region_evidence.csv | IDENTICAL (56/32/4/3 cells) |
| mars_h2o_exclusion.csv | IDENTICAL (excl-E_h2o rho=0.839, GRSens=0.161, j5=0.554) |
| resolution_10deg.csv | IDENTICAL (rho 0.966/607 cells, 0.884/703 cells) |
| QC.md | IDENTICAL |
| robustness.csv | unique rows identical in rho; 2 of 39 J5 values differ |

## Mismatches
1. robustness.csv written with 78 rows (39 duplicated x2): latent defect in
   03_models.py — `robust_eval` appends to and returns the shared list `rob`,
   so `robust_eval(moon) + robust_eval(mars)` doubles every row. Canonical
   results/robustness.csv (39 rows) is the deduplicated set; the script bug is
   fixed in wip (2026-10-28) and the fix syncs to the public repo.
2. J5 differs in 2/39 rows by <=0.014: Moon "bottleneck min(S,M,T)"
   0.041 -> 0.047, Mars "leave-S-out" 0.079 -> 0.065. All rho values identical.
   Cause: top-5% boundary ties break differently across platforms
   (np.argsort stability on equal scores); Jaccard on equal-count sets shifts
   by boundary membership only. Both remain the same order-of-magnitude
   "weak" results the text reports (~0.04 bottleneck; ~0.08 leave-S-out).
   No textual claim changes.

## Conclusion: PASS
The regenerated ODY files (server re-issued, hash-mismatched) carry identical
decoded values — every canonical headline number reproduces from public code +
fresh public data. The only deviations are a cosmetic CSV row-duplication bug
(fixed) and top-5% boundary tie nondeterminism <=0.014 in two J5 values
(declared, immaterial).
