"""Annotate Google Earth Pro captures of six key Gilgit-Baltistan glaciers.

RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali.
Design rule (from earlier GB work): no computed arrows or positions are drawn on the imagery.
Every geographic mark (the yellow RGI 7.0 outline) was rendered by Google Earth itself from KML;
this script only crops window chrome and adds a header, a fact panel, a legend and credits.
Imagery dates are read from Earth's own status bar (OCR) at the frame centre.
"""
import os, re, json
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "annotated")
os.makedirs(OUT, exist_ok=True)
KG = json.load(open(os.path.join(D, "key_glaciers.json")))
R = json.load(open(os.path.join(D, "gb_results.json")))
SHOTS = [json.loads(l) for l in open(os.path.join(HERE, "shots.jsonl"))]
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
INK, MUTED, BRAND, YEL = (31, 35, 40), (91, 99, 110), (74, 117, 38), (255, 225, 77)
CREDIT = "RegenX.eco Geospatial Computational Model  ·  Designed and prepared by Mr. Dinar Wali"


def f(sz, bold=False):
    return ImageFont.truetype(FONT, sz, index=1 if bold else 0)


def imagery_date(status):
    """OCR reads '/' as '1' (or l, |, j): enumerate every m/d/yyyy split of the digit run and keep the first valid one."""
    m = re.search(r"Date[^0-9]*([0-9/1lI|j]{6,12})", status)
    if not m:
        return None
    t = re.sub(r"[lI|j]", "1", m.group(1))
    for mlen in (2, 1):  # two-digit month first: matches every on-screen date checked by eye
        for dlen in (1, 2):
            i = mlen
            if t[i:i + 1] not in ("/", "1"): continue
            dd = t[i + 1:i + 1 + dlen]; j = i + 1 + dlen
            if t[j:j + 1] not in ("/", "1"): continue
            yy = t[j + 1:j + 5]
            try:
                mo, d, y = int(t[:mlen]), int(dd), int(yy)
            except ValueError:
                continue
            if 1 <= mo <= 12 and 1 <= d <= 31 and 1984 <= y <= 2026 and len(yy) == 4:
                return f"{y}-{mo:02d}-{d:02d}"
    return None


