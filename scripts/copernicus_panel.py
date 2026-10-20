"""Panel of Copernicus Browser captures (Sentinel-2 L2A, most recent clear scenes), annotated and credited.

RegenX.eco Geospatial Computational Model - designed and prepared by Mr. Dinar Wali.
"""
import os, json
from PIL import Image, ImageDraw, ImageFont

H = os.path.join(os.path.dirname(__file__), "..")
C = os.path.join(H, "copernicus")
FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
f = lambda sz, b=False: ImageFont.truetype(FONT, sz, index=1 if b else 0)
INK, MUTED, BRAND = (31, 35, 40), (91, 99, 110), (74, 117, 38)
caps = [json.loads(l) for l in open(os.path.join(C, "captures.jsonl"))]
order = ["cb_baltoro_2026-10-03_truecolor.jpg", "cb_biafo_2026-10-03_truecolor.jpg", "cb_hispar_2026-10-01_truecolor.jpg",
         "cb_hunza_batura_passu_2026-08-17_truecolor.jpg", "cb_hispar_2026-10-16_truecolor_firstsnow.jpg"]
label = {"cb_baltoro_2026-10-03_truecolor.jpg": "Baltoro and Concordia · 3 Oct 2026 · 3.3 % scene cloud",
         "cb_biafo_2026-10-03_truecolor.jpg": "Biafo · 3 Oct 2026 · 1.5 % scene cloud",
         "cb_hispar_2026-10-01_truecolor.jpg": "Hispar · 1 Oct 2026 · 8.4 % scene cloud",
         "cb_hunza_batura_passu_2026-08-17_truecolor.jpg": "Hunza: Batura, Passu, Attabad Lake · 17 Aug 2026 · 1.0 % cloud",
         "cb_hispar_2026-10-16_truecolor_firstsnow.jpg": "Hispar · 16 Oct 2026 · first autumn snow buries the ice (panel open)"}
tw, th = 1200, 750
cols, rows = 2, 3
W = cols * tw + (cols + 1) * 30
Hh = 210 + rows * (th + 80) + 150
cv = Image.new("RGB", (W, Hh), "white"); dr = ImageDraw.Draw(cv)
dr.text((30, 34), "Most recent clear Sentinel-2 views, as seen in the Copernicus Browser", font=f(52, True), fill=INK)
dr.text((30, 110), "Copernicus Data Space Ecosystem · Sentinel-2 L2A · True colour (B4, B3, B2) · scenes chosen from the CDSE catalogue (cloud ≤ 25 %), Aug–Oct 2026",
        font=f(28), fill=MUTED)
for i, fn in enumerate(order):
    im = Image.open(os.path.join(C, fn)).convert("RGB").resize((tw, th))
    x = 30 + (i % cols) * (tw + 30); y = 190 + (i // cols) * (th + 80)
    cv.paste(im, (x, y)); dr.rectangle([x, y, x + tw - 1, y + th - 1], outline=(208, 212, 217), width=2)
    dr.text((x + 4, y + th + 14), label[fn], font=f(30, True), fill=INK)
x = 30 + (len(order) % cols) * (tw + 30); y = 190 + (len(order) // cols) * (th + 80)
note = ["How to read these views",
        "• Grey-brown ribbons are debris-covered glacier tongues;",
        "  white above them is snow and clean ice.",
        "• The same scenes feed the snow-line and snow-cover",
        "  measurements in this assessment (Earth Engine copy",
        "  of the identical ESA L2A product).",
        "• The 16 Oct scene shows why late-season scenes can't",
        "  measure melt: one storm resets the surface."]
for k, t in enumerate(note):
    dr.text((x + 10, y + 20 + k * 56), t, font=f(32, k == 0), fill=INK if k == 0 else MUTED)
dr.text((30, Hh - 110), "Contains modified Copernicus Sentinel data 2026, processed by ESA. Browser captures at 800 × 500 px; full-resolution renders are in the report.",
        font=f(27), fill=MUTED)
dr.text((30, Hh - 66), "RegenX.eco Geospatial Computational Model  ·  Designed and prepared by Mr. Dinar Wali", font=f(29, True), fill=BRAND)
cv.save(os.path.join(H, "maps", "G10_copernicus_browser_recent_scenes.jpg"), quality=88)
print("ok", cv.size)
