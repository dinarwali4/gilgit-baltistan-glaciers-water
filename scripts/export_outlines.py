"""Export simplified (30 m) RGI 7.0 outlines of Gilgit-Baltistan glaciers for KML and maps.
RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali."""
import os, json
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
import ee
ee.Initialize(project=os.environ["EE_PROJECT"])  # your Earth Engine cloud project
H = os.path.join(os.path.dirname(__file__), "..")
D = os.path.join(H, "data")
inGB = json.load(open(os.path.join(D, "rgi7_gb_attributes.json")))
ids_in = [r["rgi_id"] for r in inGB]
GL = ee.FeatureCollection("projects/sat-io/open-datasets/RGI/RGI_VECTOR_MERGED_V7").filter(ee.Filter.inList("rgi_id", ids_in))
# ---------------------------------------------------------------- outlines for KML / maps (simplified 30 m)
feats = []
GLs = GL.map(lambda f: ee.Feature(f.geometry().simplify(30), f.toDictionary(["rgi_id", "glac_name", "area_km2", "surge_type", "src_date", "zmed_m"])))
for off in range(0, len(ids_in), 800):
    feats += ee.FeatureCollection(GLs.toList(800, off)).getInfo()["features"]
dist_of = {r["rgi_id"]: r["district"] for r in inGB}
lon_of = {r["rgi_id"]: r["cenlon"] for r in inGB}
for f in feats:
    f["properties"]["district"] = dist_of.get(f["properties"]["rgi_id"])
    f["properties"]["siachen_sector"] = f["properties"]["district"] == "Ghanche" and lon_of[f["properties"]["rgi_id"]] >= 76.85
json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(D, "rgi7_gb_outlines_30m.geojson"), "w"))
print("outlines", len(feats))
