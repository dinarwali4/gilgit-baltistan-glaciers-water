"""Gilgit-Baltistan figures: glacier change, storage, snow, climate and projections.

RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, Normalize
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from PIL import Image
from shapely.geometry import shape

H = os.path.join(os.path.dirname(__file__), "..")
D, M = os.path.join(H, "data"), os.path.join(H, "maps")
os.makedirs(M, exist_ok=True)
WS = os.path.join(H, "data", "boundaries")  # geoBoundaries gbOpen PAK ADM1/ADM2
R = json.load(open(os.path.join(D, "gb_results.json")))
MC = json.load(open(os.path.join(D, "glacier_mass_change.json")))
INK, MUTED, GRID, BRAND = "#1f2328", "#5b636e", "#d0d4d9", "#4A7526"
LOSS, LOSS2, GAIN, NEUT = "#c4501b", "#7f2704", "#2f78b5", "#9aa3ab"
DIV = LinearSegmentedColormap.from_list("div", ["#7f2704", "#c4501b", "#f2a374", "#ececec", "#8fbfe0", "#2f78b5", "#0b3c6e"])
plt.rcParams.update({"font.family": "Helvetica Neue", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED})
CREDIT = "RegenX.eco Geospatial Computational Model  ·  Designed and prepared by Mr. Dinar Wali  ·  Gilgit-Baltistan assessment, 20 Oct 2026"
BB = [72.4, 34.45, 77.85, 37.15]
adm1 = json.load(open(os.path.join(WS, "pak_ADM1.geojson")))["features"]
GB = shape([f for f in adm1 if f["properties"]["shapeName"] == "Gilgit-Baltistan"][0]["geometry"])
adm2 = json.load(open(os.path.join(WS, "pak_ADM2.geojson")))["features"]
DIST = {f["properties"]["shapeName"]: shape(f["geometry"]) for f in adm2 if GB.buffer(0.01).contains(shape(f["geometry"]).representative_point())}


def footer(fig, src):
    fig.text(0.012, 0.042, src, fontsize=6.7, color=MUTED, ha="left", va="bottom", wrap=True)
    fig.text(0.012, 0.012, CREDIT, fontsize=7.6, color=BRAND, ha="left", va="bottom", weight="bold")


def heading(fig, title, sub, y=0.955):
    fig.text(0.04, y, title, fontsize=15, weight="bold", color=INK)
    fig.text(0.04, y - 0.035, sub, fontsize=9, color=MUTED, va="top")


def lines(ax, g, color=INK, lw=0.8, ls="-"):
    for p in getattr(g, "geoms", [g]):
        x, y = p.exterior.xy; ax.plot(x, y, color=color, lw=lw, ls=ls)


def style(ax):
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=.4)


P = R["glaciers"]["periods"]
full = P["2000-01-01_2020-01-01"]

# ================================================================ G1 glacier elevation change map
fig = plt.figure(figsize=(12, 7.6))
ax = fig.add_axes([0.04, 0.11, 0.74, 0.76])
hs = Image.open(os.path.join(D, "rasters", "hillshade.png")).convert("RGB")
dh = Image.open(os.path.join(D, "rasters", "dhdt.png")).convert("RGBA")
ext = [BB[0], BB[2], BB[1], BB[3]]
ax.imshow(hs, extent=ext, alpha=0.85)
ax.imshow(dh, extent=ext)
lines(ax, GB, "#1f2328", 1.6)
for n, g in DIST.items():
    lines(ax, g, "#5b636e", 0.5, "--")
    c = g.representative_point()
    ax.text(c.x, c.y, n, fontsize=7.5, color=INK, ha="center", style="italic",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.6))
ax.add_patch(plt.Rectangle((76.85, 34.95), 0.95, 0.85, fill=False, ec="#5b636e", lw=1.0, ls=":"))
ax.text(77.32, 34.88, "Siachen sector (administered by India)", fontsize=7, color=MUTED, ha="center", va="top", bbox=dict(fc="white", ec="none", alpha=.7, pad=1))
for r in sorted(MC["largest"], key=lambda r: -r["area_km2"])[:12]:
    nm = (r["glac_name"] or "").replace("IN5Q151B0013 ", "").replace("IN5Q153E0011 ", "")
    if not nm or "Siachen" in nm or "Rimo" in nm: continue
    off = {"Hispar Glacier": (-40, -62), "Khurdopin Glacier": (-105, 6), "Biafo Glacier": (-95, -12), "Panmah Glacier": (40, -48),
           "Braldu Glacier": (14, 12), "Batura Glacier": (10, 12), "Baltoro Glacier": (10, 14), "Virjerab Glacier": (16, 18)}.get(nm, (8, 8))
    ax.annotate(f"{nm.replace(' Glacier','')}\n{r['dhdt_2000_2019']:+.2f} m/yr", (r["cenlon"], r["cenlat"]), xytext=off, textcoords="offset points",
                fontsize=7, color=INK, arrowprops=dict(arrowstyle="-", lw=.5, color=INK),
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=GRID, lw=.5, alpha=.9))
ax.set_xlim(BB[0], BB[2]); ax.set_ylim(BB[1], BB[3]); ax.set_aspect(1 / np.cos(np.radians(35.8)))
ax.set_xticks(np.arange(73, 78, 1)); ax.set_yticks(np.arange(35, 37.5, .5))
ax.set_xticklabels([f"{x}°E" for x in range(73, 78)], fontsize=7); ax.set_yticklabels([f"{y:.1f}°N" for y in np.arange(35, 37.5, .5)], fontsize=7)
cax = fig.add_axes([0.8, 0.3, 0.014, 0.4])
cb = fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(-2, 2), cmap=DIV), cax=cax); cb.outline.set_visible(False)
cb.set_label("Glacier surface elevation change 2000–2019 (m/yr)", fontsize=8)
g20 = full["Gilgit-Baltistan"]; x20 = full["GB excl. Siachen sector"]
side = (f"{R['glaciers']['n']:,} glaciers · {R['glaciers']['area_km2_rgi']:,.0f} km²\n(RGI 7.0, centroid in GB)\n\n"
        f"2000–2019 mean change\n{g20['dhdt_m_yr']:+.3f} m/yr surface\n{g20['mwe_yr']:+.3f} m w.e./yr\n= {g20['gt_yr']:+.2f} Gt/yr of water\n\n"
        f"Excluding Siachen sector\n{x20['mwe_yr']:+.3f} m w.e./yr\n= {x20['gt_yr']:+.2f} Gt/yr")
fig.text(0.86, 0.3, side, fontsize=8.6, color=INK, va="bottom", linespacing=1.35)
heading(fig, "Gilgit-Baltistan's glaciers are thinning, and the loss is speeding up",
        "Blue = thickening, brown = thinning. Most large Karakoram glaciers held near balance in 2000–2019 (the 'Karakoram anomaly'), "
        "but loss grew in every five-year period to 2015–19.")
footer(fig, "Data: Hugonnet et al. 2021 (Nature 592:726) glacier elevation change, 100 m, ASTER/ArcticDEM time series, via GEE community catalogue; "
       "RGI 7.0 outlines (GLIMS/NSIDC 0770); Copernicus GLO-30 hillshade; geoBoundaries ADM1/ADM2. Mass = dh/dt × area × 850 kg/m³ (Huss 2013).")
fig.savefig(os.path.join(M, "G1_glacier_elevation_change_2000_2019.png"), dpi=220); plt.close(fig)

# ================================================================ G2 acceleration by period + districts
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1, 1.25]})
fig.subplots_adjust(left=.07, right=.98, top=.78, bottom=.2, wspace=.32)
five = ["2000-01-01_2005-01-01", "2005-01-01_2010-01-01", "2010-01-01_2015-01-01", "2015-01-01_2020-01-01"]
lab = ["2000–04", "2005–09", "2010–14", "2015–19"]
xg = np.arange(4)
for off, reg, col, nm in [(-0.19, "Gilgit-Baltistan", "#0e2f3a", "GB (geoBoundaries)"), (0.19, "GB excl. Siachen sector", "#76AD41", "GB excl. Siachen sector")]:
    v = [P[p][reg]["mwe_yr"] for p in five]
    a1.bar(xg + off, v, 0.36, color=col, label=nm)
    for x, y in zip(xg + off, v):
        a1.text(x, y + (0.006 if y >= 0 else -0.006), f"{y:+.3f}", ha="center", va="bottom" if y >= 0 else "top", fontsize=7.5, color=INK)
a1.axhline(0, color=INK, lw=.7); a1.set_xticks(xg); a1.set_xticklabels(lab); style(a1)
a1.set_ylabel("Mass balance (m water equivalent per year)"); a1.legend(frameon=False, fontsize=8, loc="lower left")
a1.set_title("By five-year period", loc="left", fontsize=10, weight="bold", color=INK)
dd = sorted(R["glaciers"]["districts_2000_2019"].items(), key=lambda kv: kv[1]["gt_yr"])
names = [k for k, v in dd]; gt = [v["gt_yr"] for k, v in dd]; mwe = [v["mwe_yr"] for k, v in dd]
yb = np.arange(len(names))
a2.barh(yb, gt, color=[LOSS if g < 0 else GAIN for g in gt], height=.62)
for y_, g_, m_, n_ in zip(yb, gt, mwe, names):
    a2.text(g_ + (0.01 if g_ >= 0 else -0.01), y_, f"{g_:+.2f} Gt/yr  ({m_:+.2f} m w.e.)", va="center", ha="left" if g_ >= 0 else "right", fontsize=7.5, color=INK)
a2.set_yticks(yb); a2.set_yticklabels([f"{n} ({R['glaciers']['districts_2000_2019'][n]['glacier_area_km2']:,.0f} km²)" for n in names], fontsize=8)
a2.axvline(0, color=INK, lw=.7); a2.set_xlim(min(gt) * 1.9, max(0.09, max(gt) * 4.5))
for s in ["top", "right"]: a2.spines[s].set_visible(False)
a2.set_xlabel("Glacier mass change 2000–2019 (Gt of water per year)")
a2.set_title("By district, 2000–2019", loc="left", fontsize=10, weight="bold", color=INK)
acc = R["glaciers"]["acceleration_Gilgit-Baltistan"]
heading(fig, "Glacier loss accelerated in every five-year period since 2000",
        f"GB glaciers went from slight gain (+0.043 m w.e./yr, 2000–04) to loss (−0.120 m w.e./yr, 2015–19): "
        f"{acc['mwe_per_yr_per_decade']:+.2f} m w.e./yr per decade. Ghanche includes the Siachen sector.", y=.95)
footer(fig, "Data: Hugonnet et al. 2021 elevation change (100 m), masked to RGI 7.0 glaciers with centroid in GB; 92 % of glacier area has valid data. "
       "Per-pixel uncertainty maps are not averaged here; period differences, not single-period values, carry the signal.")
fig.savefig(os.path.join(M, "G2_glacier_mass_balance_periods_districts.png"), dpi=220); plt.close(fig)

# ================================================================ G3 GRACE three solutions
fig, ax = plt.subplots(figsize=(12, 6.0))
fig.subplots_adjust(left=.07, right=.97, top=.8, bottom=.17)
cols = {"CSR": "#0e2f3a", "GFZ": "#2f78b5", "JPL": "#76AD41"}
for k in ["CSR", "GFZ", "JPL"]:
    a = R["grace"][k]["annual"]; ys = sorted(int(y) for y in a)
    ax.plot(ys, [a[str(y)] for y in ys], "-o", color=cols[k], lw=2, ms=4, label=f"{R['grace'][k]['name']}")
ax.axvspan(2017.5, 2018.5, color="#eef0f2"); ax.text(2018, ax.get_ylim()[1] if False else 6, "mission\ngap", ha="center", fontsize=7, color=MUTED)
ax.axhline(0, color=GRID, lw=.8); style(ax)
ax.set_ylabel("Annual-mean storage anomaly vs 2004–2009 (cm of water)")
ax.legend(frameon=False, fontsize=8, loc="lower left")
c, g_ = R["grace"]["CSR"], R["grace"]["GFZ"]
ax.annotate(f"2026 (Jan–Aug): CSR {c['annual']['2026']:+.1f} cm, GFZ {g_['annual']['2026']:+.1f} cm", (2026, c["annual"]["2026"]), xytext=(2017.6, -46),
            fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", lw=.6, color=INK), bbox=dict(fc="white", ec=GRID, pad=3))
heading(fig, "Measured from orbit: Gilgit-Baltistan's stored water fell sharply after 2023",
        f"Three independent GRACE solutions agree to 2024 (2024: CSR {c['annual']['2024']:+.1f}, GFZ {g_['annual']['2024']:+.1f}, JPL {R['grace']['JPL']['annual']['2024']:+.1f} cm). "
        f"Since 2018 the trend is {g_['trend_fo']['cm_yr']:+.1f} (GFZ) to {c['trend_fo']['cm_yr']:+.1f} (CSR) cm/yr — "
        f"{g_['trend_fo']['km3_yr']:+.1f} to {c['trend_fo']['km3_yr']:+.1f} km³/yr.", y=.95)
footer(fig, "Data: UT-CSR RL06.3 mascons (0.25° grid, to Aug 2026); GFZ GravIS RL06 v0006 (1°, to Aug 2026); NASA-JPL RL06.3 CRI mascons (to Sep 2024). "
       "Area-weighted over the GB polygon (69,078 km²), seasonal cycle removed. GB spans ~1–2 GRACE mascons: single months are noisy, read annual means.")
fig.savefig(os.path.join(M, "G3_grace_gb_three_solutions.png"), dpi=220); plt.close(fig)

# ================================================================ G4 High Mountain Asia anomaly map
A = np.load(os.path.join(D, "hma_anomaly_2025_26.npz"))
fig = plt.figure(figsize=(12, 6.8))
ax = fig.add_axes([0.05, 0.14, 0.8, 0.68])
im = ax.imshow(A["d"], extent=[A["lon"][0] - .125, A["lon"][-1] + .125, A["lat"][0] - .125, A["lat"][-1] + .125], origin="lower",
               cmap=DIV, norm=TwoSlopeNorm(0, -40, 40), interpolation="nearest")
for f in adm1:
    lines(ax, shape(f["geometry"]), INK, .5)
lines(ax, GB, INK, 1.8)
ax.set_xlim(62, 100); ax.set_ylim(25, 45); ax.set_aspect(1 / np.cos(np.radians(35)))
for nm, (x, y, t) in {"Gilgit-Baltistan": (74.8, 36.2, "−34 cm"), "Ladakh": (77.5, 33.8, "−30 cm"), "W Kunlun": (79, 36.8, "−3 cm"),
                      "C Tibet": (88.5, 32.5, "0 cm"), "Nepal Himalaya": (85, 28.7, "−15 cm"), "Hindu Kush": (69.8, 35.5, "−6 cm"), "Tien Shan": (80, 41.5, "−12 cm"), "Pamir": (73, 39.4, "−24 cm"), "E Himalaya": (94.5, 31.2, "−21 cm")}.items():
    ax.text(x, y, f"{nm}\n{t}", fontsize=7.5, ha="center", color=INK, bbox=dict(fc="white", ec="none", alpha=.7, pad=1.5))
cb = fig.colorbar(im, cax=fig.add_axes([0.87, 0.25, 0.014, 0.45])); cb.outline.set_visible(False)
cb.set_label("2025–26 minus 2019–23 (cm of water, deseasonalised)", fontsize=8)
heading(fig, "The 2025–26 drop follows the Pamir–Karakoram–western Himalaya belt",
        "A test of whether the GB decline is a satellite artefact: it is not uniform. Gilgit-Baltistan (−34 cm), Ladakh (−30) and the Pamir (−24) fall most; "
        "western Kunlun and central Tibet barely move.", y=.95)
footer(fig, "Data: UT-CSR RL06.3 mascons, monthly 2019–2026; per-cell monthly climatology 2004–2022 removed; mean Jan 2025–Aug 2026 minus mean 2019–2023. "
       "Box values are area means of the named boxes.")
fig.savefig(os.path.join(M, "G4_hma_anomaly_2025_26.png"), dpi=220); plt.close(fig)

# ================================================================ G5 snow
sn = R["snow"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.4))
fig.subplots_adjust(left=.07, right=.98, top=.78, bottom=.2, wspace=.25)
ys = sorted(int(y) for y in sn["aug_on_glaciers"]); v = [sn["aug_on_glaciers"][str(y)] * 100 for y in ys]
low3 = {int(y) for y, _ in sn["aug_on_glaciers_lowest3"]}
a1.bar(ys, v, color=[LOSS if y in low3 else "#8fbfe0" for y in ys], width=.75)
tr = sn["trend_aug_glacier"]; xx = np.array(ys)
a1.plot(xx, (np.mean(v) + tr["ols"] * 100 * (xx - xx.mean())), color=INK, lw=1.2, ls="--")
a1.set_ylim(40, 75); style(a1); a1.set_ylabel("% of glacier area snow-covered (August mean)")
a1.set_title(f"August snow on glaciers: {tr['ols'] * 100:+.2f} pts/yr (MK p = {tr['mk_p']:.2f})", loc="left", fontsize=10, weight="bold", color=INK)
for y in low3:
    a1.text(y, sn["aug_on_glaciers"][str(y)] * 100 + .6, str(y), ha="center", fontsize=7, color=LOSS2)
ys2 = sorted(int(y) for y in sn["amj"]); cl = sn["amj_clim_2001_2020"]
v2 = [(sn["amj"][str(y)] / cl - 1) * 100 for y in ys2]
a2.bar(ys2, v2, color=[GAIN if x >= 0 else LOSS for x in v2], width=.75)
a2.axhline(0, color=INK, lw=.7); style(a2); a2.set_ylabel("% vs 2001–2020 mean")
a2.set_title(f"Spring (Apr–Jun) snow cover over GB: no trend (MK p = {sn['trend_amj']['mk_p']:.2f})", loc="left", fontsize=10, weight="bold", color=INK)
heading(fig, "Less snow is left on the ice each August; seasonal snow shows no trend",
        "The three barest Augusts on the glaciers are 2022, 2024 and 2025. Spring snow cover varies year to year without a trend; "
        f"2025 was {sn['amj_2025_pct']:+.0f} % below normal, 2026 normal.", y=.95)
footer(fig, "Data: MODIS Terra MOD10A1 v6.1 (500 m, daily), snow = NDSI snow cover ≥ 40, cloud-free observations only; monthly per-pixel snow frequency, "
       "area mean over GB or over RGI 7.0 glacier area. Snow extent, not snow water equivalent.")
fig.savefig(os.path.join(M, "G5_snow_cover_modis.png"), dpi=220); plt.close(fig)

# ================================================================ G6 climate
cl_ = R["climate"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.4))
fig.subplots_adjust(left=.07, right=.98, top=.78, bottom=.2, wspace=.25)
ys = sorted(int(y) for y in cl_["jja_t"]); base = cl_["jja_t_clim_2001_2020"]
v = [cl_["jja_t"][str(y)] - base for y in ys]
a1.bar(ys, v, color=[LOSS if x >= 0 else GAIN for x in v], width=.75); a1.axhline(0, color=INK, lw=.7); style(a1)
a1.set_ylabel("Summer (Jun–Aug) temperature vs 2001–2020 (°C)")
a1.set_title(f"Summer temperature: {cl_['trend_jja_t']['ols'] * 10:+.2f} °C/decade (p = {cl_['trend_jja_t']['ols_p']:.2f})", loc="left", fontsize=10, weight="bold", color=INK)
a1.text(2025, v[ys.index(2025)] + .05, "2025\nwarmest", ha="center", fontsize=7, color=LOSS2)
ys2 = sorted(int(y) for y in cl_["winter_precip_oct_mar"]); b2 = cl_["winter_precip_clim_2001_2020"]
v2 = [(cl_["winter_precip_oct_mar"][str(y)] / b2 - 1) * 100 for y in ys2]
a2.bar(ys2, v2, color=[GAIN if x >= 0 else LOSS for x in v2], width=.75); a2.axhline(0, color=INK, lw=.7); style(a2)
a2.set_ylabel("% vs 2001–2020 mean"); a2.set_xlabel("Winter ending in year (Oct–Mar)")
a2.set_title(f"Winter precipitation (Oct–Mar): no trend; normal {b2:.0f} mm", loc="left", fontsize=10, weight="bold", color=INK)
heading(fig, "Warmer summers, not less snowfall, are driving the melt",
        "ERA5-Land over GB: 2025 was the warmest summer in the record. Winter precipitation shows no trend; the driest winters were 2001, 2018 and 2024.", y=.95)
footer(fig, "Data: ECMWF ERA5-Land monthly (0.1°), area mean over GB. ERA5-Land precipitation is a model estimate with known biases in high mountains; "
       "used here for year-to-year variation, not absolute totals.")
fig.savefig(os.path.join(M, "G6_climate_era5.png"), dpi=220); plt.close(fig)

# ================================================================ G7 CMIP6 projections
cm = R["cmip6"]
fig = plt.figure(figsize=(12, 5.8))
ax = fig.add_axes([0.07, 0.18, 0.56, 0.6])
for scen, col, nm in [("historical", NEUT, "Historical"), ("ssp245", GAIN, "SSP2-4.5"), ("ssp585", LOSS, "SSP5-8.5")]:
    s = np.array(cm["jja_anomaly_series"][scen])
    ax.fill_between(s[:, 0], s[:, 2], s[:, 3], color=col, alpha=.18, lw=0)
    ax.plot(s[:, 0], s[:, 1], color=col, lw=2, label=nm)
e = R["climate"]["jja_t"]; eb = np.mean([v for y, v in e.items() if 1995 <= int(y) <= 2014]) if any(1995 <= int(y) <= 2014 for y in e) else None
ax.axhline(0, color=GRID, lw=.8); style(ax); ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.set_ylabel("Summer temperature change vs 1995–2014 (°C)"); ax.set_xlim(1985, 2100)
ax.set_title(f"{len(cm['models'])}-model median and 10–90 % range", loc="left", fontsize=10, weight="bold", color=INK)
tx = fig.add_axes([0.67, 0.18, 0.31, 0.6]); tx.axis("off")
rows = [["", "2041–60", "2081–2100"]]
for scen, nm in [("ssp245", "SSP2-4.5"), ("ssp585", "SSP5-8.5")]:
    p = cm["projections"][scen]
    rows.append([f"{nm} summer °C", f"{p['2041-2060']['dT_median']:+.1f} ({p['2041-2060']['dT_min']:+.1f} to {p['2041-2060']['dT_max']:+.1f})",
                 f"{p['2081-2100']['dT_median']:+.1f} ({p['2081-2100']['dT_min']:+.1f} to {p['2081-2100']['dT_max']:+.1f})"])
    rows.append([f"{nm} precip %", f"{p['2041-2060']['dP_pct_median']:+.0f} ({p['2041-2060']['dP_pct_min']:+.0f} to {p['2041-2060']['dP_pct_max']:+.0f})",
                 f"{p['2081-2100']['dP_pct_median']:+.0f} ({p['2081-2100']['dP_pct_min']:+.0f} to {p['2081-2100']['dP_pct_max']:+.0f})"])
tb = tx.table(cellText=rows, loc="center", cellLoc="left", colWidths=[.36, .32, .32])
tb.auto_set_font_size(False); tb.set_fontsize(8.2); tb.scale(1, 2.0)
for (i, j), c_ in tb.get_celld().items():
    c_.set_edgecolor(GRID); c_.set_text_props(color=INK, weight="bold" if i == 0 or j == 0 else "normal")
tx.text(0, .02, "Median (model range), each model vs its own 1995–2014.", fontsize=7.5, color=MUTED, transform=tx.transAxes)
heading(fig, "Going forward: 1.3–1.7 °C warmer summers by mid-century",
        f"NASA NEX-GDDP-CMIP6 over GB. Models reproduce the observed 2000–2025 warming "
        f"(ERA5-Land {R['test_cmip6_vs_era5']['era5_jja_trend_C_per_decade']:+.2f} °C/decade vs model median {R['test_cmip6_vs_era5']['model_jja_trend_C_per_decade_median']:+.2f}). "
        "Precipitation projections disagree even on sign before 2060.", y=.95)
footer(fig, "Data: NASA NEX-GDDP-CMIP6 (0.25°, bias-corrected, daily) via Google Earth Engine; models: " + ", ".join(cm["models"]) + ". "
       "Projections are model outputs (modelled), not forecasts.")
fig.savefig(os.path.join(M, "G7_cmip6_projections.png"), dpi=220); plt.close(fig)
print("figures written")
