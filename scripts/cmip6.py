"""Gilgit-Baltistan climate projections from NASA NEX-GDDP-CMIP6 (0.25 deg, bias-corrected, daily).

RegenX.eco Geospatial Computational Model - Gilgit-Baltistan Glaciers & Water Security.
Designed and prepared by Mr. Dinar Wali.

Per model x scenario x year: GB-mean summer (JJA) tas (C) and annual precipitation (mm).
Changes are computed per model against that model's own 1995-2014 historical mean, then summarised
across models (median, min, max) - the standard way to avoid carrying model bias into the change.
"""
import os, sys, json, time
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
g = ee.Geometry(mapping(GBs.simplify(0.01)))
MODELS = ["ACCESS-CM2", "CanESM5", "CNRM-ESM2-1", "EC-Earth3", "GFDL-ESM4", "INM-CM5-0", "IPSL-CM6A-LR",
          "MIROC6", "MPI-ESM1-2-HR", "MRI-ESM2-0", "NorESM2-MM", "UKESM1-0-LL"]
C = ee.ImageCollection("NASA/GDDP-CMIP6")
OUT = os.path.join(D, "cmip6_gb.json")


def series(model, scen, y0, y1):
    c = C.filter(ee.Filter.eq("model", model)).filter(ee.Filter.eq("scenario", scen))

    def yr(y):
        y = ee.Number(y)
        a = ee.Date.fromYMD(y, 1, 1)
        jja = c.filterDate(ee.Date.fromYMD(y, 6, 1), ee.Date.fromYMD(y, 9, 1)).select("tas").mean().subtract(273.15)
        pr = c.filterDate(a, a.advance(1, "year")).select("pr").mean().multiply(86400 * 365.25)
        r = ee.Image.cat([jja.rename("t"), pr.rename("p")]).reduceRegion(ee.Reducer.mean(), g, 27830, maxPixels=1e9)
        return ee.List([y, r.get("t"), r.get("p")])
    return ee.List.sequence(y0, y1).map(yr).getInfo()


if __name__ == "__main__":
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for m in MODELS:
        for scen, y0, y1 in [("historical", 1985, 2014), ("ssp245", 2015, 2100), ("ssp585", 2015, 2100)]:
            k = f"{m}|{scen}"
            if k in res:
                continue
            for attempt in range(4):
                try:
                    res[k] = series(m, scen, y0, y1); break
                except Exception as e:
                    print("retry", k, str(e)[:120], flush=True); time.sleep(20)
            print(k, "done", res.get(k, [[None]])[-1], flush=True)
            json.dump(res, open(OUT, "w"))
