# Data acquisition ledger

All URLs verified working 2026-10-28 (UTC). Files are placed under `data_raw/`
and verified against `metadata/DATA_MANIFEST.csv` (bytes + sha256).

## LP GRS (Moon; elemental abundances)
`data_raw/lp_grs/`
- `https://pds-geosciences.wustl.edu/lunar/lp-l-grs-5-elem-abundance-v1/lp_9001/data/lpgrs_high1_elem_abundance_2deg.{tab,lbl}`
- `https://pds-geosciences.wustl.edu/lunar/lp-l-grs-5-elem-abundance-v1/lp_9001/data/lpgrs_high1_elem_abundance_5deg.{tab,lbl}`
- `https://pds-geosciences.wustl.edu/lunar/lp-l-grs-5-elem-abundance-v1/lp_9001/data/lpgrs_elem_abundance.fmt`
- `https://pds-geosciences.wustl.edu/lunar/lp-l-grs-5-elem-abundance-v1/lp_9001/data/aareadme.txt`
- The 5-deg files download lowercase (`lpgrs_high1_elem_abundance_5deg.tab`); the
  pipeline expects `LPGRS_HIGH1_ELEM_ABUNDANCE_5DEG.{TAB,LBL}` — copy/rename after download.

## ODY GRS (Mars; Th, K, WEH)
`data_raw/ody_grs/`
- `https://pds-geosciences.wustl.edu/ody/ody-m-grs-5-elements-v1/odgm_xxxx/data/unsmoothed/5x5/th_5x5.{tab,lbl}`
- `https://pds-geosciences.wustl.edu/ody/ody-m-grs-5-elements-v1/odgm_xxxx/data/unsmoothed/5x5/k_5x5.{tab,lbl}`
- `https://pds-geosciences.wustl.edu/ody/ody-m-grs-5-elements-v1/odgm_xxxx/data/smoothed/h2o_sr_5x5.{tab,lbl}`
- NOTE (2026-10-28): these six files were regenerated server-side in Sep 2026
  (PDS migration); byte size/hash differ from DATA_MANIFEST but the decoded
  cell values reproduce every canonical result (see PUBLIC_CODE_REPRODUCTION.md).

## LOLA DEMs (Moon; elevation, slope, roughness)
`data_raw/dem/`
- `https://imbrium.mit.edu/DATA/LOLA_GDR/CYLINDRICAL/IMG/LDEM_16.{IMG,LBL}`
- `https://imbrium.mit.edu/DATA/LOLA_GDR/CYLINDRICAL/IMG/LDSM_16.{IMG,LBL}`
- `https://imbrium.mit.edu/DATA/LOLA_GDR/CYLINDRICAL/IMG/LDRM_16.{IMG,LBL}`

## Mars DEM (streamed; not persisted by hash)
`scripts/02_spatial_join.py` reads it via
`/vsicurl/https://planetarymaps.usgs.gov/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif`

## Lunar geology (Unified Geologic Map v2)
`data_raw/moon_geol/`
- `https://asc-astropedia.s3.us-west-2.amazonaws.com/Moon/Geology/Unified_Geologic_Map_of_the_Moon_GIS_v2.zip`
  (unzip → `Unified_Geologic_Map_of_the_Moon_GIS/Lunar_GIS/Shapefiles/GeoUnits.shp`; the zip also contains a .gdb — not needed)

## Mars geology (SIM 3292)
`data_raw/mars_geol/`
- `https://pubs.usgs.gov/sim/3292/downloads/sim3292_database.zip`
  (unzip → `extracted/SIM3292_MarsGlobalGeologicGIS_20M/SIM3292_Shapefiles/SIM3292_Global_Geology.shp`)

## Mars paleolakes (Goudge et al. 2016)
`data_raw/mars_hydro/`
- `https://www.jsg.utexas.edu/goudge/files/Goudge_et_al_2016_Geology_CBL_OBL_Catalogue_CSV.zip`
  (unzip → `lakes_csv/Goudge_et_al_2016_Geology_CBL_OBL_Catalogue.csv`)
- `https://www.jsg.utexas.edu/goudge/files/Goudge_et_al_2016_Geology_CBL_OBL_Catalogue.zip`
  (unzip → `lakes_shp/` shapefiles; also extracts the CSV)
