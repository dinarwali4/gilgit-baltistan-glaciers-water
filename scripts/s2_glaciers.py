"""End-of-ablation snow cover and snow-line altitude on six key GB glaciers, Sentinel-2 L2A, 2017-2026.

RegenX.eco Geospatial Computational Model - Gilgit-Baltistan Glaciers & Water Security.
Designed and prepared by Mr. Dinar Wali.

Same logic as the GLOF project's glacier_melt_snowline.py, with its two known defects removed:
  * COPERNICUS/S2_SR_HARMONIZED (processing-baseline offset already harmonised - no post-2022 bias)
  * all tiles of one acquisition date are mosaicked before scoring (no single-tile strip)
NDSI = (B3 - B11)/(B3 + B11); snow = NDSI >= 0.40 on clear pixels (SCL not 0,1,3,8,9,10).
Scene choice per year: in-outline coverage >= 0.90 and in-outline cloud <= 10 %, closest to 1 Sep
(window 1 Aug - 30 Sep). Snow line = lowest 100 m band (Copernicus GLO-30) that is >= 50 % snow.
"""
import os, json, time, datetime as dt
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
import ee

ee.Initialize(project=os.environ["EE_PROJECT"])  # your Earth Engine cloud project
H = os.path.join(os.path.dirname(__file__), "..")
D = os.path.join(H, "data")
KG = json.load(open(os.path.join(D, "key_glaciers.json")))
RGI = ee.FeatureCollection("projects/sat-io/open-datasets/RGI/RGI_VECTOR_MERGED_V7")
S2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
DEM = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic()
OUT = os.path.join(D, "s2_glacier_snow.json")


def day_mosaic(geom, date):
    d = ee.Date(date)
    return S2.filterBounds(geom).filterDate(d, d.advance(1, "day")).mosaic()


def score(geom, date):
    im = day_mosaic(geom, date)
    scl = im.select("SCL")
    valid = scl.gt(1)
    cloud = scl.eq(3).Or(scl.eq(8)).Or(scl.eq(9)).Or(scl.eq(10))
    r = ee.Image.cat([valid.unmask(0).rename("v"), cloud.And(valid).unmask(0).rename("c")]).reduceRegion(
        ee.Reducer.mean(), geom, 60, maxPixels=1e9, tileScale=4)
    return ee.Feature(None, {"date": date, "cov": r.get("v"), "cloud_of_area": r.get("c")})


def snow_stats(geom, date):
    im = day_mosaic(geom, date)
    scl = im.select("SCL")
    clear = scl.gt(1).And(scl.neq(3)).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10))
    ndsi = im.normalizedDifference(["B3", "B11"])
    snow = ndsi.gte(0.40).updateMask(clear).rename("snow")
    band = DEM.divide(100).floor().int().rename("band")
    r = ee.Image.cat([snow, band]).reduceRegion(ee.Reducer.mean().group(1, "band"), geom, 60, maxPixels=1e9, tileScale=4)
    tot = snow.reduceRegion(ee.Reducer.mean(), geom, 60, maxPixels=1e9, tileScale=4)
    clr = clear.unmask(0).reduceRegion(ee.Reducer.mean(), geom, 60, maxPixels=1e9, tileScale=4)
    return ee.Dictionary({"snow_frac": tot.get("snow"), "clear_frac": clr.get("SCL"), "groups": r.get("groups")})


if __name__ == "__main__":
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for k, g in KG.items():
        geom = RGI.filter(ee.Filter.eq("rgi_id", g["rgi_id"])).first().geometry()
        res.setdefault(k, {})
        for y in range(2017, 2027):
            if str(y) in res[k]:
                continue
            col = S2.filterBounds(geom).filterDate(f"{y}-08-01", f"{y}-10-01")
            dates = sorted(set(col.aggregate_array("system:time_start").map(lambda t: ee.Date(t).format("YYYY-MM-dd")).getInfo()))
            sc = []
            for i in range(0, len(dates), 8):
                for attempt in range(6):
                    try:
                        sc += [f["properties"] for f in ee.FeatureCollection([score(geom, d) for d in dates[i:i + 8]]).getInfo()["features"]]; break
                    except Exception as e:
                        print("retry", k, y, str(e)[:80], flush=True); time.sleep(15 * (attempt + 1))
            ok = [s for s in sc if (s["cov"] or 0) >= 0.90 and s["cloud_of_area"] is not None and s["cloud_of_area"] / max(s["cov"], 1e-6) <= 0.10]
            if not ok:
                res[k][str(y)] = {"scene": None, "candidates": len(sc)}
                print(k, y, "no qualifying scene of", len(sc), flush=True); continue
            target = dt.date(y, 9, 1)
            best = min(ok, key=lambda s: (abs((dt.date.fromisoformat(s["date"]) - target).days), s["cloud_of_area"]))
            st = snow_stats(geom, best["date"]).getInfo()
            groups = sorted(st["groups"], key=lambda q: q["band"])
            sl = next((q["band"] * 100 for q in groups if q.get("mean") is not None and q["mean"] >= 0.5), None)
            res[k][str(y)] = {"scene": best["date"], "days_from_sep1": (dt.date.fromisoformat(best["date"]) - target).days,
                              "coverage": best["cov"], "cloud_in_outline": best["cloud_of_area"] / best["cov"],
                              "snow_frac": st["snow_frac"], "clear_frac": st["clear_frac"], "snowline_m": sl, "candidates": len(sc)}
            print(k, y, json.dumps(res[k][str(y)]), flush=True)
            json.dump(res, open(OUT, "w"), indent=1)
