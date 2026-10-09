#!/usr/bin/env python3
"""02_spatial_join.py — join geology/DEM/hydro layers onto geochemical cells.

Produces:
  data_interim/moon_cells_layers.csv
  data_interim/mars_cells_layers.csv
  data_processed/moon_common_grid.csv
  data_processed/mars_common_grid.csv
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
RAW, INT, PROC = ROOT/"data_raw", ROOT/"data_interim", ROOT/"data_processed"
PROC.mkdir(exist_ok=True)

moon = pd.read_csv(INT/"moon_cells_raw.csv")
mars = pd.read_csv(INT/"mars_cells_raw.csv")

# ---------- LOLA GDR readers (16 ppd, LSB int16) ----------
def read_gdr(name, scale, offset=0.0, nodata=-32768):
    p = RAW/f"dem/{name}.IMG"
    a = np.fromfile(p, dtype="<i2").reshape(2880, 5760)
    a = np.where(a == nodata, np.nan, a * scale + offset)
    lats = 90.0 - (np.arange(2880) + 0.5) * (180.0/2880)
    lons = (np.arange(5760) + 0.5) * (360.0/5760)
    return a, lats, lons

# scaling factors from labels (read earlier): LDEM 0.5 m, LDSM deg(?) use label values
# LDSM_16: UNIT=DEGREE OFFSET=45, SCALING_FACTOR assumed from label; verify at runtime.
import re as _re
def lbl_scale(name):
    txt = (RAW/f"dem/{name}.LBL").read_text(errors="ignore")
    sc = float(_re.search(r"SCALING_FACTOR\s*=\s*([0-9.eE+-]+)", txt).group(1))
    off = float(_re.search(r"OFFSET\s*=\s*([0-9.eE+-]+)", txt).group(1))
    return sc, off

ldem_s, ldem_o = lbl_scale("LDEM_16");  elev, elat, elon = read_gdr("LDEM_16", ldem_s, ldem_o)
ldsm_s, ldsm_o = lbl_scale("LDSM_16");  slope, _, _ = read_gdr("LDSM_16", ldsm_s, ldsm_o)
ldrm_s, ldrm_o = lbl_scale("LDRM_16");  rough, _, _ = read_gdr("LDRM_16", ldrm_s, ldrm_o)

def cell_mean(arr, lats, lons, minlat, maxlat, minlon0360, maxlon0360):
    r = np.where((lats >= minlat) & (lats < maxlat))[0]
    lons_m = np.mod(lons, 360.0)
    if minlon0360 <= maxlon0360:
        c = np.where((lons_m >= minlon0360) & (lons_m < maxlon0360))[0]
    else:
        c = np.where((lons_m >= minlon0360) | (lons_m < maxlon0360))[0]
    if len(r) == 0 or len(c) == 0:
        return np.nan
    return np.nanmean(arr[np.ix_(r, c)])

moon["elev_m"] = np.nan; moon["slope_deg"] = np.nan; moon["rough_m"] = np.nan
for i, row in moon.iterrows():
    lo = row["clon_raw"] - 0.5*abs(row["maxlon"]-row["minlon"]) if False else row["minlon"] % 360
    hi = row["maxlon"] % 360
    moon.loc[i, "elev_m"] = cell_mean(elev, elat, elon, row.minlat, row.maxlat, lo, hi)
    moon.loc[i, "slope_deg"] = cell_mean(slope, elat, elon, row.minlat, row.maxlat, lo, hi)
    moon.loc[i, "rough_m"] = cell_mean(rough, elat, elon, row.minlat, row.maxlat, lo, hi)
print("moon DEM joined:", moon["slope_deg"].notna().mean())

# ---------- Lunar geology ----------
geo = gpd.read_file(RAW/"moon_geol/Unified_Geologic_Map_of_the_Moon_GIS/Lunar_GIS/Shapefiles/GeoUnits.shp")
u2 = geo["FIRST_Un_2"].fillna("")
def moon_class(u, code):
    if "Mare" in u or "Dome" in u or "Mantling" in u:
        return "volcanic"
    if "Basin" in u:
        return "basin"
    if any(k in u for k in ("Crater", "Imbrium", "Orientale", "Nectaris")):
        return "crater"
    return "terra"
geo["gclass"] = [moon_class(u, c) for u, c in zip(u2, geo["FIRST_Unit"])]

moon["frac_volcanic"] = 0.0; moon["frac_basin"] = 0.0; moon["frac_crater"] = 0.0
geo_sidx = geo.sindex
for i, row in moon.iterrows():
    b = box(row.minlon, row.minlat, row.maxlon, row.maxlat)
    cand = geo.iloc[list(geo_sidx.intersection(b.bounds))]
    if cand.empty:
        continue
    inter = cand.intersection(b)
    areas = inter.area.values
    tot = b.area
    frac = {}
    for gcls, a in zip(cand["gclass"], areas):
        frac[gcls] = frac.get(gcls, 0) + a / tot
    moon.loc[i, "frac_volcanic"] = frac.get("volcanic", 0.0)
    moon.loc[i, "frac_basin"] = frac.get("basin", 0.0)
    moon.loc[i, "frac_crater"] = frac.get("crater", 0.0)
print("moon geology joined")

# ---------- Mars geology ----------
mgeo = gpd.read_file(RAW/"mars_geol/extracted/SIM3292_MarsGlobalGeologicGIS_20M/SIM3292_Shapefiles/SIM3292_Global_Geology.shp")
# unit code pattern: era prefix letters + type suffix
ERA_SCORE = {"eN": 1.0, "mN": 0.95, "lN": 0.9, "HN": 0.85, "N": 0.9, "H": 0.55,
             "eH": 0.6, "lH": 0.5, "AH": 0.3, "eA": 0.2, "mA": 0.15, "lA": 0.1, "A": 0.15}
def parse_unit(code):
    m = re.match(r"^(lA|eA|mA|AH|eH|lH|HN|eN|mN|lN|AN|A|H|N)(.*)$", str(code))
    if not m:
        return None, ""
    return m.group(1), m.group(2)
def mars_class(code):
    era, t = parse_unit(code)
    if t in ("b",):
        return "basin", era
    if t in ("l",):
        return "lowland", era
    if t in ("t", "to", "tu"):
        return "transition", era
    if t in ("a", "pu", "u"):
        return "mantle", era
    if t in ("v", "ve", "vf"):
        return "volcanic", era
    if t in ("h", "hm"):
        return "highland", era
    if t in ("p", "pc", "pd"):
        return "polar", era
    if t == "i":
        return "impact", era
    return "other", era
mgeo["gclass"], mgeo["era"] = zip(*[mars_class(c) for c in mgeo["Unit"]])
mgeo["age_score"] = mgeo["era"].map(ERA_SCORE).fillna(0.4)

for col in ["basin", "lowland", "transition", "mantle", "volcanic", "highland", "polar", "impact", "other"]:
    mars[f"frac_{col}"] = 0.0
mars["geo_age"] = np.nan
mars["geol_cover"] = 0.0
msidx = mgeo.sindex
mars["minlon_180"] = ((mars["minlon_raw"] + 180) % 360) - 180
mars["maxlon_180"] = ((mars["maxlon_raw"] + 180) % 360) - 180
for i, row in mars.iterrows():
    if row.minlon_180 <= row.maxlon_180:
        boxes = [box(row.minlon_180, row.minlat, row.maxlon_180, row.maxlat)]
    else:  # wraps the antimeridian
        boxes = [box(row.minlon_180, row.minlat, 180, row.maxlat),
                 box(-180, row.minlat, row.maxlon_180, row.maxlat)]
    b = boxes[0].union(boxes[1]) if len(boxes) > 1 else boxes[0]
    cand = mgeo.iloc[list(msidx.intersection(b.bounds))]
    if cand.empty:
        continue
    inter = cand.intersection(b)
    keep = ~inter.is_empty.values
    if not keep.any():
        continue
    cand = cand[keep]
    inter = inter[keep]
    areas = inter.area.values
    # area weighting approximated by cos(latitude of polygon centroid)
    wts = np.array([np.cos(np.deg2rad(g.centroid.y)) for g in inter])
    wts = np.clip(wts * areas, 0, None)
    tot = wts.sum()
    if tot <= 0:
        continue
    for gcls, a, ag in zip(cand["gclass"], wts, cand["age_score"]):
        mars.loc[i, f"frac_{gcls}"] = mars.loc[i, f"frac_{gcls}"] + a/tot
        mars.loc[i, "geo_age"] = np.nansum([mars.loc[i, "geo_age"], a*ag/tot])
        mars.loc[i, "geol_cover"] = min(1.0, mars.loc[i, "geol_cover"] + a/tot)
print("mars geology joined:", mars["geol_cover"].mean())

# ---------- Mars paleolakes ----------
lakes = pd.read_csv(RAW/"mars_hydro/lakes_csv/Goudge_et_al_2016_Geology_CBL_OBL_Catalogue.csv")
print("lake cols:", lakes.columns.tolist()[:12])
latc = [c for c in lakes.columns if "lat" in c.lower()][0]
lonc = [c for c in lakes.columns if "lon" in c.lower()][0]
typec = [c for c in lakes.columns if "type" in c.lower() or "basin" in c.lower()]
print("lake coord cols:", latc, lonc, typec)
lk_lon = lakes[lonc].astype(float)
lk_lon0360 = lk_lon % 360
mars["n_lakes"] = 0; mars["n_open_lakes"] = 0
openmask = None
for tc in typec:
    v = lakes[tc].astype(str).str.lower()
    if v.str.contains("open").any():
        openmask = v.str.contains("open")
        break
for i, row in mars.iterrows():
    sel = (lakes[latc].astype(float).between(row.minlat, row.maxlat) &
           lk_lon0360.between(row.minlon_raw % 360, (row.maxlon_raw % 360), inclusive="both"))
    if row.minlon_raw % 360 > row.maxlon_raw % 360:
        sel = (lakes[latc].astype(float).between(row.minlat, row.maxlat) &
               ((lk_lon0360 >= row.minlon_raw % 360) | (lk_lon0360 <= row.maxlon_raw % 360)))
    mars.loc[i, "n_lakes"] = int(sel.sum())
    if openmask is not None:
        mars.loc[i, "n_open_lakes"] = int((sel & openmask.values).sum())
print("lakes joined; cells with lakes:", (mars["n_lakes"]>0).sum())

# ---------- Mars MOLA/HRSC DEM stats (vsicurl overview ~0.5deg) ----------
try:
    import rasterio
    url = "/vsicurl/https://planetarymaps.usgs.gov/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif"
    ds = rasterio.open(url)
    # read at overview covering full globe cheaply
    ov = 64
    h, w = ds.height//ov, ds.width//ov
    arr = ds.read(1, out_shape=(h, w)).astype("float64")
    # raster extent: global -180..180 lon, -90..90 lat (ESRI:104971 is geographic)
    arr[arr < -10000] = np.nan
    mlat = 90.0 - (np.arange(h)+0.5)*(180.0/h)
    mlon = -180.0 + (np.arange(w)+0.5)*(360.0/w)
    gy2, gx2 = np.gradient(arr)
    # meters per pixel
    mppy = 3396.2e3*np.pi/180 * (180.0/h)
    mppx = 3396.2e3*np.pi/180 * (360.0/w)
    slope_m = np.degrees(np.arctan(np.hypot(gy2/mppy, gx2/mppx)))
    mars["elev_m"] = np.nan; mars["slope_deg"] = np.nan; mars["rough_m"] = np.nan
    for i, row in mars.iterrows():
        lo, hi = row.minlon_180, row.maxlon_180
        r = np.where((mlat >= row.minlat) & (mlat < row.maxlat))[0]
        if lo <= hi:
            c = np.where((mlon >= lo) & (mlon < hi))[0]
        else:
            c = np.where((mlon >= lo) | (mlon < hi))[0]
        if len(r)==0 or len(c)==0: continue
        mars.loc[i,"elev_m"] = np.nanmean(arr[np.ix_(r,c)])
        mars.loc[i,"slope_deg"] = np.nanmean(slope_m[np.ix_(r,c)])
        mars.loc[i,"rough_m"] = np.nanstd(arr[np.ix_(r,c)])
    print("mars DEM joined:", mars["slope_deg"].notna().mean())
except Exception as e:
    print("MOLA DEM FAILED:", e)

moon.to_csv(INT/"moon_cells_layers.csv", index=False)
mars.to_csv(INT/"mars_cells_layers.csv", index=False)
moon.to_csv(PROC/"moon_common_grid.csv", index=False)
mars.to_csv(PROC/"mars_common_grid.csv", index=False)
print("done")
