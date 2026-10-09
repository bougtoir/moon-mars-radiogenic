#!/usr/bin/env python3
"""03_models.py — evidence normalization, domain scores, models A–D,
Monte-Carlo weight uncertainty, rank metrics, hotspots, robustness.

Outputs under data_processed/, results/, tables/.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata, spearmanr
from scipy.spatial import cKDTree
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist

ROOT = Path(__file__).resolve().parent.parent
INT, PROC, RES, TAB = (ROOT/d for d in ("data_interim","data_processed","results","tables"))
for d in (RES, TAB): d.mkdir(exist_ok=True)
rng = np.random.default_rng(20260926)

def pr(x):
    """percentile rank in (0,1]; NaN stays NaN."""
    x = np.asarray(x, float)
    r = np.full_like(x, np.nan)
    ok = np.isfinite(x)
    r[ok] = rankdata(x[ok]) / ok.sum()
    return r

def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / max(len(a | b), 1)

# =============== MOON ===============
moon = pd.read_csv(INT/"moon_cells_layers.csv")
moon["E_u"]  = pr(moon["u_ppm"])
moon["E_th"] = pr(moon["th_ppm"])
moon["E_k"]  = pr(moon["k_ppm"])
moon["E_feo"]  = pr(moon["feo"])
moon["E_tio2"] = pr(moon["tio2"])
moon["E_volc"] = pr(moon["frac_volcanic"])
moon["E_basin"]  = pr(moon["frac_basin"])
moon["E_crater"] = pr(moon["frac_crater"])
moon["E_slope"] = 1 - pr(moon["slope_deg"])
moon["E_rough"] = 1 - pr(moon["rough_m"])
moon["K"] = 1.0  # full coverage layers

# domains
moon["S"] = moon["E_u"]                                   # Model A (element-only)
moon["M"] = np.nanmean(np.vstack([moon["E_feo"], moon["E_tio2"], moon["E_volc"]]), 0)
moon["T"] = np.nanmean(np.vstack([moon["E_basin"], moon["E_crater"]]), 0)
moon["A"] = np.nanmean(np.vstack([moon["E_slope"], moon["E_rough"]]), 0)

# =============== MARS ===============
mars = pd.read_csv(INT/"mars_cells_layers.csv")
mars["E_th"] = pr(mars["th_ppm"])
mars["E_k"]  = pr(mars["k_ppm"])
mars["frac_sed"] = mars[["frac_basin","frac_lowland","frac_transition","frac_mantle"]].sum(1)
mars["lake_den"] = mars["n_lakes"] / mars["cell_area_km2"] * 1e5
mars["E_sed"]  = pr(mars["frac_sed"])
mars["E_lake"] = pr(mars["lake_den"])
mars["E_h2o"]  = pr(mars["h2o_pct"])
mars["E_volc"] = pr(mars["frac_volcanic"])
mars["E_age"]  = pr(mars["geo_age"])
mars["E_trap"] = pr(mars["frac_sed"] * mars["geo_age"])     # ancient sedimentary accommodation
mars["E_slope"] = 1 - pr(mars["slope_deg"])
mars["E_rough"] = 1 - pr(mars["rough_m"])
mars["E_elev"] = 1 - pr(np.abs(mars["elev_m"]))             # extreme elevations less accessible
# coverage: th/k/h2o GRS missing at high lat; lakes catalog global (treated complete)
obs = np.isfinite(mars[["E_th","E_k","E_h2o","E_slope","E_rough","E_elev"]]).sum(1) + 3
mars["K"] = obs / 9.0

mars["S"] = mars["E_th"]
mars["M"] = np.nanmean(np.vstack([mars["E_sed"], mars["E_lake"], mars["E_h2o"], mars["E_volc"]]), 0)
mars["T"] = np.nanmean(np.vstack([mars["E_trap"], mars["E_age"]]), 0)
mars["A"] = np.nanmean(np.vstack([mars["E_slope"], mars["E_rough"], mars["E_elev"]]), 0)

def models(df):
    out = {}
    out["A_element"] = df["S"].values
    out["B_geo"] = np.nanmean(np.vstack([df["M"].values, df["T"].values]), 0)
    out["C_integrated"] = np.exp(np.nanmean(np.log(np.clip(np.vstack(
        [df["S"], df["M"], df["T"]]).T, 1e-6, None)), 1))
    # ISRU priority = geometric combination of geological prospectivity (weight 2/3) and accessibility (1/3)
    out["D_isru"] = np.exp(np.nanmean(np.log(np.clip(np.vstack(
        [out["C_integrated"], out["C_integrated"], df["A"]]).T, 1e-6, None)), 1))
    return out

moon_m = models(moon); mars_m = models(mars)
for df, m in ((moon, moon_m), (mars, mars_m)):
    for k, v in m.items():
        df[k] = v
        df[f"rank_{k}"] = rankdata(np.where(np.isfinite(v), -v, np.inf))  # 1 = highest score

# =============== METRICS ===============
def metrics(df):
    okA = np.isfinite(df["A_element"]); okC = np.isfinite(df["C_integrated"]); okD = np.isfinite(df["D_isru"])
    rho_elem = spearmanr(df.loc[okA,"rank_A_element"], df.loc[okC & okA,"rank_C_integrated"]).statistic
    # careful: align masks
    mask = okA & okC
    rho_elem = spearmanr(df.loc[mask,"rank_A_element"], df.loc[mask,"rank_C_integrated"]).statistic
    maskD = okC & okD
    rho_isru = spearmanr(df.loc[maskD,"rank_C_integrated"], df.loc[maskD,"rank_D_isru"]).statistic
    n = mask.sum()
    out = {"n": int(n), "rho_elem_integr": rho_elem, "GRSens": 1-rho_elem,
           "rho_geo_isru": rho_isru, "ISRUshift": 1-rho_isru}
    for q in (0.01, 0.05, 0.10):
        k = max(1, int(round(q*n)))
        top_e = df.loc[mask].nsmallest(k, "rank_A_element").index
        top_c = df.loc[mask].nsmallest(k, "rank_C_integrated").index
        top_d = df.loc[maskD].nsmallest(max(1,int(round(q*maskD.sum()))), "rank_D_isru").index
        out[f"jaccard_top{int(q*100)}_e_vs_c"] = jaccard(top_e, top_c)
        out[f"jaccard_top{int(q*100)}_c_vs_d"] = jaccard(df.loc[mask].nsmallest(k,"rank_C_integrated").index, top_d)
    dr = df.loc[mask,"rank_A_element"] - df.loc[mask,"rank_C_integrated"]
    out["drank_mean"] = dr.mean(); out["drank_abs_med"] = dr.abs().median()
    out["drank_abs_max"] = dr.abs().max()
    return out

m_moon = metrics(moon); m_mars = metrics(mars)
pd.DataFrame([m_moon, m_mars], index=["Moon","Mars"]).to_csv(RES/"primary_metrics.csv")
print(pd.DataFrame([m_moon, m_mars], index=["Moon","Mars"]).T.round(3))

# =============== MONTE CARLO weight uncertainty ===============
NDRAW = 10000
def mc_weights(df, ndraw=NDRAW):
    n = len(df)
    S, M, T = df["S"].values, df["M"].values, df["T"].values
    top5_count = np.zeros(n); top1_count = np.zeros(n); top10_count = np.zeros(n)
    rank_sum = np.zeros(n); rank_sq = np.zeros(n); nok = 0
    k1, k5, k10 = max(1,int(.01*n)), max(1,int(.05*n)), max(1,int(.10*n))
    for d in range(ndraw):
        w = rng.dirichlet([1,1,1])
        g = np.full(n, np.nan)
        ok = np.isfinite(S) & np.isfinite(M) & np.isfinite(T)
        g[ok] = np.exp(w[0]*np.log(np.clip(S[ok],1e-6,None)) +
                       w[1]*np.log(np.clip(M[ok],1e-6,None)) +
                       w[2]*np.log(np.clip(T[ok],1e-6,None)))
        r = np.full(n, np.inf); r[ok] = rankdata(-g[ok])
        top1_count += r <= k1; top5_count += r <= k5; top10_count += r <= k10
        rank_sum += np.where(np.isfinite(r), r, np.nan)
        rank_sq += np.where(np.isfinite(r), r, 0)**2
        nok += 1
    mr = rank_sum/nok
    sd = np.sqrt(rank_sq/nok - mr**2)
    return pd.DataFrame({"rank_mean": mr, "rank_sd": sd,
                         "p_top1": top1_count/nok, "p_top5": top5_count/nok,
                         "p_top10": top10_count/nok}, index=df.index)

moon = pd.concat([moon, mc_weights(moon)], axis=1)
mars = pd.concat([mars, mc_weights(mars)], axis=1)

# =============== HOTSPOTS (connected top-5% clusters) ===============
def hotspots(df, planet, R):
    n = df["rank_C_integrated"].notna().sum()
    k = max(1, int(0.05*n))
    cand = df[df["rank_C_integrated"] <= k].copy()
    pts = np.deg2rad(np.c_[cand["clat"], cand["clon"]])
    # chord distance on sphere, threshold ~ half-degree * ~ sqrt area
    xyz = np.c_[np.cos(pts[:,0])*np.cos(pts[:,1]),
                np.cos(pts[:,0])*np.sin(pts[:,1]),
                np.sin(pts[:,0])]
    D = pdist(xyz); Z = linkage(D, method="single")
    # single-linkage cut: nearest-neighbor gap in degrees ~ cell spacing
    spacing = np.deg2rad(7.0); thr = 2*np.sin(spacing/2)
    cand["cluster"] = fcluster(Z, thr, criterion="distance")
    rows = []
    cid = 0
    for cl, grp in cand.groupby("cluster"):
        if len(grp) < 3:  # min area threshold ~3 cells
            continue
        cid += 1
        rows.append(dict(
            planet=planet, region=f"Candidate Region {cid}",
            n_cells=len(grp),
            clat=np.degrees(np.arctan2(np.sin(np.deg2rad(grp["clat"])).mean(),
                                       np.cos(np.deg2rad(grp["clat"])).mean())),
            clon=np.degrees(np.arctan2(np.sin(np.deg2rad(grp["clon"])).mean(),
                                       np.cos(np.deg2rad(grp["clon"])).mean())) % 360,
            area_km2=grp["cell_area_km2"].sum(),
            med_rank=grp["rank_C_integrated"].median(),
            p_top5_mean=grp["p_top5"].mean(),
            K_mean=grp["K"].mean(),
            S_mean=grp["S"].mean(), M_mean=grp["M"].mean(), T_mean=grp["T"].mean(),
            A_mean=grp["A"].mean()))
    return pd.DataFrame(rows).sort_values("med_rank")

hs_moon = hotspots(moon, "Moon", 1737.4)
hs_mars = hotspots(mars, "Mars", 3396.2)
hs = pd.concat([hs_moon, hs_mars], ignore_index=True)
hs["region"] = ["Candidate Region %d" % (i+1) for i in range(len(hs))]
hs.to_csv(RES/"candidate_regions.csv", index=False)
print(hs[["planet","region","n_cells","clat","clon","area_km2","med_rank","p_top5_mean"]].round(2).to_string(index=False))

# =============== ROBUSTNESS ===============
rob = []
def robust_eval(df, name):
    S,M,T = df["S"].values, df["M"].values, df["T"].values
    A = df["A_element"].values
    mask = np.isfinite(A) & np.isfinite(S) & np.isfinite(M) & np.isfinite(T)
    n = mask.sum(); k5 = max(1,int(0.05*n))
    topA = set(df.index[mask][np.argsort(-A[mask])[:k5]])
    def jacc_of(g):
        r = np.argsort(-np.where(np.isfinite(g),g,-np.inf))[:k5]
        return jaccard(topA, set(df.index[r]))
    ge = np.exp((np.log(np.clip(S,1e-6,None))+np.log(np.clip(M,1e-6,None))+np.log(np.clip(T,1e-6,None)))/3)
    rob.append(dict(planet=name, test="geometric (primary)",
                    rho=spearmanr(A[mask],ge[mask]).statistic, j5=jacc_of(ge)))
    ga = np.nanmean(np.vstack([S,M,T]),0)
    rob.append(dict(planet=name, test="weighted additive",
                    rho=spearmanr(A[mask],ga[mask]).statistic, j5=jacc_of(ga)))
    gb = np.nanmin(np.vstack([S,M,T]),0)
    rob.append(dict(planet=name, test="bottleneck min(S,M,T)",
                    rho=spearmanr(A[mask],gb[mask]).statistic, j5=jacc_of(gb)))
    gr = pr(S)+pr(M)+pr(T)
    rob.append(dict(planet=name, test="rank-sum",
                    rho=spearmanr(A[mask],gr[mask]).statistic, j5=jacc_of(gr)))
    # leave-one-domain-out
    for dom, arr in (("S",S),("M",M),("T",T)):
        others = {"S":S,"M":M,"T":T}; del others[dom]
        g = np.exp(np.nanmean(np.log(np.clip(np.vstack(list(others.values())),1e-6,None)),0))
        rob.append(dict(planet=name, test=f"leave-{dom}-out",
                        rho=spearmanr(A[mask],g[mask]).statistic, j5=jacc_of(g)))
    # leave-one-layer-out (recompute M/T minus each evidence col)
    for lay in [c for c in df.columns if c.startswith("E_")]:
        dfE = df.copy()
        dfE[lay] = np.nan
        Ml = np.nanmean(np.vstack([dfE[c] for c in df.columns if c.startswith("E_") and c in
                    (["E_feo","E_tio2","E_volc","E_sed","E_lake","E_h2o"])]),0)
        Tl = np.nanmean(np.vstack([dfE[c] for c in df.columns if c.startswith("E_") and c in
                    (["E_basin","E_crater","E_trap","E_age"])]),0)
        g = np.exp(np.nanmean(np.log(np.clip(np.vstack([dfE["S"],Ml,Tl]),1e-6,None)),0))
        rob.append(dict(planet=name, test=f"leave-layer {lay}",
                        rho=spearmanr(A[mask],g[mask]).statistic, j5=jacc_of(g)))
    # threshold sensitivity already in metrics; complete-case = mask (same here)
    # normalization sensitivity: min-max instead of percentile
    for col, base in (("S","u_ppm" if name=="Moon" else "th_ppm"),):
        v = df[base].values
        g = (v - np.nanmin(v))/(np.nanmax(v)-np.nanmin(v))
        g2 = np.exp(np.nanmean(np.log(np.clip(np.vstack([g,df["M"],df["T"]]),1e-6,None)),0))
        rob.append(dict(planet=name, test="minmax-norm S",
                        rho=spearmanr(A[mask],g2[mask]).statistic, j5=jacc_of(g2)))
    # coverage-restricted: exclude lowest-quartile K
    thr = np.nanquantile(df["K"], 0.25)
    m2 = mask & (df["K"].values >= thr)
    ge2 = np.where(m2, ge, np.nan)
    rr = np.isfinite(ge2)
    rob.append(dict(planet=name, test="exclude lowest-K quartile",
                    rho=spearmanr(A[m2],ge[m2]).statistic,
                    j5=jaccard(topA, set(df.index[rr][np.argsort(-ge2[rr])[:k5]]))))
    return rob

rob = robust_eval(moon, "Moon") + robust_eval(mars, "Mars")
robdf = pd.DataFrame(rob)
robdf.to_csv(RES/"robustness.csv", index=False)

# VOI (exploratory): U ~ rank_sd * K gap
for df in (moon, mars):
    df["U_model"] = df["rank_sd"] / df["rank_sd"].max()
    df["knowledge_gap"] = 1 - df["K"]
    df["VOI"] = df["U_model"] * df["knowledge_gap"]

moon.to_csv(PROC/"moon_common_grid.csv", index=False)
mars.to_csv(PROC/"mars_common_grid.csv", index=False)
print("\nGRSens  Moon=%.3f  Mars=%.3f" % (m_moon["GRSens"], m_mars["GRSens"]))
print("saved results/primary_metrics.csv, candidate_regions.csv, robustness.csv")
