#!/usr/bin/env python3
"""05_tables.py — write main + supplementary tables as CSV."""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAB, RES = ROOT/"tables", ROOT/"results"
TAB.mkdir(exist_ok=True)

t1 = pd.DataFrame([
 ["Moon","U,Th,K,FeO,TiO2,oxides","Lunar Prospector GRS/NS (high-alt.)","LP-L-GRS-5-ELEM-ABUNDANCE-V1.0","5° equal-area bins","global"],
 ["Moon","Elevation, slope, roughness","LRO LOLA GDR","LRO-L-LOLA-4-GDR-V1.0 (LDEM/LDSM/LDRM_16)","16 px/deg (~1.9 km)","global"],
 ["Moon","Geologic units","USGS Unified Geologic Map of the Moon v2","Fortezzo et al. 2020","1:5,000,000 polygons","global"],
 ["Mars","Th, K, H2O, K/Th","2001 Mars Odyssey GRS","ODY-M-GRS-5-ELEMENTS-V1.0, DOI:10.17189/1519480","5°×5° bins","|lat| ≲ 87.5°, Th masked ~5%"],
 ["Mars","Geologic units & age","USGS Geologic Map of Mars","Tanaka et al. 2014, SIM 3292","1:20,000,000 polygons","global"],
 ["Mars","Elevation (slope, roughness)","MGS MOLA + MEX HRSC blend DEM","Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2","200 m/px (read at 1/64 overview)","global"],
 ["Mars","Paleolakes","UT Austin shared data","Goudge et al. 2016, Geology 44:419","point catalog (n=... see CSV)","global catalog"],
], columns=["planet","layer","mission/instrument","product","native support","coverage"])
t1.to_csv(TAB/"table1_datasets.csv", index=False)

# Table 2 = evidence dictionary copy
pd.read_csv(ROOT/"metadata/EVIDENCE_DICTIONARY.csv").to_csv(TAB/"table2_evidence.csv", index=False)

pd.read_csv(RES/"primary_metrics.csv").rename(columns={"Unnamed: 0":"planet"}).to_csv(TAB/"table3_metrics.csv", index=False)
pd.read_csv(RES/"candidate_regions.csv").to_csv(TAB/"table4_candidate_regions.csv", index=False)
pd.read_csv(RES/"robustness.csv").to_csv(TAB/"table5_robustness.csv", index=False)
print("tables written")
