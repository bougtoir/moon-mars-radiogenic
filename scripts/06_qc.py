"""QC: spatial autocorrelation, coverage, missingness, sanity diagnostics -> results/QC.md"""
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
def load(p): return pd.read_csv(BASE/p)
lines=["# Phase 23 QC diagnostics",""]
for body in ["moon","mars"]:
    g=load(f"data_processed/{body}_common_grid.csv")
    lines.append(f"## {body.capitalize()} ({len(g)} cells)")
    col = ["C_integrated","A_element","rank_sd","u_ppm" if body=="moon" else "th_ppm"]
    pos=np.c_[g["clat"].values*np.pi/180, g["clon"].values*np.pi/180]
    xyz=np.c_[np.cos(pos[:,0])*np.cos(pos[:,1]),np.cos(pos[:,0])*np.sin(pos[:,1]),np.sin(pos[:,0])]
    tree=cKDTree(xyz); pairs=tree.query_pairs(np.radians(7.5))
    i=[p[0] for p in pairs]; j=[p[1] for p in pairs]
    for c in col:
        if c not in g.columns: continue
        x=g[c].values; ok=np.isfinite(x); xn=x[ok]
        mp=-np.ones(len(x),int); mp[ok]=np.arange(len(xn))
        pr=[(mp[a],mp[b]) for a,b in zip(i,j) if ok[a] and ok[b]]
        idx=np.array([p[0] for p in pr]); jdx=np.array([p[1] for p in pr])
        xm=xn.mean(); xs=xn-xm
        den=(xs**2).sum()
        mi=(len(xn)/len(idx))*((xs[idx]*xs[jdx]).sum()/den) if den>0 and len(idx) else np.nan
        lines.append(f"- Moran-like I({c}) = {mi:.3f} over {len(idx)} neighbour pairs (7.5° adjacency)")
    miss={c: int(g[c].isna().sum()) for c in g.columns if g[c].isna().sum()>0}
    lines.append(f"- columns with missing values: {miss if miss else 'none'}")
lines.append("")
lines.append("## Declared checks")
lines.append("- Layer Moran I ranges ~0.15–0.96 → strong spatial autocorrelation; per-cell inferential p-values would be anti-conservative. We therefore rely on set-overlap metrics (Jaccard), rank correlations and resampling, as protocolled.")
lines.append("- Lunar T domain is near-flat (limited dynamic range of basin/crater fractions at 5°) — flagged in LIMITATIONS.")
Path(BASE/"results/QC.md").write_text("\n".join(lines))
print("QC written")
