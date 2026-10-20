"""Drive Google Earth Pro through state.kml, wait for imagery to settle, capture the window, read the imagery date.

RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali.
Each frame carries the glacier's RGI 7.0 outline (historical snapshot) rendered by Earth itself.
Usage: shoot.py [glacier ...]   (default: all key glaciers)
"""
import os, sys, json, time, subprocess
import numpy as np
from PIL import Image
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "data")
T = os.environ.get("EARTH_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))  # winid, mouse, ocr helpers
KG = json.load(open(os.path.join(D, "key_glaciers.json")))
F = {f["properties"]["rgi_id"]: f for f in json.load(open(os.path.join(D, "rgi7_gb_outlines_30m.geojson")))["features"]}
ATTR = {r["rgi_id"]: r for r in json.load(open(os.path.join(D, "rgi7_gb_attributes.json")))}
DATES = ["2026-10-20", "2016-12-31", "2010-12-31"]  # pre-2010 is Landsat-only over GB


def win():
    for attempt in range(10):
        if attempt:  # only pull Earth forward when its window is not on the current screen
            subprocess.run(["osascript", "-e", 'tell application "Google Earth Pro" to activate'], capture_output=True)
            time.sleep(3)
        for line in subprocess.run([T + "/winid"], capture_output=True, text=True).stdout.splitlines():
            p = line.split()
            if int(float(p[3])) > 800:
                return p[0], float(p[1]), float(p[2]), float(p[3]), float(p[4])
    raise SystemExit("no Earth window")


def outline_kml(rgi_id, name):
    g = shape(F[rgi_id]["geometry"])
    polys = [q for q in getattr(g, "geoms", [g]) if q.geom_type == "Polygon"]
    rings = "".join(f"<Polygon><tessellate>1</tessellate><outerBoundaryIs><LinearRing><coordinates>{' '.join(f'{x:.5f},{y:.5f},0' for x, y in p.exterior.coords)}</coordinates></LinearRing></outerBoundaryIs></Polygon>" for p in polys)
    return (f'<Style id="o"><LineStyle><color>ff00ffff</color><width>3</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>'
            f'<Placemark><styleUrl>#o</styleUrl><MultiGeometry>{rings}</MultiGeometry></Placemark>')


def write_state(lat, lon, rng, when, extra):
    ts = f"<gx:TimeStamp><when>{when}</when></gx:TimeStamp>" if when else ""
    open(os.path.join(HERE, "state.kml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">'
        f'<Document><name>v {lat:.5f} {lon:.5f} {rng:.0f} {when}</name><LookAt>{ts}<longitude>{lon}</longitude><latitude>{lat}</latitude>'
        f'<altitude>0</altitude><heading>0</heading><tilt>0</tilt><range>{rng}</range><altitudeMode>relativeToGround</altitudeMode></LookAt>{extra}</Document></kml>')


def grab(p, wid):
    for _ in range(20):
        if os.path.exists(p): os.remove(p)
        subprocess.run(["screencapture", "-x", "-o", "-l", wid, p], capture_output=True)
        if os.path.exists(p) and os.path.getsize(p) > 0: return
        time.sleep(4)
    raise SystemExit("capture failed")


def small(p):
    return np.asarray(Image.open(p).convert("L").resize((294, 168)), dtype=float)


def ocr(p, box):
    tmp = os.path.join(HERE, "raw", "_ocr.png")
    im = Image.open(p).crop(box); im.resize((im.width * 2, im.height * 2)).save(tmp)
    return " ".join(l.split("\t", 1)[-1] for l in subprocess.run([T + "/ocr", tmp], capture_output=True, text=True).stdout.splitlines())


def shoot(lat, lon, rng, when, out, extra, maxwait=95):
    wid, wx, wy, ww, wh = win()
    write_state(lat, lon, rng, when, extra)
    tmp = os.path.join(HERE, "raw", "_ge.png")
    t0 = time.time(); prev = None; stable = 0; time.sleep(14)
    while time.time() - t0 < maxwait:
        wid = win()[0]; grab(tmp, wid); cur = small(tmp)
        if prev is not None:
            stable = stable + 1 if np.abs(cur - prev).mean() < 1.0 else 0
            if stable >= 2: break
        prev = cur; time.sleep(5)
    subprocess.run([T + "/mouse", str(wx + ww / 2), str(wy + wh / 2 + 20)]); time.sleep(2.5)
    grab(tmp, wid)
    W, Hh = Image.open(tmp).size
    meta = {"when": when, "lat": lat, "lon": lon, "range": rng, "settled": stable >= 2, "secs": round(time.time() - t0),
            "status": ocr(tmp, (int(W * .38), Hh - 46, W, Hh)), "slider": ocr(tmp, (0, 110, int(W * .25), 240)),
            "credit": ocr(tmp, (int(W * .3), int(Hh * .86), int(W * .75), int(Hh * .93)))}
    os.replace(tmp, out)
    return meta


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "raw"), exist_ok=True)
    keys = sys.argv[1:] or list(KG)
    log = open(os.path.join(HERE, "shots.jsonl"), "a")
    for k in keys:
        g = KG[k]; a = ATTR[g["rgi_id"]]
        extra = outline_kml(g["rgi_id"], g["name"])
        w, s, e, n = g["bounds"]
        ext_m = max((e - w) * 111320 * np.cos(np.radians((s + n) / 2)), (n - s) * 110540)
        jobs = [("overview", (s + n) / 2, (w + e) / 2, ext_m * 0.95, "2026-10-20")]
        jobs += [("tongue", a["termlat"], a["termlon"], 9000, d) for d in DATES]
        for kind, la, lo, rng, d in jobs:
            out = os.path.join(HERE, "raw", f"{k}_{kind}_{d}.png")
            m = shoot(la, lo, rng, d, out, extra)
            m.update({"glacier": k, "kind": kind, "file": os.path.basename(out)})
            print(json.dumps(m), flush=True); log.write(json.dumps(m) + "\n"); log.flush()
