"""Gilgit-Baltistan glacier census (RGI 7.0) and 2000-2019 mass change (Hugonnet et al. 2021).

RegenX.eco Geospatial Computational Model - Gilgit-Baltistan Glaciers & Water Security.
Designed and prepared by Mr. Dinar Wali.

Sources
  RGI 7.0 (RGI2000-v7.0-G), GEE community copy projects/sat-io/open-datasets/RGI/RGI_VECTOR_MERGED_V7
    (validated: Shisper 14-08488 = 36.83 km2, src 1997-08-10, surge 3 - identical to the NSIDC 0770 download)
  Hugonnet et al. 2021, Nature 592:726 - glacier elevation change, 100 m, periods 2000-04 ... 2015-19
    projects/sat-io/open-datasets/GLOBAL-GLACIER-MASS-LOSS/elevation-change (+ -error)
Mass = dh/dt x area x 0.85 (ice/firn density 850 +/- 60 kg m-3, Huss 2013). 1 Gt = 1 km3 of water.
Glacier "in GB" = RGI centroid (cenlon, cenlat) inside the geoBoundaries ADM1 Gilgit-Baltistan polygon.
"""
import os, json
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
import ee
from shapely.geometry import shape, mapping, Point, box
from shapely.prepared import prep

ee.Initialize(project=os.environ["EE_PROJECT"])  # your Earth Engine cloud project
H = os.path.join(os.path.dirname(__file__), "..")
D = os.path.join(H, "data")
WS = os.path.join(H, "data", "boundaries")  # geoBoundaries gbOpen PAK ADM1/ADM2
RHO = 0.85

adm1 = json.load(open(os.path.join(WS, "pak_ADM1.geojson")))["features"]
adm2 = json.load(open(os.path.join(WS, "pak_ADM2.geojson")))["features"]
GB = shape([f for f in adm1 if f["properties"]["shapeName"] == "Gilgit-Baltistan"][0]["geometry"]).buffer(0)
pGB = prep(GB)
DIST = {f["properties"]["shapeName"]: shape(f["geometry"]).buffer(0) for f in adm2 if pGB.intersects(shape(f["geometry"]).representative_point())}
DIST = {k: v for k, v in DIST.items() if GB.contains(v.representative_point())}
print("GB districts:", sorted(DIST))
g = ee.Geometry(mapping(GB.simplify(0.005)))

RGI = ee.FeatureCollection("projects/sat-io/open-datasets/RGI/RGI_VECTOR_MERGED_V7").filterBounds(g)
props = ["rgi_id", "glac_name", "area_km2", "cenlat", "cenlon", "zmin_m", "zmax_m", "zmed_m", "surge_type", "src_date", "term_type", "termlat", "termlon", "slope_deg", "aspect_deg", "lmax_m"]
n = RGI.size().getInfo()
rows = []
lst = RGI.select(props).map(lambda f: f.setGeometry(None))
for off in range(0, n, 4000):
    rows += [f["properties"] for f in ee.FeatureCollection(lst.toList(4000, off)).getInfo()["features"]]
inGB = []
for r in rows:
    pt = Point(r["cenlon"], r["cenlat"])
    if pGB.contains(pt):
        r["district"] = next((k for k, v in DIST.items() if v.contains(pt)), "unassigned")
        inGB.append(r)
print(f"RGI7 touching GB {len(rows)}, centroid in GB {len(inGB)}")
ids_in = [r["rgi_id"] for r in inGB]
GL = RGI.filter(ee.Filter.inList("rgi_id", ids_in))

# ---------------------------------------------------------------- Hugonnet dh/dt by period
DH = ee.ImageCollection("projects/sat-io/open-datasets/GLOBAL-GLACIER-MASS-LOSS/elevation-change")
ER = ee.ImageCollection("projects/sat-io/open-datasets/GLOBAL-GLACIER-MASS-LOSS/elevation-change-error")
PERIODS = ["2000-01-01_2005-01-01", "2005-01-01_2010-01-01", "2010-01-01_2015-01-01", "2015-01-01_2020-01-01",
           "2000-01-01_2010-01-01", "2010-01-01_2020-01-01", "2000-01-01_2020-01-01"]
mask = ee.Image(0).byte().paint(GL, 1).selfMask()
regions = ee.FeatureCollection([ee.Feature(ee.Geometry(mapping(v.simplify(0.003))), {"district": k}) for k, v in DIST.items()]
                               + [ee.Feature(g, {"district": "Gilgit-Baltistan"}),
                                  ee.Feature(ee.Geometry(mapping(DIST["Ghanche"].intersection(box(76.85, 34.5, 78.5, 36.5)).simplify(0.003))), {"district": "Siachen sector"})])
