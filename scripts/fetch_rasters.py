"""Fetch map rasters for Gilgit-Baltistan figures from Earth Engine (PNG, georeferenced by bbox).

RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali.
  hillshade.png   Copernicus GLO-30 hillshade (grey)
  dhdt.png        Hugonnet et al. 2021 glacier elevation change 2000-2019, masked to RGI 7.0 GB glaciers, -2..+2 m/yr
  s2_<key>_<year>.png  Sentinel-2 L2A true colour on the scene used for that glacier-year (key glaciers)
"""
import os, json, urllib.request
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
import ee

ee.Initialize(project=os.environ["EE_PROJECT"])  # your Earth Engine cloud project
H = os.path.join(os.path.dirname(__file__), "..")
D = os.path.join(H, "data")
R = os.path.join(H, "data", "rasters")
os.makedirs(R, exist_ok=True)
BB = [72.4, 34.45, 77.85, 37.15]  # W S E N, Gilgit-Baltistan
ids = [r["rgi_id"] for r in json.load(open(os.path.join(D, "rgi7_gb_attributes.json")))]
GL = ee.FeatureCollection("projects/sat-io/open-datasets/RGI/RGI_VECTOR_MERGED_V7").filter(ee.Filter.inList("rgi_id", ids))
gmask = ee.Image(0).byte().paint(GL, 1)
region = ee.Geometry.Rectangle(BB, "EPSG:4326", False)


def save(img, name, dims=3000, region=region):
    url = img.getThumbURL({"region": region, "dimensions": dims, "format": "png", "crs": "EPSG:4326"})
    open(os.path.join(R, name), "wb").write(urllib.request.urlopen(url, timeout=600).read())
    print("saved", name)


if __name__ == "__main__":
    import sys
    what = sys.argv[1:] or ["hillshade", "dhdt", "s2"]
    dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic().setDefaultProjection("EPSG:4326", None, 30)
    if "hillshade" in what:
        hs = ee.Terrain.hillshade(dem.reduceResolution(ee.Reducer.mean(), True, 64).reproject("EPSG:4326", None, 150))
        save(hs.visualize(min=60, max=240, palette=["3a3f44", "f4f5f6"]), "hillshade.png")
    if "dhdt" in what:
        dh = ee.ImageCollection("projects/sat-io/open-datasets/GLOBAL-GLACIER-MASS-LOSS/elevation-change") \
            .filter(ee.Filter.stringContains("system:index", "2000-01-01_2020-01-01")).mosaic()
        vis = dh.updateMask(gmask).visualize(min=-2, max=2, palette=["7f2704", "c4501b", "f2a374", "ececec", "8fbfe0", "2f78b5", "0b3c6e"])
        save(vis, "dhdt.png")
    if "s2" in what:
        KG = json.load(open(os.path.join(D, "key_glaciers.json")))
        S2 = json.load(open(os.path.join(D, "s2_glacier_snow.json")))
        col = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        for k, g in KG.items():
            yrs = sorted(int(y) for y, v in S2.get(k, {}).items() if v.get("scene"))
            if not yrs:
                continue
            w, s, e, n = g["bounds"]; pad = 0.06
            reg = ee.Geometry.Rectangle([w - pad, s - pad, e + pad, n + pad], "EPSG:4326", False)
            for y in {yrs[0], yrs[-1]}:
                d = ee.Date(S2[k][str(y)]["scene"])
                im = col.filterBounds(reg).filterDate(d, d.advance(1, "day")).mosaic().select(["B4", "B3", "B2"])
                save(im.visualize(min=0, max=11000, gamma=1.6), f"s2_{k}_{y}.png", dims=2000, region=reg)
        json.dump({k: [g["bounds"][0] - .06, g["bounds"][1] - .06, g["bounds"][2] + .06, g["bounds"][3] + .06] for k, g in KG.items()},
                  open(os.path.join(R, "s2_bounds.json"), "w"))
