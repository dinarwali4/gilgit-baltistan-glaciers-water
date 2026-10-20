"""Insert the Google Earth Pro section into report.html (replaces the <!--EARTH--> marker or a previous section).
RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali."""
import os, json, re, html
H = os.path.join(os.path.dirname(__file__), "..")
OBS = json.load(open(os.path.join(H, "deck", "earth_observations.json")))
rep = os.path.join(H, "report.html")
s = open(rep).read()
parts = ['<!--EARTH-START--><h3 class="col">High-resolution imagery in Google Earth Pro</h3>',
         '<p class="col">Each glacier tongue was captured top-down from the same camera at every high-resolution date Google Earth Pro holds '
         '(earlier imagery over GB is Landsat-grade only). The yellow line is the RGI 7.0 outline, drawn by Google Earth itself from KML; '
         'imagery dates were read from Earth\'s status bar.</p>']
for k in ["shisper", "hispar", "batura", "baltoro", "biafo", "passu"]:
    f = f"earth/{k}_tongue_then_now_annotated.jpg"
    if k not in OBS or not os.path.exists(os.path.join(H, "earth", "annotated", f"{k}_tongue_then_now_annotated.jpg")):
        continue
    pts = " ".join(f"<b>{html.escape(p['b'])}</b> {html.escape(p['t'])}" for p in OBS[k]["points"])
    parts.append(f'<figure><img src="{f}" alt="{html.escape(OBS[k]["title"])}: Google Earth Pro imagery of the tongue at three dates" loading="lazy">'
                 f'<figcaption><b>{html.escape(OBS[k]["title"])}.</b> {pts}</figcaption></figure>')
parts.append("<!--EARTH-END-->")
block = "\n".join(parts)
if "<!--EARTH-START-->" in s:
    s = re.sub(r"<!--EARTH-START-->.*?<!--EARTH-END-->", lambda m: block, s, flags=re.S)
else:
    s = s.replace("<!--EARTH-->", block)
open(rep, "w").write(s)
print("inserted", block.count("<figure>"), "Earth figures")
