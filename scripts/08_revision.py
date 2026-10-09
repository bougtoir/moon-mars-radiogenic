"""08_revision.py — targeted revision analyses:
A) Mars sensitivity excluding the E_h2o (water-equivalent hydrogen) layer from M;
B) 10-deg common-grid robustness pass (aggregation of existing 5-deg evidence);
C) per-region evidence table for the four Martian candidate regions.
Outputs to results/ only; does not change canonical 5-deg results.
"""
import numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import rankdata, spearmanr
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist

ROOT = Path(__file__).resolve().parent.parent
PROC, RES = ROOT/"data_processed", ROOT/"results"
rng = np.random.default_rng(20260926)

def pr(x):
    x = np.asarray(x, float); r = np.full_like(x, np.nan)
    ok = np.isfinite(x); r[ok] = rankdata(x[ok]) / ok.sum(); return r

def jaccard(a, b):
    a, b = set(a), set(b); return len(a & b) / max(len(a | b), 1)

def metrics(df, ecol="A_element", ccol="C_integrated", dcol="D_isru"):
    okA = np.isfinite(df[ecol]); okC = np.isfinite(df[ccol]); okD = np.isfinite(df[dcol])
    mask = okA & okC; maskD = okC & okD
    n = mask.sum()
    out = {"n": int(n),
           "rho_elem_integr": spearmanr(df.loc[mask,ecol], df.loc[mask,ccol]).statistic,
           "GRSens": np.nan,
           "rho_geo_isru": spearmanr(df.loc[maskD,ccol], df.loc[maskD,dcol]).statistic,
           "ISRUshift": np.nan}
    out["GRSens"] = 1 - out["rho_elem_integr"]; out["ISRUshift"] = 1 - out["rho_geo_isru"]
    for q in (0.01, 0.05, 0.10):
        k = max(1, int(round(q*n)))
        te = df.loc[mask].nsmallest(k, ecol).index
        tc = df.loc[mask].nsmallest(k, ccol).index
        td = df.loc[maskD].nsmallest(max(1, int(round(q*maskD.sum()))), dcol).index
        out[f"jaccard_top{int(q*100)}_e_vs_c"] = jaccard(te, tc)
        out[f"jaccard_top{int(q*100)}_c_vs_d"] = jaccard(tc, td)
    dr = df.loc[mask, ecol] - df.loc[mask, ccol]
    out["drank_abs_med"] = dr.abs().median(); out["drank_abs_max"] = dr.abs().max()
    return out

mars = pd.read_csv(PROC/"mars_common_grid.csv")
moon = pd.read_csv(PROC/"moon_common_grid.csv")

# ---------- A) Mars without E_h2o ----------
m2 = mars.copy()
m2["M"] = np.nanmean(np.vstack([m2["E_sed"], m2["E_lake"], m2["E_volc"]]), 0)
m2["C_integrated"] = np.exp(np.nanmean(np.log(np.clip(
    np.vstack([m2["S"], m2["M"], m2["T"]]).T, 1e-6, None)), 1))
m2["D_isru"] = np.exp(np.nanmean(np.log(np.clip(
    np.vstack([m2["C_integrated"], m2["C_integrated"], m2["A"]]).T, 1e-6, None)), 1))
for col in ["A_element","C_integrated","D_isru"]:
    m2["rank_"+col] = rankdata(np.where(np.isfinite(m2[col]), -m2[col], np.inf))
met_noh2o = metrics(m2, "rank_A_element", "rank_C_integrated", "rank_D_isru")
met_noh2o["variant"] = "Mars excluding E_h2o"
base = pd.read_csv(RES/"primary_metrics.csv", index_col=0).loc["Mars"]
comp = pd.DataFrame([{**{k: base[k] for k in met_noh2o if k in base}, "variant": "Mars baseline (with E_h2o)"},
                     met_noh2o]).set_index("variant")
# top-5% membership stability of C itself with vs without E_h2o
ok = np.isfinite(mars["C_integrated"]) & np.isfinite(m2["C_integrated"])
k5 = max(1, int(0.05*ok.sum()))
topA = set(mars.index[ok][np.argsort(-mars.loc[ok,"C_integrated"].values)[:k5]])
topB = set(m2.index[ok][np.argsort(-m2.loc[ok,"C_integrated"].values)[:k5]])
comp["j5_C_vs_C_no_h2o"] = [np.nan, jaccard(topA, topB)]
comp.to_csv(RES/"mars_h2o_exclusion.csv")
print("== Mars H2O exclusion =="); print(comp.round(3).to_string())

