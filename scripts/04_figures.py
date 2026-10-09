#!/usr/bin/env python3
"""04_figures.py — publication figures (equirectangular, planetocentric lat, 0–360E lon)."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIG, RES, PROC = ROOT/"figures", ROOT/"results", ROOT/"data_processed"
FIG.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.linewidth": 0.5})

moon = pd.read_csv(PROC/"moon_common_grid.csv")
mars = pd.read_csv(PROC/"mars_common_grid.csv")
hs = pd.read_csv(RES/"candidate_regions.csv")
rob = pd.read_csv(RES/"robustness.csv")

def cellmap(ax, df, val, cmap="viridis", label="", vmin=None, vmax=None, regions=None):
    """scatter cells as square markers in equirectangular view."""
    sc = ax.scatter(df["clon"], df["clat"], c=val, s=9, marker="s",
                    cmap=cmap, vmin=vmin, vmax=vmax, linewidths=0)
    ax.set_xlim(0, 360); ax.set_ylim(-90, 90)
    ax.set_xticks(range(0, 361, 60)); ax.set_yticks(range(-90, 91, 30))
    ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
    if regions is not None:
        for _, r in regions.iterrows():
            ax.plot(r["clon"], r["clat"], "rx", ms=7, mew=1.5)
            ax.annotate(r["region"].replace("Candidate Region ", "R"), (r["clon"], r["clat"]),
                        textcoords="offset points", xytext=(5, 4), color="r", fontsize=6)
    if label:
        plt.colorbar(sc, ax=ax, fraction=0.03, pad=0.02, label=label)
    return sc

# ---- Figure 1: conceptual framework ----
fig, ax = plt.subplots(figsize=(7.0, 2.2))
ax.axis("off")
labels = ["SOURCE\nU (Moon),\nTh, K (GRS)", "MOBILIZATION /\nCONCENTRATION\nmagmatic,\nhydrologic context",
          "TRAP / EXPOSURE\nsedimentary\naccommodation,\nimpact excavation",
          "ACCESSIBILITY\nslope, roughness,\n|elev| (ISRU proxy)"]
xs = np.linspace(0.08, 0.92, len(labels))
BW = 0.19
for x, l in zip(xs, labels):
    ax.add_patch(FancyBboxPatch((x-BW/2, 0.20), BW, 0.65, boxstyle="round,pad=0.02",
                 fc="#eef4fb", ec="#2255aa", lw=1.0))
    ax.text(x, 0.525, l, ha="center", va="center", fontsize=6)
for x1, x2 in zip(xs[:-1], xs[1:]):
    ax.add_patch(FancyArrowPatch((x1+BW/2+0.01, 0.525), (x2-BW/2-0.01, 0.525),
                 arrowstyle="-|>", mutation_scale=10, color="#333"))
ax.text(0.5, 0.05, "Models: A = source only;  B = geology only;  C = S×M×T integrated;  D = C combined with accessibility",
        ha="center", fontsize=7, style="italic")
fig.savefig(FIG/"fig1_framework.png", dpi=300, bbox_inches="tight"); plt.close(fig)

# ---- Figure 2: lunar evidence + source model ----
fig, axs = plt.subplots(2, 2, figsize=(9.5, 5.4))
cellmap(axs[0,0], moon, moon["u_ppm"], "magma", "U (µg/g)", regions=None)
axs[0,0].set_title("(a) Lunar Prospector U (5° equal-area bins)")
cellmap(axs[0,1], moon, moon["M"], "viridis", "normalized M")
axs[0,1].set_title("(b) Mobilization: mare/differentiation proxies")
cellmap(axs[1,0], moon, moon["T"], "viridis", "normalized T")
axs[1,0].set_title("(c) Trap/exposure: basin + crater excavation")
cellmap(axs[1,1], moon, moon["A"], "viridis", "normalized A")
axs[1,1].set_title("(d) Accessibility: inverse slope & roughness")
fig.tight_layout(); fig.savefig(FIG/"fig2_moon_layers.png", dpi=300); plt.close(fig)

# ---- Figure 3: martian layers ----
fig, axs = plt.subplots(2, 2, figsize=(9.5, 5.4))
cellmap(axs[0,0], mars, mars["th_ppm"], "magma", "Th (µg/g)")
axs[0,0].set_title("(a) Odyssey GRS Th (5° cells; polar masked)")
cellmap(axs[0,1], mars, mars["M"], "viridis", "normalized M")
axs[0,1].set_title("(b) Mobilization: sedimentary + lakes + WEH context + volcanic")
cellmap(axs[1,0], mars, mars["T"], "viridis", "normalized T")
axs[1,0].set_title("(c) Trap/exposure: ancient sedimentary accommodation")
cellmap(axs[1,1], mars, mars["A"], "viridis", "normalized A")
axs[1,1].set_title("(d) Accessibility: slope, roughness, |elevation|")
fig.tight_layout(); fig.savefig(FIG/"fig3_mars_layers.png", dpi=300); plt.close(fig)

# ---- Figure 4: element-only vs integrated ----
fig, axs = plt.subplots(2, 2, figsize=(9.5, 5.4))
cellmap(axs[0,0], moon, moon["A_element"], "magma", "score")
axs[0,0].set_title("(a) Moon — Model A (U only)")
cellmap(axs[0,1], moon, moon["C_integrated"], "magma", "score")
axs[0,1].set_title("(b) Moon — Model C (S·M·T)")
cellmap(axs[1,0], mars, mars["A_element"], "magma", "score")
axs[1,0].set_title("(c) Mars — Model A (Th only)")
cellmap(axs[1,1], mars, mars["C_integrated"], "magma", "score")
axs[1,1].set_title("(d) Mars — Model C (S·M·T)")
fig.tight_layout(); fig.savefig(FIG/"fig4_models.png", dpi=300); plt.close(fig)

# ---- Figure 5: rank-shift centerpiece ----
fig, axs = plt.subplots(2, 2, figsize=(9.5, 5.6))
vmax = np.nanpercentile(np.abs(moon["rank_A_element"]-moon["rank_C_integrated"]), 98)
cellmap(axs[0,0], moon, moon["rank_A_element"]-moon["rank_C_integrated"], "RdBu_r",
        "Δrank (element − integrated)", vmin=-vmax, vmax=vmax,
        regions=hs[hs.planet=="Moon"])
axs[0,0].set_title("(a) Moon Δrank (within-planet; positive = promoted by integration)")
vmax2 = np.nanpercentile(np.abs(mars["rank_A_element"]-mars["rank_C_integrated"]), 98)
cellmap(axs[0,1], mars, mars["rank_A_element"]-mars["rank_C_integrated"], "RdBu_r",
        "Δrank", vmin=-vmax2, vmax=vmax2, regions=hs[hs.planet=="Mars"])
axs[0,1].set_title("(b) Mars Δrank (within-planet; same sign convention)")
axs[1,0].hist((moon["rank_A_element"]-moon["rank_C_integrated"]).dropna(), bins=60,
              color="#2255aa", alpha=0.8)
axs[1,0].set_xlabel("Δrank"); axs[1,0].set_ylabel("cells"); axs[1,0].set_title("(c) Moon rank-shift histogram")
axs[1,1].hist((mars["rank_A_element"]-mars["rank_C_integrated"]).dropna(), bins=60,
              color="#aa5522", alpha=0.8)
axs[1,1].set_xlabel("Δrank"); axs[1,1].set_title("(d) Mars rank-shift histogram")
fig.tight_layout(); fig.savefig(FIG/"fig5_rankshift.png", dpi=300); plt.close(fig)

# ---- Figure 6: geological prospectivity vs ISRU ----
fig, axs = plt.subplots(2, 2, figsize=(9.5, 5.4))
cellmap(axs[0,0], moon, moon["C_integrated"], "viridis", "G")
axs[0,0].set_title("(a) Moon — geological prospectivity (C)")
cellmap(axs[0,1], moon, moon["D_isru"], "viridis", "P")
axs[0,1].set_title("(b) Moon — ISRU exploration priority (D)")
cellmap(axs[1,0], mars, mars["C_integrated"], "viridis", "G")
axs[1,0].set_title("(c) Mars — geological prospectivity (C)")
cellmap(axs[1,1], mars, mars["D_isru"], "viridis", "P")
axs[1,1].set_title("(d) Mars — ISRU exploration priority (D)")
fig.tight_layout(); fig.savefig(FIG/"fig6_isru.png", dpi=300); plt.close(fig)

# ---- Figure 7: robustness / uncertainty ----
fig, axs = plt.subplots(2, 2, figsize=(9.5, 5.6))
cellmap(axs[0,0], moon, moon["p_top5"], "plasma", "P(top 5%)")
axs[0,0].set_title("(a) Moon — top-priority inclusion probability (model uncertainty)")
cellmap(axs[0,1], mars, mars["p_top5"], "plasma", "P(top 5%)")
axs[0,1].set_title("(b) Mars — top-priority inclusion probability")
r = rob.copy()
SHORT = {"geometric (primary)": "primary: geometric", "weighted additive": "agg: additive",
         "bottleneck min(S,M,T)": "agg: bottleneck min", "rank-sum": "agg: rank-sum",
         "leave-S-out": "minus source domain", "leave-M-out": "minus mobilization domain",
         "leave-T-out": "minus trap/exposure domain", "minmax-norm S": "norm: min-max S",
         "exclude lowest-K quartile": "mask: low-coverage quartile"}
KEEP = list(SHORT)
for ax, pl in ((axs[1,0], "Moon"), (axs[1,1], "Mars")):
    sub = r[r.planet == pl].set_index("test").reindex(KEEP).dropna().reset_index()
    ax.barh(range(len(sub))[::-1], sub["rho"].values, color="#336699", height=0.7)
    ax.set_yticks(range(len(sub))[::-1]); ax.set_yticklabels([SHORT[t] for t in sub["test"]], fontsize=7)
    ax.axvline(x=r[(r.planet==pl)&(r.test=="geometric (primary)")]["rho"].iloc[0],
               color="k", lw=0.6, ls="--")
    ax.set_xlim(0, 1.01)
    ax.set_xlabel("Spearman ρ (element-only vs variant)")
    ax.set_title(f"({'c' if pl=='Moon' else 'd'}) {pl} — robustness across modeling choices")
fig.tight_layout(); fig.savefig(FIG/"fig7_uncertainty.png", dpi=300); plt.close(fig)

# full robustness battery -> supplement figure
fig, axs = plt.subplots(1, 2, figsize=(10, 6.5))
for ax, pl in ((axs[0], "Moon"), (axs[1], "Mars")):
    sub = r[r.planet == pl].iloc[::-1]
    ax.barh(range(len(sub)), sub["rho"].values, color="#336699", height=0.7)
    ax.set_yticks(range(len(sub))); ax.set_yticklabels(sub["test"], fontsize=6)
    ax.axvline(x=1.0, color="k", lw=0.5)
    ax.set_xlim(0, 1.05); ax.set_xlabel("Spearman ρ"); ax.set_title(pl)
fig.tight_layout(); fig.savefig(FIG/"supp_robustness_full.png", dpi=300); plt.close(fig)

# supplement: coverage + K maps + element context
fig, axs = plt.subplots(2, 2, figsize=(9.5, 5.4))
cellmap(axs[0,0], moon, moon["th_ppm"], "magma", "Th (µg/g)")
axs[0,0].set_title("(a) Moon Th")
cellmap(axs[0,1], moon, moon["k_ppm"], "magma", "K (µg/g)")
axs[0,1].set_title("(b) Moon K")
cellmap(axs[1,0], mars, mars["k_ppm"], "magma", "K (µg/g)")
axs[1,0].set_title("(c) Mars K")
cellmap(axs[1,1], mars, mars["K"], "cividis", "K (0–1)")
axs[1,1].set_title("(d) Mars knowledge completeness")
fig.tight_layout(); fig.savefig(FIG/"supp_context.png", dpi=300); plt.close(fig)
print("figures written")
