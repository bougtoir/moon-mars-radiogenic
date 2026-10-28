#!/usr/bin/env python3
"""01_build_layers.py — parse raw products into cell-level layer tables.

Outputs:
  data_interim/moon_cells_raw.csv  (LP 5deg equal-area bins)
  data_interim/mars_cells_raw.csv  (ODY 5x5 deg bins)
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data_raw"
INT = ROOT / "data_interim"
INT.mkdir(exist_ok=True)

# ---------------- Lunar geochemistry (LP GRS, 5-deg equal-area bins) ----------------
# Columns per LPGRS_ELEM_ABUNDANCE.FMT:
# 0 pixel_index, 1-4 lat/lon bounds, 5 AM, 6 NEUTRON_DEN,
# 7 W_MGO,8 W_AL2O3,9 W_SIO2,10 W_CAO,11 TIO2,12 W_FEO,13 W_K,14 W_TH,15 W_U,
# 16..60 error-matrix upper triangle (9 params -> order i<=j, i,j in 0..8);
# E[8,8] = U variance is the LAST column (index 60).
lp = pd.read_csv(RAW / "lp_grs/LPGRS_HIGH1_ELEM_ABUNDANCE_5DEG.TAB",
                 sep=r"\s+", header=None)
lp = lp.rename(columns={
    0: "cell", 1: "minlat", 2: "maxlat", 3: "minlon", 4: "maxlon",
    5: "am", 6: "nden", 7: "mgo", 8: "al2o3", 9: "sio2", 10: "cao",
    11: "tio2", 12: "feo", 13: "k", 14: "th", 15: "u", 60: "u_var"})
# LP GRS table already reports K/Th/U in micrograms/gram (ppm); oxides are weight fractions.
lp["u_ppm"] = lp["u"]
lp["th_ppm"] = lp["th"]
lp["k_ppm"] = lp["k"]
lp["u_sigma_ppm"] = np.sqrt(lp["u_var"].clip(lower=0))
lp["clat"] = 0.5 * (lp["minlat"] + lp["maxlat"])
lp["clon_raw"] = 0.5 * (lp["minlon"] + lp["maxlon"])  # -180..180 E
lp["clon"] = lp["clon_raw"] % 360.0
R_moon = 1737.4e3
lp["cell_area_km2"] = (R_moon ** 2 / 1e6) * np.deg2rad(lp["maxlon"] - lp["minlon"]) * (
    np.sin(np.deg2rad(lp["maxlat"])) - np.sin(np.deg2rad(lp["minlat"])))

# ---------------- Mars geochemistry (ODY GRS 5x5 cells) ----------------
def read_ody(name):
    df = pd.read_csv(RAW / f"ody_grs/{name}.tab", sep=r"\s+", header=None,
                     names=["clat", "clon", "val", "sigma", "sigma_cfs"])
    df.loc[df["val"] < 0, ["val", "sigma"]] = np.nan
    return df.set_index(["clat", "clon"])

th = read_ody("th_5x5").rename(columns={"val": "th_wt", "sigma": "th_sig"})
k = read_ody("k_5x5").rename(columns={"val": "k_wt", "sigma": "k_sig"})
h2o = read_ody("h2o_sr_5x5").rename(columns={"val": "h2o_wt"})
mars = th.join(k[["k_wt", "k_sig"]]).join(h2o[["h2o_wt"]]).reset_index()
# ODY values are weight percent -> ppm
mars["th_ppm"] = mars["th_wt"] * 1e4
mars["k_ppm"] = mars["k_wt"] * 1e4
mars["h2o_pct"] = mars["h2o_wt"]
mars["kvsth"] = mars["k_wt"] / mars["th_wt"]
mars["cell"] = range(len(mars))
mars["minlat"], mars["maxlat"] = mars["clat"] - 2.5, mars["clat"] + 2.5
mars["minlon_raw"], mars["maxlon_raw"] = mars["clon"] - 2.5, mars["clon"] + 2.5
R_mars = 3396.2e3
mars["cell_area_km2"] = (R_mars ** 2 / 1e6) * np.deg2rad(5.0) * (
    np.sin(np.deg2rad(mars["maxlat"])) - np.sin(np.deg2rad(mars["minlat"])))

# sanity prints
print("Moon cells:", len(lp), "| U mean ppm:", lp['u_ppm'].mean().round(3),
      "| Th mean ppm:", lp['th_ppm'].mean().round(3))
print("Mars cells:", len(mars), "| Th median ppm:", np.nanmedian(mars['th_ppm']).round(3),
      "| K median ppm:", np.nanmedian(mars['k_ppm']).round(1),
      "| Th coverage:", np.mean(np.isfinite(mars['th_ppm'])).round(3))

lp.to_csv(INT / "moon_cells_raw.csv", index=False)
mars.to_csv(INT / "mars_cells_raw.csv", index=False)
