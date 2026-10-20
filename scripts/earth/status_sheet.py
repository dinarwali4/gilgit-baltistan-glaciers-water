"""Stack Earth status-bar crops (imagery date) for every shot so dates can be read by eye.
RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali."""
import os, json, importlib.util
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("a", os.path.join(HERE, "annotate.py")); a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
shots = [json.loads(l) for l in open(os.path.join(HERE, "shots.jsonl"))]
rows = []
for s in shots:
    p = os.path.join(HERE, "raw", s["file"])
    if not os.path.exists(p): continue
    im = Image.open(p); W, H = im.size
    crop = im.crop((int(W * .52), H - 46, int(W * .72), H)).resize((int(W * .2 * 1.6), int(46 * 1.6)))
    rows.append((f"{s['glacier']} {s['kind']} {s['when']} -> parsed {a.imagery_date(s['status'])}", crop))
f = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 22)
sh = Image.new("RGB", (1500, 80 * len(rows)), "white"); d = ImageDraw.Draw(sh)
for i, (t, c) in enumerate(rows):
    d.text((10, i * 80 + 25), t, font=f, fill=(0, 0, 0)); sh.paste(c, (560, i * 80))
sh.save(os.path.join(HERE, "raw", "_status_sheet.png")); print(len(rows))
