# Data Provenance — moon-mars-radiogenic

All data retrieved 2026-09-26 (UTC). All files are public NASA PDS / USGS / publisher-shared products; no authentication or license restrictions apply beyond citation norms. Raw snapshots are stored under `data_raw/`; nothing was kept only in memory or in `/tmp` — see per-file SHA-256 in `metadata/DATA_MANIFEST.csv`.

## Lunar

| Layer | Source | Product | Path |
|---|---|---|---|
| U, Th, K, FeO, TiO2, MgO, Al2O3, SiO2, CaO (+ full error matrix) | Lunar Prospector GRS+NS, high-altitude (100 km) | LP-L-GRS-5-ELEM-ABUNDANCE-V1.0, `LPGRS_HIGH1_ELEM_ABUNDANCE_{2,5}DEG.TAB` (Prettyman et al. 2006 products; PDS3 archive assembled 2012, migrated 2021) | `data_raw/lp_grs/` |
| Elevation, slope, roughness | LRO LOLA GDR (LDEM/LDSM/LDRM, 16 px/deg, 4 px/deg) | LRO-L-LOLA-4-GDR-V1.0 via MIT PDS mirror `imbrium.mit.edu/DATA/LOLA_GDR/CYLINDRICAL/IMG/` | `data_raw/dem/` |
| Geologic units | USGS Unified Geologic Map of the Moon v2, 1:5M (Fortezzo, Spudis & Harrel 2020) | `Unified_Geologic_Map_of_the_Moon_GIS_v2.zip` (GeoUnits.shp) | `data_raw/moon_geol/` |

## Mars

| Layer | Source | Product | Path |
|---|---|---|---|
| Th, K, H2O, K/Th (5x5 deg bins + smoothed) | 2001 Mars Odyssey GRS | ODY-M-GRS-5-ELEMENTS-V1.0, DOI 10.17189/1519480 (Boynton et al. 2007; June 2002–April 2005 data, CO2-frost corrected) | `data_raw/ody_grs/` |
| Geologic units (age + unit class) | USGS Geologic Map of Mars, 1:20M (Tanaka et al. 2014, SIM 3292) | `sim3292_database.zip` → `SIM3292_Global_Geology.shp` | `data_raw/mars_geol/` |
| Elevation → slope, roughness | MGS MOLA + MEX HRSC blended DEM, global 200 m/px v2 | `Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif` read remotely via GDAL `/vsicurl` overview levels | streamed (not stored; CRS ESRI:104971) |
| Paleolakes (open- and closed-basin) | Goudge et al. 2016, Geology 44:419 | `Goudge_et_al_2016_Geology_CBL_OBL_Catalogue` CSV + shapefile, UT Austin shared-data page | `data_raw/mars_hydro/` |

## Documented substitutions / unavailability

- **Valley networks**: global machine-readable mapping (Hynek et al. 2010; Alemanno et al. 2018) could not be downloaded (publisher SI blocked / no public file found at reasonable effort). Compensated by geologic-map fluvial/sedimentary units + paleolake catalog + GRS H2O. Recorded as a coverage limitation in `EVIDENCE_DICTIONARY.csv`.
- **CRISM hydrated minerals**: no global machine-readable detection catalog obtainable; folded into discussion + evidence dictionary as unobserved (contributes to knowledge-gap map, not scored 0).
- **Kaguya/SELENE GRS U map**: LP GRS U (2°/5° bins) used as the primary lunar source layer; Kaguya product cited but not required since LP provides U at the analysis support.
- **Chloride deposits (Osterloo et al.)**: no machine-readable catalog obtained; noted as limitation.