T = os.environ.get("EARTH_TOOLS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))  # winid, mouse, ocr helpers
OVR_P = os.path.join(HERE, "date_overrides.json")
OVR = json.load(open(OVR_P)) if os.path.exists(OVR_P) else {}


def shot_date(s):
    """Status-bar date: manual reading (checked by eye) > OCR of the tight status crop > OCR stored at capture time."""
    if s["file"] in OVR:
        return OVR[s["file"]]
    import subprocess
    p = os.path.join(HERE, "raw", s["file"])
    im = Image.open(p); W, H = im.size
    tmp = os.path.join(HERE, "raw", "_date.png")
    im.crop((int(W * .52), H - 46, int(W * .72), H)).resize((int(W * .2 * 3), 46 * 3)).save(tmp)
    txt = " ".join(l.split("\t", 1)[-1] for l in subprocess.run([T + "/ocr", tmp], capture_output=True, text=True).stdout.splitlines())
    return imagery_date(txt) or imagery_date(s["status"])


def provider(credit):
    c = credit.lower()
    out = [n for k, n in [("airbus", "Airbus"), ("maxar", "Maxar Technologies"), ("cnes", "CNES"), ("landsat", "Landsat / Copernicus")] if k in c]
    return " / ".join(out) or "see attribution on image"


def frame(png):
    im = Image.open(png).convert("RGB")
    W, H = im.size
    return im.crop((0, 250, W, H - 46))  # drop title bar, toolbar, history slider row and status bar


def compose(panels, title, sub, facts, out):
    pw = 2940 if len(panels) == 1 else 1470
    ims = [p.resize((pw, int(p.height * pw / p.width))) for p, _ in panels]
    ph = ims[0].height
    W = pw * len(panels) + 12 * (len(panels) - 1)
    head, foot = 190, 150
    canvas = Image.new("RGB", (W, head + ph + 70 + foot), "white")
    dr = ImageDraw.Draw(canvas)
    dr.text((40, 34), title, font=f(54, True), fill=INK)
    dr.text((40, 112), sub, font=f(30), fill=MUTED)
    for i, (im, (_, cap)) in enumerate(zip(ims, panels)):
        x = i * (pw + 12)
        canvas.paste(im, (x, head))
        dr.rectangle([x, head + ph, x + pw, head + ph + 70], fill=(243, 245, 244))
        dr.text((x + 24, head + ph + 16), cap, font=f(30, True), fill=INK)
    y = head + ph + 70 + 22
    dr.line([40, y + 22, 110, y + 22], fill=YEL, width=8)
    dr.text((126, y + 4), "RGI 7.0 glacier outline, drawn by Google Earth from KML — mapped " + facts["rgi_date"] + " (historical snapshot)", font=f(27), fill=INK)
    dr.text((40, y + 52), facts["line"], font=f(27), fill=INK)
    dr.text((40, y + 96), CREDIT + "  ·  Imagery via Google Earth Pro (provider credits on image)", font=f(27, True), fill=BRAND)
    canvas.save(out, quality=90)


if __name__ == "__main__":
    s2 = R["s2_glaciers"]
    log = []
    for k, g in KG.items():
        shots = {(s["kind"], s["when"]): s for s in SHOTS if s["glacier"] == k}
        ys = s2.get(k, {}).get("years", {})
        snow_line = ""
        if ys:
            y0, y1 = min(ys, key=int), max(ys, key=int)
            snow_line = f"  ·  Sentinel-2 end-of-summer snow {ys[y0]['snow_frac'] * 100:.0f} % ({y0}) to {ys[y1]['snow_frac'] * 100:.0f} % ({y1})"
        facts = {"rgi_date": g["src_date"],
                 "line": f"{g['name']}: {g['area_km2']:.1f} km², {g['zmin_m']:,.0f}–{g['zmax_m']:,.0f} m  ·  surface change {g['d0004']:+.2f} m/yr (2000–04) to {g['d1519']:+.2f} m/yr (2015–19), Hugonnet et al. 2021" + snow_line}
        ov = shots.get(("overview", "2026-10-20"))
        if ov:
            dt_ = shot_date(ov); src = provider(ov["credit"])
            compose([(frame(os.path.join(HERE, "raw", ov["file"])), f"Latest Google Earth imagery · centre-tile date {dt_ or 'not read'} · provider credit on image")],
                    f"{g['name']} — whole glacier", "Google Earth Pro, top-down view; yellow line = the glacier as mapped in the RGI inventory", facts,
                    os.path.join(OUT, f"{k}_overview_annotated.jpg"))
            log.append({"glacier": k, "view": "overview", "imagery_date": dt_, "provider": src})
        tongue = [shots.get(("tongue", d)) for d in ["2010-12-31", "2016-12-31", "2026-10-20"]]
        tongue = [t for t in tongue if t]
        if tongue:
            panels = []
            for t in tongue:
                dt_ = shot_date(t); src = provider(t["credit"])
                panels.append((frame(os.path.join(HERE, "raw", t["file"])), f"Imagery date {dt_ or 'not read'} · provider credit on image"))
                log.append({"glacier": k, "view": "tongue", "requested": t["when"], "imagery_date": dt_, "provider": src})
            compose(panels, f"{g['name']} — the tongue then and now", "Same camera (9 km range, top-down) at each historical imagery date available in Google Earth Pro", facts,
                    os.path.join(OUT, f"{k}_tongue_then_now_annotated.jpg"))
    json.dump(log, open(os.path.join(OUT, "imagery_dates.json"), "w"), indent=1)
    for l in log: print(l)
