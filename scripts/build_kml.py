"""Gilgit-Baltistan glacier KMZ for Google Earth Pro + camera control files.

RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali.
Outlines: RGI 7.0 (RGI2000-v7.0-G), simplified to 30 m; dh/dt: Hugonnet et al. 2021 (2000-2019).
"""
import os, json, zipfile
from xml.sax.saxutils import escape
from shapely.geometry import shape

H = os.path.join(os.path.dirname(__file__), "..")
D = os.path.join(H, "data")
K = os.path.join(H, "kml")
WS = os.path.join(H, "data", "boundaries")  # geoBoundaries gbOpen PAK ADM1/ADM2
CREDIT = "RegenX.eco Geospatial Computational Model · Designed and prepared by Mr. Dinar Wali"
F = json.load(open(os.path.join(D, "rgi7_gb_outlines_30m.geojson")))["features"]
MC = json.load(open(os.path.join(D, "glacier_mass_change.json")))
big = {r["rgi_id"]: r for r in MC["largest"]}

KEY = {  # imagery targets: RGI 7.0 glac_name
    "baltoro": "Baltoro Glacier", "biafo": "Biafo Glacier", "hispar": "Hispar Glacier",
    "batura": "Batura Glacier", "passu": "Pasu Glacier", "shisper": None,
}
SHISPER = "RGI2000-v7.0-G-14-08488"


def ring(coords):
    return " ".join(f"{x:.5f},{y:.5f},0" for x, y in coords)


def poly_kml(geom):
    out = []
    for p in [q for q in getattr(geom, "geoms", [geom]) if q.geom_type == "Polygon"]:
        inner = "".join(f"<innerBoundaryIs><LinearRing><coordinates>{ring(i.coords)}</coordinates></LinearRing></innerBoundaryIs>" for i in p.interiors)
        out.append(f"<Polygon><tessellate>1</tessellate><outerBoundaryIs><LinearRing><coordinates>{ring(p.exterior.coords)}</coordinates></LinearRing></outerBoundaryIs>{inner}</Polygon>")
    return "<MultiGeometry>" + "".join(out) + "</MultiGeometry>"


def key_glaciers():
    out = {}
    for k, nm in KEY.items():
        f = next(f for f in F if (f["properties"]["rgi_id"] == SHISPER if nm is None else f["properties"]["glac_name"] == nm))
        g = shape(f["geometry"])
        out[k] = {"rgi_id": f["properties"]["rgi_id"], "name": nm or "Shisper Glacier", "area_km2": f["properties"]["area_km2"],
                  "src_date": f["properties"]["src_date"][:10], "bounds": g.bounds, "centroid": [g.centroid.y, g.centroid.x]}
    return out


if __name__ == "__main__":
    os.makedirs(K, exist_ok=True)
    gb = [f for f in json.load(open(os.path.join(WS, "pak_ADM1.geojson")))["features"] if f["properties"]["shapeName"] == "Gilgit-Baltistan"][0]
    gbg = shape(gb["geometry"])
    pm = []
    for f in F:
        p = f["properties"]
        st = "#sia" if p["siachen_sector"] else ("#big" if p["area_km2"] >= 10 else "#gl")
        nm = p["glac_name"] or p["rgi_id"]
        b = big.get(p["rgi_id"])
        dh = f"<br/>Elevation change 2000–2019: {b['dhdt_2000_2019']:+.2f} m/yr (Hugonnet et al. 2021)" if b and b.get("dhdt_2000_2019") is not None else ""
        desc = (f"{escape(nm)}<br/>{p['area_km2']:.2f} km² · district {p['district']} · outline date {p['src_date'][:10]} · surge type {p['surge_type']}{dh}"
                + ("<br/>Siachen sector: administered by India; included in the geoBoundaries GB polygon." if p["siachen_sector"] else "")
                + f"<br/>Outline: RGI 7.0. {escape(CREDIT)}")
        pm.append(f"<Placemark><name>{escape(nm) if p['area_km2'] >= 25 else ''}</name><description><![CDATA[{desc}]]></description><styleUrl>{st}</styleUrl>{poly_kml(shape(f['geometry']))}</Placemark>")
    labels = []
    for r in sorted(MC["largest"], key=lambda r: -r["area_km2"])[:30]:
        nm = (r["glac_name"] or "").replace("IN5Q151B0013 ", "").replace("IN5Q153E0011 ", "") or r["rgi_id"][-8:]
        labels.append(f"<Placemark><name>{escape(nm)}</name><styleUrl>#lab</styleUrl><Point><coordinates>{r['cenlon']:.5f},{r['cenlat']:.5f},0</coordinates></Point></Placemark>")
    bnd = "".join(f"<Placemark><name>Gilgit-Baltistan (geoBoundaries ADM1)</name><styleUrl>#bnd</styleUrl><LineString><tessellate>1</tessellate><coordinates>{ring(p.exterior.coords)}</coordinates></LineString></Placemark>"
                  for p in getattr(gbg, "geoms", [gbg]))
    doc = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"><Document>
