"""Gilgit-Baltistan total water storage from three GRACE/GRACE-FO solutions (CSR, GFZ, JPL).

RegenX.eco Geospatial Computational Model - Gilgit-Baltistan Glaciers & Water Security.
Designed and prepared by Mr. Dinar Wali.

Same method as the Pakistan assessment: area-weighted (cos lat x cell fraction inside GB) mean,
anomaly vs Jan 2004 - Dec 2009, deseasonalised with a 2004-2022 monthly climatology for annual means,
OLS + annual/semi-annual harmonics for trends. GB polygon: geoBoundaries ADM1.
Usage: grace_gb.py <gfz.nc> <csr.nc> <jpl_twsa.npz>
"""
import os, sys, json
import numpy as np, pandas as pd, xarray as xr
from shapely.geometry import shape, Point
from shapely.prepared import prep
from scipy import stats

H = os.path.join(os.path.dirname(__file__), "..")
D = os.path.join(H, "data")
WS = os.path.join(H, "data", "boundaries")  # geoBoundaries gbOpen PAK ADM1/ADM2
GB = shape([f for f in json.load(open(os.path.join(WS, "pak_ADM1.geojson")))["features"]
            if f["properties"]["shapeName"] == "Gilgit-Baltistan"][0]["geometry"]).buffer(0)
pg = prep(GB)
AREA = 69078.1  # km2, geodesic (Pakistan assessment)


def frac_grid(lat, lon, res, n=8):
    off = (np.arange(n) + .5) / n * res - res / 2
    F = np.zeros((len(lat), len(lon)))
    for i, la in enumerate(lat):
        if la < 34 or la > 38: continue
        for j, lo in enumerate(lon):
            if lo < 71.5 or lo > 78.5: continue
            F[i, j] = sum(pg.contains(Point(lo + a, la + b)) for a in off for b in off) / n / n
    return F * np.cos(np.radians(lat))[:, None]


def series(stack, w):
    m = ~np.isnan(stack)
    return np.nansum(np.where(m, stack, 0) * w, axis=(1, 2)) / np.sum(w * m, axis=(1, 2))


def dyear(ts):
    return np.array([t.year + (t.dayofyear - .5) / (366 if t.is_leap_year else 365) for t in ts])


def analyse(t, s, name):
    y = dyear(t)
    s = s - s[(y >= 2004) & (y < 2010)].mean()
    mon = np.array([d.month for d in t])
    base = (y >= 2004) & (y < 2023)
    clim = np.array([s[base & (mon == k)].mean() for k in range(1, 13)])
    ds = s - clim[mon - 1]
    yrs = np.floor(y).astype(int)
    ann = {int(k): float(ds[yrs == k].mean()) for k in np.unique(yrs) if (yrs == k).sum() >= 6}

    def trend(lo, hi):
        sel = (y >= lo) & (y < hi)
        X = np.column_stack([np.ones(sel.sum()), y[sel] - 2014, np.sin(2 * np.pi * y[sel]), np.cos(2 * np.pi * y[sel]),
                             np.sin(4 * np.pi * y[sel]), np.cos(4 * np.pi * y[sel])])
        b, *_ = np.linalg.lstsq(X, s[sel], rcond=None)
        a = {k: v for k, v in ann.items() if lo <= k < hi}
        p = stats.kendalltau(list(a), list(a.values()))[1] if len(a) > 3 else None
        return {"cm_yr": float(b[1]), "mk_p": p, "km3_yr": float(b[1]) * 1e-5 * AREA}
    return {"name": name, "first": str(t[0].date()), "last": str(t[-1].date()), "n": int(len(t)),
            "trend_all": trend(2002, 2027), "trend_grace": trend(2002, 2017.5), "trend_fo": trend(2018.4, 2027),
            "annual": ann, "monthly": [[str(a.date()), float(b), float(c)] for a, b, c in zip(t, s, ds)],
            "mom_abs_change_median_cm": float(np.median(np.abs(np.diff(ds))))}


if __name__ == "__main__":
    out = {}
    c = xr.open_dataset(sys.argv[2])  # UT-CSR RL06.3 mascons (all corrections)
    sub = c.lwe_thickness.sel(lat=slice(34, 38), lon=slice(71.5, 78.5))
    t = pd.to_datetime("2002-01-01") + pd.to_timedelta(c.time.values.astype(float), unit="D")
    out["CSR"] = analyse(t, series(sub.values, frac_grid(sub.lat.values, sub.lon.values, .25)), "UT-CSR RL06.3 mascons")
    gz = xr.open_dataset(sys.argv[1], decode_times=False)
    gs = gz.sel(lat=slice(38, 34), lon=slice(71.5, 78.5))
    tg = pd.to_datetime("2002-04-18") + pd.to_timedelta(gz.time.values.astype(float), unit="D")
    wg = frac_grid(gs.lat.values, gs.lon.values, 1.0)
    out["GFZ"] = analyse(tg, series(gs.tws.values, wg), "GFZ GravIS RL06 v0006")
    out["GFZ_minus_leakage"] = analyse(tg, series(gs.tws.values - gs.leakage.values, wg), "GFZ GravIS minus its leakage field")
    j = np.load(sys.argv[3])  # JPL CRI mascons on the 0.25 deg grid (Pakistan assessment fetch_ee.py)
    tj = pd.to_datetime(j["t"]); lat, lon = j["lat"], j["lon"]
    out["JPL"] = analyse(tj, series(j["twsa"], frac_grid(lat, lon, .25)), "NASA-JPL RL06.3 CRI mascons (to Sep 2024)")
    # agreement on common years
    for k in ["GFZ", "JPL", "GFZ_minus_leakage"]:
        a, b = out["CSR"]["annual"], out[k]["annual"]
        yrs = sorted(set(a) & set(b))
        out[k]["r_vs_csr_annual"] = float(np.corrcoef([a[y] for y in yrs], [b[y] for y in yrs])[0, 1])
    json.dump(out, open(os.path.join(D, "grace_gb.json"), "w"), indent=0)
    for k, v in out.items():
        a = v["annual"]
        print(f"{k:18s} {v['first']}..{v['last']}  all {v['trend_all']['cm_yr']:+.2f}  GRACE {v['trend_grace']['cm_yr']:+.2f}  FO {v['trend_fo']['cm_yr']:+.2f} (p {v['trend_fo']['mk_p']})  "
              f"r {v.get('r_vs_csr_annual', 1):.2f}  2023 {a.get(2023, float('nan')):+.1f} 2024 {a.get(2024, float('nan')):+.1f} 2025 {a.get(2025, float('nan')):+.1f} 2026 {a.get(2026, float('nan')):+.1f}  |dm| {v['mom_abs_change_median_cm']:.1f}")