# Siachen sector = Ghanche east of 76.85 E (Saltoro ridge): Siachen, Rimo, Bilafond, Gyong - administered by India.


out = {"n_glaciers": len(inGB), "area_km2": sum(r["area_km2"] for r in inGB), "periods": {}}
for p in PERIODS:
    dh = DH.filter(ee.Filter.stringContains("system:index", p)).mosaic().rename("dh")
    er = ER.filter(ee.Filter.stringContains("system:index", p)).mosaic().rename("er")
    pa = ee.Image.pixelArea()
    img = ee.Image.cat([dh.multiply(pa).rename("dhA"), er.multiply(pa).rename("erA"),
                        pa.updateMask(dh.mask()).rename("Avalid"), pa.rename("Aglac")]).updateMask(mask)
    st = img.reduceRegions(regions, ee.Reducer.sum(), scale=100, tileScale=8).getInfo()["features"]
    res = {}
    for f in st:
        q = f["properties"]
        if not q.get("Avalid"):
            continue
        dhm = q["dhA"] / q["Avalid"]
        A = q["Aglac"] / 1e6
        res[q["district"]] = {"dhdt_m_yr": dhm, "glacier_area_km2": A, "valid_frac": q["Avalid"] / q["Aglac"],
                              "mwe_yr": dhm * RHO}
        # Gt/yr = dh/dt (m) * area (km2) * 1e6 m2/km2 * 850 kg/m3 / 1e12 kg/Gt
        res[q["district"]]["gt_yr"] = dhm * A * 1e6 * 850 / 1e12
        res[q["district"]]["sums"] = {k: q[k] for k in ["dhA", "Avalid", "Aglac"]}
    a, b = res["Gilgit-Baltistan"]["sums"], res["Siachen sector"]["sums"]
    dA, vA, gA = a["dhA"] - b["dhA"], a["Avalid"] - b["Avalid"], a["Aglac"] - b["Aglac"]
    res["GB excl. Siachen sector"] = {"dhdt_m_yr": dA / vA, "mwe_yr": dA / vA * RHO, "glacier_area_km2": gA / 1e6,
                                      "valid_frac": vA / gA, "gt_yr": dA / vA * gA * 850 / 1e12}
    out["periods"][p] = res
    t = res["Gilgit-Baltistan"]
    x = res["GB excl. Siachen sector"]
    print(f"{p}: GB {t['mwe_yr']:+.3f} m w.e./yr {t['gt_yr']:+.3f} Gt/yr ({t['glacier_area_km2']:.0f} km2, valid {t['valid_frac']:.2f}) | excl. Siachen {x['mwe_yr']:+.3f} m w.e./yr {x['gt_yr']:+.3f} Gt/yr ({x['glacier_area_km2']:.0f} km2)")

# ---------------------------------------------------------------- per-glacier 2000-2019 for the large glaciers
big = sorted(inGB, key=lambda r: -r["area_km2"])[:40]
bigFC = RGI.filter(ee.Filter.inList("rgi_id", [r["rgi_id"] for r in big]))
dh20 = DH.filter(ee.Filter.stringContains("system:index", "2000-01-01_2020-01-01")).mosaic().rename("dh")
dh04 = DH.filter(ee.Filter.stringContains("system:index", "2000-01-01_2005-01-01")).mosaic().rename("dh0004")
dh19 = DH.filter(ee.Filter.stringContains("system:index", "2015-01-01_2020-01-01")).mosaic().rename("dh1519")
per = ee.Image.cat([dh20, dh04, dh19]).reduceRegions(bigFC.select(["rgi_id"]), ee.Reducer.mean(), scale=100, tileScale=8).getInfo()["features"]
pm = {f["properties"]["rgi_id"]: f["properties"] for f in per}
for r in big:
    q = pm.get(r["rgi_id"], {})
    r["dhdt_2000_2019"] = q.get("dh"); r["dhdt_2000_2004"] = q.get("dh0004"); r["dhdt_2015_2019"] = q.get("dh1519")
out["largest"] = big
json.dump(out, open(os.path.join(D, "glacier_mass_change.json"), "w"), indent=1)
json.dump(inGB, open(os.path.join(D, "rgi7_gb_attributes.json"), "w"))
print("largest:")
for r in big[:15]:
    print(f"  {r['glac_name'] or r['rgi_id']:28s} {r['area_km2']:7.1f} km2 {r['district']:10s} surge {r['surge_type']} dh/dt {r['dhdt_2000_2019']}")

