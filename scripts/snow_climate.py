"""Gilgit-Baltistan snow cover (MODIS) and observed climate (ERA5-Land), monthly 2001-2026.

RegenX.eco Geospatial Computational Model - Gilgit-Baltistan Glaciers & Water Security.
Designed and prepared by Mr. Dinar Wali.

MODIS/061/MOD10A1 (Terra, 500 m daily): snow = NDSI_Snow_Cover >= 40 on valid land pixels (0-100);
  monthly snow frequency per pixel = snow days / valid (cloud-free) days; reported as the area mean.
  Two masks: all of GB, and RGI 7.0 glacier area (late-summer snow on ice = snowline proxy).
ECMWF/ERA5_LAND/MONTHLY_AGGR: 2 m temperature (K -> C), total precipitation (m -> mm), GB area mean.
"""
import os, json, datetime as dt
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
import ee
from shapely.geometry import shape, mapping

ee.Initialize(project=os.environ["EE_PROJECT"])  # your Earth Engine cloud project
H = os.path.join(os.path.dirname(__file__), "..")
D = os.path.join(H, "data")
WS = os.path.join(H, "data", "boundaries")  # geoBoundaries gbOpen PAK ADM1/ADM2
GBs = shape([f for f in json.load(open(os.path.join(WS, "pak_ADM1.geojson")))["features"]
             if f["properties"]["shapeName"] == "Gilgit-Baltistan"][0]["geometry"]).buffer(0)
g = ee.Geometry(mapping(GBs.simplify(0.005)))
ids = [r["rgi_id"] for r in json.load(open(os.path.join(D, "rgi7_gb_attributes.json")))]
GL = ee.FeatureCollection("projects/sat-io/open-datasets/RGI/RGI_VECTOR_MERGED_V7").filter(ee.Filter.inList("rgi_id", ids))
gmask = ee.Image(0).byte().paint(GL, 1)

MOD = ee.ImageCollection("MODIS/061/MOD10A1").select("NDSI_Snow_Cover")


def snow_day(img):
    v = img.lte(100)
    s = img.gte(40).And(v)
    return ee.Image.cat([s.rename("s"), v.rename("v"), s.And(gmask).rename("sg"), v.And(gmask).rename("vg")]).toFloat() \
        .set("system:time_start", img.get("system:time_start"))


def month_stats(y, m):
    """Per-pixel snow frequency for the month (snow days / valid days), then GB- and glacier-area means."""
    a = ee.Date.fromYMD(y, m, 1); b = a.advance(1, "month")
    c = MOD.filterDate(a, b).map(snow_day)
    tot = c.select(["s", "v"]).sum()
    freq = tot.select("s").divide(tot.select("v")).rename("f").updateMask(tot.select("v").gt(0))
    r = ee.Image.cat([freq, freq.updateMask(gmask).rename("fg"), tot.select("v").gt(0).rename("cov")]).reduceRegion(
        ee.Reducer.mean(), g, 500, maxPixels=1e10, tileScale=4)
    return ee.Feature(None, {"y": y, "m": m, "snow_frac": r.get("f"), "glacier_snow_frac": r.get("fg"),
                             "n_days": c.size(), "observed_frac": r.get("cov")})


E5 = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")


def era_month(img):
    r = img.select(["temperature_2m", "total_precipitation_sum"]).reduceRegion(ee.Reducer.mean(), g, 11132, maxPixels=1e9)
    return ee.Feature(None, {"t": img.date().format("YYYY-MM"), "t2m_c": ee.Number(r.get("temperature_2m")).subtract(273.15),
                             "pr_mm": ee.Number(r.get("total_precipitation_sum")).multiply(1000)})


if __name__ == "__main__":
    OUT = os.path.join(D, "snow_climate.json")
    out = json.load(open(OUT)) if os.path.exists(OUT) else {"modis": [], "era5": []}
    done = {r["y"] for r in out["modis"]} - {dt.date.today().year}
    out["modis"] = [r for r in out["modis"] if r["y"] in done]
    today = dt.date.today()
    for y in range(2001, today.year + 1):
        if y in done:
            continue
        ms = [m for m in range(1, 13) if dt.date(y, m, 1) < dt.date(today.year, today.month, 1)]
        if y == 2001:
            pass
        rows = []
        for i in range(0, len(ms), 6):  # six months per request
            fc = ee.FeatureCollection([month_stats(y, m) for m in ms[i:i + 6]])
            got = None
            for attempt in range(8):
                try:
                    got = [f["properties"] for f in fc.getInfo()["features"]]; break
                except Exception as e:
                    print("retry", y, ms[i], str(e)[:80], flush=True); import time; time.sleep(20 * (attempt + 1))
            if got is None:
                raise SystemExit(f"modis {y}-{ms[i]} failed")
            rows += got
        out["modis"] += rows
        print("modis", y, [round(r["snow_frac"] or 0, 2) for r in rows], flush=True)
        json.dump(out, open(os.path.join(D, "snow_climate.json"), "w"))
    e = E5.filterDate("2000-01-01", str(today)).map(era_month)
    out["era5"] = [f["properties"] for f in e.getInfo()["features"]]
    print("era5", len(out["era5"]), out["era5"][-1])
    json.dump(out, open(os.path.join(D, "snow_climate.json"), "w"), indent=0)