# ---------- B) 10-degree robustness ----------
rows = []
for name, df in (("Moon", moon), ("Mars", mars)):
    d = df.copy()
    d["b10"] = list(zip((d["clat"]+5)//10*10 - 5, (d["clon"]+5)//10*10 - 5))
    ec = [c for c in d.columns if c.startswith("E_")]
    agg = d.groupby("b10")[ec + ["S","M","T","A","K","cell_area_km2"]].mean().reset_index()
    agg["n5"] = d.groupby("b10").size().values
    # renormalize evidence layers within the 10-deg set, then rebuild domains
    for c in ec: agg[c] = pr(agg[c])
    if name == "Moon":
        agg["S"] = agg["E_u"]; agg["M"] = np.nanmean(np.vstack([agg["E_feo"],agg["E_tio2"],agg["E_volc"]]),0)
        agg["T"] = np.nanmean(np.vstack([agg["E_basin"],agg["E_crater"]]),0)
        agg["A"] = np.nanmean(np.vstack([agg["E_slope"],agg["E_rough"]]),0)
    else:
        agg["S"] = agg["E_th"]; agg["M"] = np.nanmean(np.vstack([agg["E_sed"],agg["E_lake"],agg["E_h2o"],agg["E_volc"]]),0)
        agg["T"] = np.nanmean(np.vstack([agg["E_trap"],agg["E_age"]]),0)
        agg["A"] = np.nanmean(np.vstack([agg["E_slope"],agg["E_rough"],agg["E_elev"]]),0)
    agg["A_element"] = agg["S"]
    agg["C_integrated"] = np.exp(np.nanmean(np.log(np.clip(
        np.vstack([agg["S"],agg["M"],agg["T"]]).T, 1e-6, None)), 1))
    agg["D_isru"] = np.exp(np.nanmean(np.log(np.clip(
        np.vstack([agg["C_integrated"],agg["C_integrated"],agg["A"]]).T, 1e-6, None)), 1))
    for col in ["A_element","C_integrated","D_isru"]:
        agg["rank_"+col] = rankdata(np.where(np.isfinite(agg[col]), -agg[col], np.inf))
    mm = metrics(agg, "rank_A_element","rank_C_integrated","rank_D_isru")
    mm["planet"] = name; mm["grid"] = "10deg"
    rows.append(mm)
pd.DataFrame(rows).set_index("planet").to_csv(RES/"resolution_10deg.csv")
print("== 10-deg robustness =="); print(pd.DataFrame(rows).set_index("planet").round(3).to_string())

# ---------- C) per-region evidence (Mars) ----------
n = mars["rank_C_integrated"].notna().sum(); k = max(1, int(0.05*n))
cand = mars[mars["rank_C_integrated"] <= k].copy()
pts = np.deg2rad(np.c_[cand["clat"], cand["clon"]])
xyz = np.c_[np.cos(pts[:,0])*np.cos(pts[:,1]), np.cos(pts[:,0])*np.sin(pts[:,1]), np.sin(pts[:,0])]
Z = linkage(pdist(xyz), method="single")
thr = 2*np.sin(np.deg2rad(7.0)/2)
cand["cluster"] = fcluster(Z, thr, criterion="distance")
rows = []
for cl, g in cand.groupby("cluster"):
    if len(g) < 3: continue
    rows.append(dict(cluster=int(cl), n_cells=len(g),
        clat=g["clat"].mean(), clon=g["clon"].mean() % 360, med_rank=g["rank_C_integrated"].median(),
        S_mean=g["S"].mean(), E_th=g["E_th"].mean(), E_k=g["E_k"].mean(),
        E_sed=g["E_sed"].mean(), E_lake=g["E_lake"].mean(), E_h2o=g["E_h2o"].mean(),
        E_volc=g["E_volc"].mean(), E_trap=g["E_trap"].mean(), E_age=g["E_age"].mean(),
        A_mean=g["A"].mean()))
ev = pd.DataFrame(rows).sort_values("med_rank")
ev.to_csv(RES/"mars_region_evidence.csv", index=False)
glob = {c: mars[c].mean() for c in ["E_th","E_k","E_sed","E_lake","E_h2o","E_volc","E_trap","E_age"]}
print("== Mars region evidence vs global means =="); print(ev.round(3).to_string(index=False))
print("global:", {k: round(v,3) for k,v in glob.items()})
