"""Gilgit-Baltistan glaciers & water security: combine all layers, run the validation tests.

RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali.
Inputs (data/): grace_gb.json, glacier_mass_change.json, snow_climate.json, cmip6_gb.json, s2_glacier_snow.json
Output: data/gb_results.json (every number quoted in the report and deck)
"""
import os, json
import numpy as np
from scipy import stats

H = os.path.join(os.path.dirname(__file__), "..")
D = os.path.join(H, "data")
J = lambda f: json.load(open(os.path.join(D, f)))
G, M, SC, CM = J("grace_gb.json"), J("glacier_mass_change.json"), J("snow_climate.json"), J("cmip6_gb.json")
S2 = J("s2_glacier_snow.json") if os.path.exists(os.path.join(D, "s2_glacier_snow.json")) else {}
R = {}


def trend(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    k = ~np.isnan(y); x, y = x[k], y[k]
    lr = stats.linregress(x, y); tau, p = stats.kendalltau(x, y); ts = stats.theilslopes(y, x)
    return {"ols": lr.slope, "ols_p": lr.pvalue, "sen": ts[0], "mk_p": p, "n": int(len(x))}


# ---------------------------------------------------------------- MODIS snow
mod = sorted(SC["modis"], key=lambda r: (r["y"], r["m"]))
by = {}
for r in mod:
    by.setdefault(r["y"], {})[r["m"]] = r
wy = {}  # water year Oct(y-1)-Sep(y)
for y in range(2002, 2027):
    months = [(y - 1, m) for m in (10, 11, 12)] + [(y, m) for m in range(1, 10)]
    v = [by.get(a, {}).get(m, {}).get("snow_frac") for a, m in months]
    if all(x is not None for x in v):
        wy[y] = float(np.mean(v))
winter = {y: float(np.mean([by[y][m]["snow_frac"] for m in (1, 2, 3)])) for y in by if all(m in by[y] for m in (1, 2, 3))}
spring = {y: float(np.mean([by[y][m]["snow_frac"] for m in (4, 5, 6)])) for y in by if all(m in by[y] for m in (4, 5, 6))}
aug_gl = {y: by[y][8]["glacier_snow_frac"] for y in by if 8 in by[y]}
R["snow"] = {"water_year_mean": wy, "jfm": winter, "amj": spring, "aug_on_glaciers": aug_gl,
             "trend_water_year": trend(list(wy), list(wy.values())), "trend_jfm": trend(list(winter), list(winter.values())),
             "trend_amj": trend(list(spring), list(spring.values())), "trend_aug_glacier": trend(list(aug_gl), list(aug_gl.values()))}
for k, d in [("amj", spring), ("jfm", winter), ("aug_on_glaciers", aug_gl), ("water_year_mean", wy)]:
    vals = sorted(d.items(), key=lambda kv: kv[1])
    R["snow"][k + "_lowest3"] = vals[:3]
    clim = np.mean([v for y, v in d.items() if 2001 <= y <= 2020])
    R["snow"][k + "_clim_2001_2020"] = float(clim)
    R["snow"][k + "_2025_pct"] = (d[2025] / clim - 1) * 100 if 2025 in d else None
    R["snow"][k + "_2026_pct"] = (d[2026] / clim - 1) * 100 if 2026 in d else None

# ---------------------------------------------------------------- ERA5-Land climate
e5 = {r["t"]: r for r in SC["era5"]}
jja = {}; wyp = {}
for y in range(2000, 2027):
    t = [e5.get(f"{y}-{m:02d}", {}).get("t2m_c") for m in (6, 7, 8)]
    if all(v is not None for v in t): jja[y] = float(np.mean(t))
    ps = [e5.get(f"{y - 1}-{m:02d}" if m >= 10 else f"{y}-{m:02d}", {}).get("pr_mm") for m in (10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9)]
    if all(v is not None for v in ps): wyp[y] = float(sum(ps))
win_p = {y: float(sum(e5[f"{y - 1}-{m:02d}" if m >= 10 else f"{y}-{m:02d}"]["pr_mm"] for m in (10, 11, 12, 1, 2, 3)))
         for y in range(2001, 2027) if all((f"{y - 1}-{m:02d}" if m >= 10 else f"{y}-{m:02d}") in e5 for m in (10, 11, 12, 1, 2, 3))}
R["climate"] = {"jja_t": jja, "trend_jja_t": trend(list(jja), list(jja.values())), "wy_precip": wyp, "trend_wy_precip": trend(list(wyp), list(wyp.values())),
                "winter_precip_oct_mar": win_p, "winter_precip_clim_2001_2020": float(np.mean([v for y, v in win_p.items() if y <= 2020])),
                "jja_t_clim_2001_2020": float(np.mean([v for y, v in jja.items() if 2001 <= y <= 2020]))}
R["climate"]["warmest_jja"] = sorted(jja.items(), key=lambda kv: -kv[1])[:4]
R["climate"]["driest_winters"] = sorted(win_p.items(), key=lambda kv: kv[1])[:4]

# ---------------------------------------------------------------- GRACE
R["grace"] = {k: {kk: v[kk] for kk in ["name", "first", "last", "trend_all", "trend_grace", "trend_fo", "annual", "mom_abs_change_median_cm"] + (["r_vs_csr_annual"] if "r_vs_csr_annual" in v else [])} for k, v in G.items()}

# ---------------------------------------------------------------- glaciers (Hugonnet)
P = M["periods"]
R["glaciers"] = {"n": M["n_glaciers"], "area_km2_rgi": M["area_km2"],
                 "periods": {p: {r: {k: v for k, v in P[p][r].items() if k != "sums"} for r in ["Gilgit-Baltistan", "GB excl. Siachen sector", "Siachen sector"]} for p in P},
                 "districts_2000_2019": {d: {k: v for k, v in P["2000-01-01_2020-01-01"][d].items() if k != "sums"} for d in P["2000-01-01_2020-01-01"] if d not in ("Gilgit-Baltistan", "GB excl. Siachen sector", "Siachen sector")}}
five = ["2000-01-01_2005-01-01", "2005-01-01_2010-01-01", "2010-01-01_2015-01-01", "2015-01-01_2020-01-01"]
mid = [2002.5, 2007.5, 2012.5, 2017.5]
for reg in ["Gilgit-Baltistan", "GB excl. Siachen sector"]:
    v = [P[p][reg]["mwe_yr"] for p in five]
    R["glaciers"]["acceleration_" + reg] = {"mwe_per_yr_per_decade": float(np.polyfit(mid, v, 1)[0] * 10), "monotonic_decline": all(np.diff(v) < 0)}

# ---------------------------------------------------------------- consistency test: glacier mass loss vs GRACE (2010-2019)
csr = G["CSR"]["annual"]
yrs = [y for y in range(2010, 2020) if str(y) in csr]
gr = np.polyfit(yrs, [csr[str(y)] for y in yrs], 1)[0]  # cm/yr over GB
R["test_grace_vs_glaciers"] = {"grace_csr_2010_2019_cm_yr": gr, "grace_km3_yr": gr * 1e-5 * 69078.1,
                               "glacier_2010_2019_gt_yr": P["2010-01-01_2020-01-01"]["Gilgit-Baltistan"]["gt_yr"],
                               "years_used": yrs,
                               "note": "GRACE annual means exclude 2017-2018 (mission gap); glaciers are one component of GRACE total storage"}

# ---------------------------------------------------------------- CMIP6 projections
models = sorted({k.split("|")[0] for k in CM})
proj = {}
for scen in ["ssp245", "ssp585"]:
    dT = {"2021-2040": [], "2041-2060": [], "2081-2100": []}; dP = {k: [] for k in dT}
    for m in models:
        h = {int(r[0]): r for r in CM.get(f"{m}|historical", [])}
        f = {int(r[0]): r for r in CM.get(f"{m}|{scen}", [])}
        if not h or not f: continue
        bt = np.mean([h[y][1] for y in range(1995, 2015)]); bp = np.mean([h[y][2] for y in range(1995, 2015)])
        for per in dT:
            a, b = map(int, per.split("-"))
            dT[per].append(np.mean([f[y][1] for y in range(a, b + 1)]) - bt)
            dP[per].append((np.mean([f[y][2] for y in range(a, b + 1)]) / bp - 1) * 100)
    proj[scen] = {per: {"dT_median": float(np.median(dT[per])), "dT_min": float(np.min(dT[per])), "dT_max": float(np.max(dT[per])),
                        "dP_pct_median": float(np.median(dP[per])), "dP_pct_min": float(np.min(dP[per])), "dP_pct_max": float(np.max(dP[per])),
                        "n_models": len(dT[per])} for per in dT}
# annual ensemble series for charts (anomaly vs each model's 1995-2014)
series = {}
for scen in ["historical", "ssp245", "ssp585"]:
    yrs_all = range(1985, 2015) if scen == "historical" else range(2015, 2101)
    rows = []
    for y in yrs_all:
        vals = []
        for m in models:
            h = {int(r[0]): r for r in CM.get(f"{m}|historical", [])}
            s = {int(r[0]): r for r in CM.get(f"{m}|{scen}", [])}
            if y in s and h:
                vals.append(s[y][1] - np.mean([h[k][1] for k in range(1995, 2015)]))
        rows.append([y, float(np.median(vals)), float(np.percentile(vals, 10)), float(np.percentile(vals, 90))])
    series[scen] = rows
R["cmip6"] = {"models": models, "baseline": "1995-2014 per model", "projections": proj, "jja_anomaly_series": series}
# validation: modelled 2000-2025 JJA warming (historical+ssp245) vs ERA5-Land
mt = []
for m in models:
    h = {int(r[0]): r for r in CM.get(f"{m}|historical", [])}; f = {int(r[0]): r for r in CM.get(f"{m}|ssp245", [])}
    ys = list(range(2000, 2026)); v = [(h.get(y) or f.get(y))[1] for y in ys]
    mt.append(np.polyfit(ys, v, 1)[0] * 10)
e_ys = [y for y in range(2000, 2026) if y in jja]
R["test_cmip6_vs_era5"] = {"model_jja_trend_C_per_decade_median": float(np.median(mt)), "model_range": [float(min(mt)), float(max(mt))],
                           "era5_jja_trend_C_per_decade": float(np.polyfit(e_ys, [jja[y] for y in e_ys], 1)[0] * 10),
                           "pass": bool(min(mt) <= np.polyfit(e_ys, [jja[y] for y in e_ys], 1)[0] * 10 <= max(mt))}

# ---------------------------------------------------------------- Sentinel-2 key glaciers
s2 = {}
for k, d in S2.items():
    rows = {int(y): v for y, v in d.items() if v.get("scene")}
    if len(rows) >= 4:
        ys = sorted(rows)
        s2[k] = {"years": rows, "trend_snow_frac_per_yr": trend(ys, [rows[y]["snow_frac"] for y in ys]),
                 "trend_snowline_m_per_yr": trend([y for y in ys if rows[y]["snowline_m"]], [rows[y]["snowline_m"] for y in ys if rows[y]["snowline_m"]]),
                 "lowest_snow_year": min(ys, key=lambda y: rows[y]["snow_frac"]), "highest_snowline_year": max((y for y in ys if rows[y]["snowline_m"]), key=lambda y: rows[y]["snowline_m"])}
R["s2_glaciers"] = s2

# ---------------------------------------------------------------- test: warm summers <-> bare glaciers (independent sensors)
yy = [y for y in range(2001, 2027) if y in jja and y in aug_gl]
r_, p_ = stats.pearsonr([jja[y] for y in yy], [aug_gl[y] for y in yy])
rs, ps = stats.spearmanr([jja[y] for y in yy], [aug_gl[y] for y in yy])
R["test_temp_vs_glacier_snow"] = {"pearson_r": r_, "p": p_, "spearman_r": rs, "spearman_p": ps, "n": len(yy),
                                   "note": "ERA5-Land JJA 2 m temperature vs MODIS August snow fraction on RGI 7.0 glacier area"}
# ---------------------------------------------------------------- test: does winter snowfall explain the 2025-26 storage low?
R["test_2025_26_attribution"] = {"winter_precip_2025_pct": (win_p[2025] / R["climate"]["winter_precip_clim_2001_2020"] - 1) * 100,
                                  "winter_precip_2026_pct": (win_p[2026] / R["climate"]["winter_precip_clim_2001_2020"] - 1) * 100,
                                  "jja_anom_2025": jja[2025] - R["climate"]["jja_t_clim_2001_2020"], "jja_anom_2026": jja[2026] - R["climate"]["jja_t_clim_2001_2020"],
                                  "spring_snow_2025_pct": R["snow"]["amj_2025_pct"], "spring_snow_2026_pct": R["snow"]["amj_2026_pct"]}
json.dump(R, open(os.path.join(D, "gb_results.json"), "w"), indent=1, default=float)
print("TEST temp vs glacier snow", R["test_temp_vs_glacier_snow"]); print("TEST 2025-26 attribution", R["test_2025_26_attribution"])
# ---------------------------------------------------------------- print summary
s = R["snow"]
print("SNOW water-year trend", {k: round(v, 4) if isinstance(v, float) else v for k, v in s["trend_water_year"].items()})
print("SNOW AMJ trend", {k: round(v, 4) if isinstance(v, float) else v for k, v in s["trend_amj"].items()}, "lowest", [(y, round(v, 3)) for y, v in s["amj_lowest3"]], "2025 %", round(s["amj_2025_pct"], 1), "2026 %", s["amj_2026_pct"] and round(s["amj_2026_pct"], 1))
print("SNOW JFM lowest", [(y, round(v, 3)) for y, v in s["jfm_lowest3"]], "2025 %", round(s["jfm_2025_pct"], 1), "2026 %", round(s["jfm_2026_pct"], 1))
print("SNOW Aug on glaciers trend", {k: round(v, 4) if isinstance(v, float) else v for k, v in s["trend_aug_glacier"].items()}, "lowest", [(y, round(v, 3)) for y, v in s["aug_on_glaciers_lowest3"]])
c = R["climate"]
print("JJA T trend C/decade", round(c["trend_jja_t"]["ols"] * 10, 3), "p", round(c["trend_jja_t"]["ols_p"], 4), "warmest", [(y, round(v, 2)) for y, v in c["warmest_jja"]])
print("WY precip trend mm/yr", round(c["trend_wy_precip"]["ols"], 2), "p", round(c["trend_wy_precip"]["ols_p"], 3), "driest winters", [(y, round(v)) for y, v in c["driest_winters"]], "clim", round(c["winter_precip_clim_2001_2020"]))
print("GLACIER acceleration", R["glaciers"]["acceleration_Gilgit-Baltistan"], R["glaciers"]["acceleration_GB excl. Siachen sector"])
print("TEST grace vs glaciers", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in R["test_grace_vs_glaciers"].items() if k != "note"})
print("CMIP6", json.dumps({s_: {p: {k: round(v, 2) for k, v in d.items()} for p, d in v.items()} for s_, v in proj.items()}))
print("TEST cmip6 vs era5", R["test_cmip6_vs_era5"])
for k, v in s2.items():
    print("S2", k, {y: (r["scene"], round(r["snow_frac"], 3), r["snowline_m"]) for y, r in v["years"].items()}, "trend", round(v["trend_snow_frac_per_yr"]["ols"], 4), round(v["trend_snow_frac_per_yr"]["mk_p"], 3))
