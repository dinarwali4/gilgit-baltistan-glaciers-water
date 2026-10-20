"""Per-glacier elevation change (Hugonnet et al. 2021) and RGI terminus/elevation range for the six key glaciers.
RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali.
Run after build_kml.py (which writes data/key_glaciers.json)."""
import os, json, certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
import ee
ee.Initialize(project=os.environ["EE_PROJECT"])  # your Earth Engine cloud project
D = os.path.join(os.path.dirname(__file__), "..", "data")
KG = json.load(open(os.path.join(D, "key_glaciers.json")))
RGI = ee.FeatureCollection("projects/sat-io/open-datasets/RGI/RGI_VECTOR_MERGED_V7").filter(ee.Filter.inList("rgi_id", [v["rgi_id"] for v in KG.values()]))
DH = ee.ImageCollection("projects/sat-io/open-datasets/GLOBAL-GLACIER-MASS-LOSS/elevation-change")
im = ee.Image.cat([DH.filter(ee.Filter.stringContains("system:index", p)).mosaic().rename(n)
                   for p, n in [("2000-01-01_2020-01-01", "d0019"), ("2000-01-01_2005-01-01", "d0004"), ("2015-01-01_2020-01-01", "d1519")]])
r = im.reduceRegions(RGI.select(["rgi_id", "zmin_m", "zmax_m", "termlat", "termlon"]), ee.Reducer.mean(), 100, tileScale=8).getInfo()["features"]
out = {f["properties"]["rgi_id"]: f["properties"] for f in r}
for k, v in KG.items():
    v.update({x: out[v["rgi_id"]].get(x) for x in ["d0019", "d0004", "d1519", "zmin_m", "zmax_m", "termlat", "termlon"]})
    print(k, round(v["d0004"], 3), round(v["d1519"], 3))
json.dump(KG, open(os.path.join(D, "key_glaciers.json"), "w"), indent=1)
