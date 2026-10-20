"""Sentinel-2 figures for six key Gilgit-Baltistan glaciers: end-of-season snow series and earliest-vs-latest imagery.

RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from shapely.geometry import shape

H = os.path.join(os.path.dirname(__file__), "..")
D, M = os.path.join(H, "data"), os.path.join(H, "maps")
R = json.load(open(os.path.join(D, "gb_results.json")))
KG = json.load(open(os.path.join(D, "key_glaciers.json")))
F = {f["properties"]["rgi_id"]: f for f in json.load(open(os.path.join(D, "rgi7_gb_outlines_30m.geojson")))["features"]}
BND = json.load(open(os.path.join(D, "rasters", "s2_bounds.json")))
INK, MUTED, GRID, BRAND, LOSS, LOSS2, GAIN = "#1f2328", "#5b636e", "#d0d4d9", "#4A7526", "#c4501b", "#7f2704", "#2f78b5"
plt.rcParams.update({"font.family": "Helvetica Neue", "font.size": 9, "axes.edgecolor": GRID, "xtick.color": MUTED, "ytick.color": MUTED})
CREDIT = "RegenX.eco Geospatial Computational Model  ·  Designed and prepared by Mr. Dinar Wali  ·  Gilgit-Baltistan assessment, 20 Oct 2026"
ORDER = ["baltoro", "biafo", "hispar", "batura", "shisper", "passu"]
S2 = R["s2_glaciers"]

# ================================================================ G8 end-of-season snow cover, six glaciers
fig, axs = plt.subplots(2, 3, figsize=(12, 6.8), sharex=True)
fig.subplots_adjust(left=.06, right=.98, top=.8, bottom=.15, hspace=.42, wspace=.22)
rec = 0
for ax, k in zip(axs.flat, ORDER):
    d = S2[k]; ys = sorted(int(y) for y in d["years"]); v = [d["years"][str(y)]["snow_frac"] * 100 for y in ys]
    low = int(d["lowest_snow_year"]); rec += low in (2025, 2026)
    ax.bar(ys, v, color=[LOSS if y == low else "#8fbfe0" for y in ys], width=.72)
    for y, x in zip(ys, v):
        ax.text(y, x + .8, f"{d['years'][str(y)]['snowline_m'] or '–'}", ha="center", fontsize=6.3, color=MUTED, rotation=90, va="bottom")
    lo = min(v); ax.set_ylim(max(0, lo - 15), min(100, max(v) + 14))
    t = d["trend_snow_frac_per_yr"]
    note = " · clean ice reads as snow" if k == "passu" else ""
    ax.set_title(f"{KG[k]['name'].replace(' Glacier','')}: lowest {low}; trend {t['ols'] * 100:+.1f} pts/yr, p {t['mk_p']:.2f}{note}", loc="left", fontsize=8.4, weight="bold", color=INK)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=.4); ax.set_ylabel("% snow-covered", fontsize=8)
fig.text(.04, .955, "End-of-summer snow on six key glaciers: 2025–26 are the lowest since 2017–19", fontsize=15, weight="bold", color=INK)
fig.text(.04, .92, f"Sentinel-2 L2A scene nearest 1 September each year. {rec} of 6 glaciers have their lowest snow cover of the Sentinel-2 record in 2025 or 2026 (Passu's values mix clean ice with snow); "
         "only Hispar's decline is statistically significant over this short record.\nSmall numbers above bars = snow-line altitude (m, Copernicus GLO-30): the lowest 100 m band still ≥ 50 % snow.",
         fontsize=8.8, color=MUTED, va="top")
fig.text(0.012, 0.045, "Data: Copernicus Sentinel-2 L2A (COPERNICUS/S2_SR_HARMONIZED via Google Earth Engine), same-date tiles mosaicked, in-outline coverage ≥ 90 %, cloud ≤ 10 %; "
         "NDSI = (B3−B11)/(B3+B11) ≥ 0.40; outlines RGI 7.0. L2A coverage over GB is sparse before 2019; years without a qualifying scene are omitted.", fontsize=6.7, color=MUTED)
fig.text(0.012, 0.015, CREDIT, fontsize=7.6, color=BRAND, weight="bold")
fig.savefig(os.path.join(M, "G8_s2_end_of_season_snow.png"), dpi=220); plt.close(fig)

# ================================================================ G9 earliest vs latest true colour with RGI outline
for part, keys in [("a", ["baltoro", "biafo", "hispar"]), ("b", ["batura", "shisper", "passu"])]:
    fig, axs = plt.subplots(len(keys), 2, figsize=(12, 4.6 * len(keys)))
    fig.subplots_adjust(left=.02, right=.98, top=.9, bottom=.06, hspace=.16, wspace=.04)
    for row, k in zip(axs, keys):
        d = S2[k]["years"]; ys = sorted(int(y) for y in d)
        w, s, e, n = BND[k]
        g = shape(F[KG[k]["rgi_id"]]["geometry"])
        for ax, y in zip(row, [ys[0], ys[-1]]):
            im = Image.open(os.path.join(D, "rasters", f"s2_{k}_{y}.png")).convert("RGB")
            ax.imshow(im, extent=[w, e, s, n])
            for p in [q for q in getattr(g, "geoms", [g]) if q.geom_type == "Polygon"]:
                x_, y_ = p.exterior.xy; ax.plot(x_, y_, color="#ffe14d", lw=1.1)
            ax.set_xlim(w, e); ax.set_ylim(s, n); ax.set_aspect(1 / np.cos(np.radians((s + n) / 2)))
            ax.set_xticks([]); ax.set_yticks([])
            r = d[str(y)]
            ax.set_title(f"{KG[k]['name']} · {r['scene']} · snow {r['snow_frac'] * 100:.0f} % · snow line {r['snowline_m']} m", loc="left", fontsize=9, weight="bold", color=INK)
    fig.text(.02, .955, "Sentinel-2 true colour at the end of summer: first qualifying year vs 2026", fontsize=14, weight="bold", color=INK)
    fig.text(.02, .935, "Yellow line: RGI 7.0 outline (mapped 1997–2002). Same processing on both dates.", fontsize=9, color=MUTED, va="top")
    fig.text(0.012, 0.025, "Contains modified Copernicus Sentinel-2 data (L2A, B4/B3/B2, 10 m), via Google Earth Engine.", fontsize=6.8, color=MUTED)
    fig.text(0.012, 0.008, CREDIT, fontsize=7.6, color=BRAND, weight="bold")
    fig.savefig(os.path.join(M, f"G9{part}_s2_then_now.jpg"), dpi=160, pil_kwargs={"quality": 86}); plt.close(fig)
print("s2 figures written; record-low in 2025/26:", rec)