<name>Gilgit-Baltistan Glaciers — RegenX.eco</name><open>1</open>
<description><![CDATA[{len(F):,} glaciers with centroid in Gilgit-Baltistan, RGI 7.0 outlines (source dates 1990s–2000s; historical snapshot, not current ice). {escape(CREDIT)}]]></description>
<Style id="gl"><LineStyle><color>ffffd34a</color><width>1.2</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>
<Style id="big"><LineStyle><color>ff00ffff</color><width>2.2</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="sia"><LineStyle><color>ffb0b0b0</color><width>1.2</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>
<Style id="bnd"><LineStyle><color>ff4ad3ff</color><width>3</width></LineStyle></Style>
<Style id="lab"><IconStyle><scale>0</scale></IconStyle><LabelStyle><color>ffffffff</color><scale>1.0</scale></LabelStyle></Style>
<Folder><name>Gilgit-Baltistan boundary</name>{bnd}</Folder>
<Folder><name>Glacier names (30 largest)</name>{''.join(labels)}</Folder>
<Folder><name>Glacier outlines (RGI 7.0)</name>{''.join(pm)}</Folder>
</Document></kml>"""
    with zipfile.ZipFile(os.path.join(K, "GB_Glaciers_RGI7_RegenX.kmz"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("doc.kml", doc)
    kg = key_glaciers()
    kgx = json.load(open(os.path.join(D, "key_glaciers.json"))) if os.path.exists(os.path.join(D, "key_glaciers.json")) else {}
    s2r = json.load(open(os.path.join(D, "gb_results.json"))).get("s2_glaciers", {}) if os.path.exists(os.path.join(D, "gb_results.json")) else {}
    kp_ = []
    for k, v in kgx.items():
        if "termlat" not in v: continue
        ys = s2r.get(k, {}).get("years", {})
        sn = ""
        if ys:
            y0, y1 = min(ys, key=int), max(ys, key=int)
            sn = f"<br/>Sentinel-2 end-of-summer snow: {ys[y0]['snow_frac']*100:.0f} % ({y0}) to {ys[y1]['snow_frac']*100:.0f} % ({y1}); lowest {s2r[k]['lowest_snow_year']}"
        desc = (f"<b>{escape(v['name'])}</b><br/>{v['area_km2']:.1f} km², {v['zmin_m']:,.0f}–{v['zmax_m']:,.0f} m · RGI outline {v['src_date']}"
                f"<br/>Surface change {v['d0004']:+.2f} m/yr (2000–04) to {v['d1519']:+.2f} m/yr (2015–19), Hugonnet et al. 2021{sn}<br/>{escape(CREDIT)}")
        kp_.append(f"<Placemark><name>{escape(v['name'])} (tongue)</name><description><![CDATA[{desc}]]></description>"
                   f"<LookAt><longitude>{v['termlon']:.5f}</longitude><latitude>{v['termlat']:.5f}</latitude><altitude>0</altitude><heading>0</heading><tilt>0</tilt><range>9000</range></LookAt>"
                   f"<Point><coordinates>{v['termlon']:.5f},{v['termlat']:.5f},0</coordinates></Point></Placemark>")
    if kp_:
        doc = doc.replace("<Folder><name>Glacier names (30 largest)</name>", "<Folder><name>Key glaciers (click to fly to the tongue)</name>" + "".join(kp_) + "</Folder><Folder><name>Glacier names (30 largest)</name>")
        with zipfile.ZipFile(os.path.join(K, "GB_Glaciers_RGI7_RegenX.kmz"), "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("doc.kml", doc)
    prev = json.load(open(os.path.join(D, "key_glaciers.json"))) if os.path.exists(os.path.join(D, "key_glaciers.json")) else {}
    for k_ in kg:  # keep fields added by key_glacier_rates.py
        kg[k_] = {**prev.get(k_, {}), **kg[k_]}
    json.dump(kg, open(os.path.join(D, "key_glaciers.json"), "w"), indent=1)
    # outline-only KML for the key glaciers (bright, for the imagery captures)
    sel = {v["rgi_id"] for v in kg.values()}
    kp = "".join(f"<Placemark><styleUrl>#k</styleUrl>{poly_kml(shape(f['geometry']))}</Placemark>" for f in F if f["properties"]["rgi_id"] in sel)
    open(os.path.join(K, "key_outlines.kml"), "w").write(f"""<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Key glacier outlines</name>
<Style id="k"><LineStyle><color>ff00ffff</color><width>3</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>{kp}</Document></kml>""")
    print("kmz", os.path.getsize(os.path.join(K, "GB_Glaciers_RGI7_RegenX.kmz")) // 1024, "KB;", json.dumps({k: (v["name"], round(v["area_km2"], 1), v["src_date"]) for k, v in kg.items()}))
