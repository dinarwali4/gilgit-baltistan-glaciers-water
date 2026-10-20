// Gilgit-Baltistan Glaciers & Water 2000–2026 — presentation builder.
// RegenX.eco Geospatial Computational Model · Designed and prepared by Mr. Dinar Wali.
// Run: NODE_PATH="$(npm root -g)" PPTX_SKILL=<pptx skill dir> node build.js
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");
const path = require("path");
const fs = require("fs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "data.json"), "utf8"));
const SZ = JSON.parse(fs.readFileSync(path.join(__dirname, "img", "sizes.json"), "utf8"));
const IMG = (f) => path.join(__dirname, "img", f);
const EARTH = path.join(__dirname, "..", "earth", "annotated");
const OUT = process.argv[2] || path.join(__dirname, "Gilgit_Baltistan_Glaciers_Water_2000_2026_Dinar_Wali.pptx");

const THEME = {
  name: "RegenX Glacier", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "16242A", lt1: "FFFFFF", dk2: "0E2F3A", lt2: "EEF3F1", accent1: "76AD41", accent2: "B3471A",
            accent3: "2F78B5", accent4: "4A7526", accent5: "B8860B", accent6: "5F6E73", hlink: "2F78B5", folHlink: "4A7526" },
};
const H = THEME.colors;
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Dinar Wali"; pres.company = "RegenX.eco"; pres.title = "Gilgit-Baltistan Glaciers and Water 2000–2026";
const C = pres.SchemeColor;
const W = 13.333, M = 0.6;

pres.defineSlideMaster({ title: "TITLE_DARK", background: { color: C.text2 }, objects: [
  { placeholder: { options: { name: "title", type: "title", x: M, y: 1.6, w: 6.4, h: 2.1, fontFace: THEME.headFontFace, fontSize: 40, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
  { placeholder: { options: { name: "body", type: "body", x: M, y: 3.85, w: 6.2, h: 1.1, fontSize: 18, color: C.background2, valign: "top", align: "left", margin: 0 }, text: "" } }] });
pres.defineSlideMaster({ title: "CONTENT", background: { color: C.background1 }, margin: [0.5, M, 0.6, M], objects: [
  { placeholder: { options: { name: "title", type: "title", x: M, y: 0.32, w: W - 2 * M, h: 0.85, fontFace: THEME.headFontFace, fontSize: 30, bold: true, color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
  { text: { text: "RegenX.eco Geospatial Computational Model  ·  Designed and prepared by Mr. Dinar Wali", options: { x: M, y: 7.02, w: 9, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } }],
  slideNumber: { x: W - M - 0.6, y: 7.02, w: 0.6, h: 0.3, fontSize: 10, color: C.accent6, align: "right", margin: 0 } });
pres.defineSlideMaster({ title: "CLOSING_DARK", background: { color: C.text2 }, objects: [
  { placeholder: { options: { name: "title", type: "title", x: M, y: 0.4, w: W - 2 * M, h: 0.9, fontFace: THEME.headFontFace, fontSize: 32, bold: true, color: C.background1, valign: "middle", align: "left", margin: 0 }, text: "" } }] });

async function icon(Comp, color = "#FFFFFF") {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color, size: "256" }));
  return "image/png;base64," + (await sharp(Buffer.from(svg)).png().toBuffer()).toString("base64");
}
const fit = (iw, ih, bw, bh) => { const s = Math.min(bw / iw, bh / ih); return { w: iw * s, h: ih * s }; };
function figure(slide, file, iw, ih, x, y, bw, bh, name, alt) {
  const { w, h } = fit(iw, ih, bw, bh);
  slide.addShape(pres.shapes.RECTANGLE, { x: x - 0.06, y: y - 0.06, w: w + 0.12, h: h + 0.12, fill: { color: C.background1 }, line: { color: "D5DCD8", width: 0.75 }, objectName: name + " frame" });
  slide.addImage({ path: file, x, y, w, h, altText: alt, objectName: name });
  return { w, h };
}
function points(slide, items, x, y, w, h, name, size = 15) {
  slide.addText(items.flatMap((it, i) => {
    const runs = [{ text: it.b + " ", options: { bold: true, color: H.dk2 } }, { text: it.t, options: {} }];
    runs[0].options.bullet = { indent: 18 }; runs[1].options.breakLine = i < items.length - 1; return runs;
  }), { x, y, w, h, fontSize: size, color: C.text1, paraSpaceAfter: 10, valign: "top", margin: 0, isTextBox: true, objectName: name });
}
function callouts(slide, items, x, w, name) {
  items.forEach((c, i) => {
    const y = 1.45 + i * 1.75;
    slide.addText(c.v, { x, y, w, h: 0.6, fontFace: THEME.headFontFace, fontSize: 28, bold: true, color: c.col || C.accent2, margin: 0, isTextBox: true, objectName: `${name} ${i + 1} value` });
    slide.addText([{ text: c.l, options: { bold: true, breakLine: true } }, { text: c.d, options: { color: H.accent6 } }],
      { x, y: y + 0.6, w, h: 1.05, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: `${name} ${i + 1} text` });
  });
}
const chartText = { catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt",
  catAxisLabelColor: H.accent6, valAxisLabelColor: H.accent6, catAxisLabelFontSize: 11, valAxisLabelFontSize: 11,
  valGridLine: { color: "DCE3E0", size: 0.5 }, catGridLine: { style: "none" }, valAxisTitleFontSize: 12, valAxisTitleColor: H.accent6 };
const note = (s, t, w = 8.3) => s.addText(t, { x: M, y: 6.55, w, h: 0.3, fontSize: 10, color: C.accent6, margin: 0, isTextBox: true, objectName: "chart note" });

(async () => {
  const ic = { ice: await icon(fa.FaMountain), sat: await icon(fa.FaSatellite), snow: await icon(fa.FaSnowflake), temp: await icon(fa.FaTemperatureHigh),
    img: await icon(fa.FaImage), well: await icon(fa.FaFaucetDrip), radar: await icon(fa.FaTowerBroadcast), sync: await icon(fa.FaArrowsRotate), gauge: await icon(fa.FaWater) };

  // 1 Title
  pres.addSection({ title: "Opening" });
  let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Opening" });
  s.addText("Gilgit-Baltistan Glaciers & Water 2000–2026", { placeholder: "title" });
  s.addText("How fast the ice is going, what is driving it, and what it means for water", { placeholder: "body" });
  s.addText("SITE ASSESSMENT  ·  GILGIT-BALTISTAN  ·  20 OCTOBER 2026", { x: M, y: 1.05, w: 6.4, h: 0.35, fontSize: 12, bold: true, charSpacing: 2, color: "A9C7BF", margin: 0, isTextBox: true, objectName: "kicker" });
  s.addShape(pres.shapes.RECTANGLE, { x: M, y: 5.3, w: 0.5, h: 0.08, fill: { color: C.accent1 }, line: { type: "none" }, objectName: "brand mark" });
  s.addText([{ text: "RegenX.eco Geospatial Computational Model", options: { bold: true, breakLine: true } }, { text: "Designed and prepared by Mr. Dinar Wali" }],
    { x: M, y: 5.55, w: 6.4, h: 0.75, fontSize: 15, color: C.background1, margin: 0, isTextBox: true, objectName: "credit" });
  s.addText("RGI 7.0  ·  Hugonnet 2021  ·  GRACE/GRACE-FO  ·  MODIS  ·  ERA5-Land  ·  CMIP6  ·  Sentinel-2  ·  Google Earth Pro", { x: M, y: 6.55, w: 6.6, h: 0.35, fontSize: 11, color: "A9C7BF", margin: 0, isTextBox: true, objectName: "sources" });
  { const [iw, ih] = SZ.cover; const { w, h } = fit(iw, ih, 5.7, 6.3);
    s.addImage({ path: IMG("s2_baltoro_2026.png"), x: 7.25, y: (7.5 - h) / 2, w, h, altText: "Sentinel-2 true colour of Baltoro Glacier, 29 Aug 2026", objectName: "cover image" });
    s.addText("Baltoro Glacier, Sentinel-2 L2A, 29 Aug 2026", { x: 7.25, y: (7.5 + h) / 2 + 0.05, w, h: 0.3, fontSize: 10, color: "A9C7BF", margin: 0, isTextBox: true, objectName: "cover caption" }); }
  s.addNotes("Gilgit-Baltistan Glaciers & Water 2000–2026. RegenX.eco Geospatial Computational Model, designed and prepared by Mr. Dinar Wali, 20 October 2026. Cover: Copernicus Sentinel-2 L2A true colour, Baltoro Glacier, 29 Aug 2026.");

  // 2 Answer
  pres.addSection({ title: "Answer" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Answer" });
  s.addText("The ice is going faster, and heat is driving it", { placeholder: "title" });
  const cw = (W - 2 * M - 3 * 0.3) / 4;
  [["12,880", "km²", "Glacier area in GB", "8,633 glaciers, RGI 7.0 (10,738 km² without the Siachen sector).", C.text2],
   ["−0.120", "", "Loss 2015–19, m w.e./yr", "Up from +0.043 in 2000–04: loss grew every five years. −1.5 Gt of water a year.", C.accent2],
   ["−2.4 to −4.1", "", "Stored water, km³/yr", "GRACE total storage trend since 2018 (GFZ to CSR); 2026 is the lowest year.", C.accent2],
   ["+2.8", "°C", "Summer 2025 vs normal", "Warmest GB summer on record (ERA5-Land); winters near-normal.", C.accent2]].forEach(([v, u, l, d, col], i) => {
    const x = M + i * (cw + 0.3);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: cw, h: 2.7, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: `stat ${i + 1} card` });
    s.addText([{ text: v, options: { fontSize: v.length > 8 ? 25 : 32 } }, { text: u ? " " + u : "", options: { fontSize: 16 } }], { x: x + 0.25, y: 1.68, w: cw - 0.5, h: 0.75, fontFace: THEME.headFontFace, bold: true, color: col, valign: "bottom", margin: 0, isTextBox: true, objectName: `stat ${i + 1} value` });
    s.addText(l, { x: x + 0.25, y: 2.45, w: cw - 0.5, h: 0.5, fontSize: 15, bold: true, color: C.text1, margin: 0, isTextBox: true, objectName: `stat ${i + 1} label` });
    s.addText(d, { x: x + 0.25, y: 2.95, w: cw - 0.5, h: 1.15, fontSize: 12, color: C.accent6, margin: 0, valign: "top", isTextBox: true, objectName: `stat ${i + 1} source` });
  });
  s.addText([{ text: "Gilgit-Baltistan is spending its ice buffer. ", options: { bold: true, color: H.dk2 } },
    { text: "Glacier loss has accelerated since 2000, stored water fell sharply after 2023, and every recent hot summer left the glaciers barer. Snowfall has not declined: the driver is heat, and the models say summers warm another 1.3–1.7 °C by mid-century." }],
    { x: M, y: 4.6, w: W - 2 * M, h: 1.5, fontSize: 19, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: "summary" });
  s.addText("1 Gt of ice melted = 1 km³ = 1 billion m³ of water.", { x: M, y: 6.4, w: W - 2 * M, h: 0.35, fontSize: 12, italic: true, color: C.accent6, margin: 0, isTextBox: true, objectName: "units" });
  s.addNotes("Glacier area: RGI 7.0 polygons with centroid in the geoBoundaries GB polygon. Mass: Hugonnet et al. 2021 dh/dt × area × 850 kg/m³; 2015–19 −0.141 m/yr × 12,638 km² × 0.85 = −1.51 Gt/yr. Stored water: GRACE-FO-era trend, GFZ −3.41 and CSR −5.93 cm/yr × 69,078 km². Summer: ERA5-Land JJA 2025 = 6.42 °C vs 3.62 °C 2001–20 mean.");

  // 3 Method
  pres.addSection({ title: "Method" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Method" });
  s.addText("Six independent satellite layers", { placeholder: "title" });
  [[ic.ice, "Glaciers", "RGI 7.0 outlines + Hugonnet et al. 2021 elevation change", "8,633 glaciers · 2000–2019 · 100 m"],
   [ic.sat, "Stored water", "GRACE/GRACE-FO from UT-CSR, GFZ and NASA-JPL", "Apr 2002 – Aug 2026 · ~300 km"],
   [ic.snow, "Snow", "MODIS Terra MOD10A1 snow cover", "2001 – Sep 2026 · 500 m daily"],
   [ic.temp, "Climate", "ERA5-Land observed; NEX-GDDP-CMIP6 projected (12 models)", "2000–2026 · 1985–2100"],
   [ic.img, "Imagery", "Sentinel-2 L2A (Copernicus Browser + Earth Engine); Google Earth Pro Airbus/Maxar", "2010 – Oct 2026 · 0.5–10 m"]].forEach(([ico, hd, what, when], i) => {
    const y = 1.45 + i * 1.07;
    s.addShape(pres.shapes.OVAL, { x: M, y: y + 0.05, w: 0.72, h: 0.72, fill: { color: C.text2 }, line: { type: "none" }, objectName: `layer ${i + 1} badge` });
    s.addImage({ data: ico, x: M + 0.18, y: y + 0.23, w: 0.36, h: 0.36, objectName: `layer ${i + 1} icon`, altText: hd });
    s.addText(hd, { x: M + 1.0, y, w: 2.4, h: 0.82, fontFace: THEME.headFontFace, fontSize: 20, bold: true, color: C.text2, valign: "middle", margin: 0, isTextBox: true, objectName: `layer ${i + 1} name` });
    s.addText([{ text: what, options: { bold: true, breakLine: true } }, { text: when, options: { color: H.accent6 } }], { x: M + 3.5, y, w: 8.6, h: 0.82, fontSize: 15, color: C.text1, valign: "middle", margin: 0, isTextBox: true, objectName: `layer ${i + 1} source` });
  });
  s.addNotes("Same tools and logic as the Pakistan-wide assessment, narrowed to Gilgit-Baltistan. Earth Engine copy of RGI 7.0 verified against the NSIDC download (Shisper identical). Sentinel-2 from the harmonised collection (no post-2022 offset bias) with same-date tiles mosaicked.");

  // 4 Glacier map
  pres.addSection({ title: "Glaciers" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Glaciers" });
  s.addText("Thinning is concentrated in the big Karakoram valleys", { placeholder: "title" });
  figure(s, IMG("G1_glacier_elevation_change_2000_2019_c.png"), ...SZ["G1_glacier_elevation_change_2000_2019.png"], M, 1.35, 9.2, 5.5, "glacier map", "Map of 2000–2019 glacier elevation change across GB");
  points(s, [{ b: "Hispar", t: "−0.35 m/yr, Braldu −0.43, Panmah −0.20 (2000–19 means)." },
    { b: "Baltoro and Batura", t: "−0.08 m/yr: near balance, the 'Karakoram anomaly'." },
    { b: "Shigar, Ghanche, Hunza", t: "hold most of the ice and most of the loss." }], 10.1, 1.5, 2.65, 5, "map points", 14);
  s.addNotes("Hugonnet et al. 2021 elevation change 2000–2019, masked to RGI 7.0 glaciers. Brown thinning, blue thickening. The dotted box is the Siachen sector, administered by India and included in the geoBoundaries GB polygon.");

  // 5 Acceleration (native)
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Glaciers" });
  s.addText("Glacier loss grew in every five-year period", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [{ name: "GB (geoBoundaries)", labels: D.periods, values: D.mwe_gb }, { name: "GB excl. Siachen sector", labels: D.periods, values: D.mwe_ex }], {
    x: M, y: 1.4, w: 8.3, h: 5.1, barDir: "col", barGapWidthPct: 50, ...chartText, chartColors: [H.dk2, H.accent1], showLegend: true, legendPos: "t", legendFontSize: 12, legendColor: H.dk1,
    showValue: true, dataLabelFormatCode: "+0.000;-0.000", dataLabelFontSize: 11, dataLabelColor: H.dk1, valAxisMinVal: -0.14, valAxisMaxVal: 0.08, valAxisMajorUnit: 0.04,
    showValAxisTitle: true, valAxisTitle: "Mass balance (m water equivalent per year)", objectName: "acceleration chart" });
  note(s, "Hugonnet et al. 2021, 100 m, 92 % of glacier area with valid data; ice/firn density 850 kg/m³.");
  callouts(s, [{ v: "−0.10", l: "m w.e./yr per decade", d: "The rate of acceleration, with or without the Siachen sector." },
    { v: "−1.5 Gt/yr", l: "of water in 2015–19", d: "Up from a small gain of +0.5 Gt/yr in 2000–04." },
    { v: "2.7×", l: "faster loss than 2005–09", d: "From −0.044 to −0.120 m w.e. per year." }], 9.3, 3.45, "accel");
  s.addNotes("Five-year GB means: +0.043, −0.044, −0.066, −0.120 m w.e./yr; excluding the Siachen sector +0.057, −0.031, −0.051, −0.115. Linear fit of period means: −0.102 (GB) and −0.107 (excl.) m w.e./yr per decade. Per-pixel error maps were not averaged; the signal is the period difference.");

  // 6 Stored water (native)
  pres.addSection({ title: "Stored water" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Stored water" });
  s.addText("Stored water fell sharply after 2023", { placeholder: "title" });
  const yl = D.years.map((y) => (y === "2026" ? "2026*" : y));
  s.addChart(pres.charts.LINE, [{ name: "UT-CSR", labels: yl, values: D.csr }, { name: "GFZ GravIS", labels: yl, values: D.gfz }, { name: "NASA-JPL (to 2024)", labels: yl, values: D.jpl }], {
    x: M, y: 1.4, w: 8.3, h: 5.1, ...chartText, chartColors: [H.dk2, H.accent3, H.accent1], lineSize: 2.25, lineDataSymbol: "circle", lineDataSymbolSize: 6, displayBlanksAs: "gap",
    showLegend: true, legendPos: "t", legendFontSize: 12, legendColor: H.dk1, valAxisMinVal: -55, valAxisMaxVal: 15, valAxisMajorUnit: 10,
    showValAxisTitle: true, valAxisTitle: "Annual anomaly vs 2004–2009 (cm of water)", catAxisLabelFrequency: 2, objectName: "grace chart" });
  note(s, "Seasonal cycle removed. 2017–18: mission gap. *2026 = Jan–Aug. GB spans 1–2 GRACE mascons: read annual means only.");
  callouts(s, [{ v: "r = 0.95–0.97", l: "Three solutions agree to 2024", d: "2024: CSR −16.4, GFZ −17.3, JPL −16.3 cm.", col: C.accent4 },
    { v: "−32 to −50 cm", l: "2026 anomaly (Jan–Aug)", d: "GFZ to CSR: same direction, 35 % apart in size." },
    { v: "−2.4 to −4.1", l: "km³ per year since 2018", d: "GFZ −3.41 to CSR −5.93 cm/yr over 69,078 km²." }], 9.3, 3.45, "grace");
  s.addNotes("Area-weighted GRACE TWS over the GB polygon. CSR RL06.3 mascons, GFZ GravIS RL06 v0006, JPL RL06.3 CRI (ends Sep 2024). Single months are noisy (Jul→Aug 2026 swings 65 cm). GFZ's leakage-corrected series is larger still (2026 −89 cm) but is modelled, not used for the headline.");

  // 7 Regional pattern
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Stored water" });
  s.addText("The 2025–26 drop follows the Karakoram belt", { placeholder: "title" });
  figure(s, IMG("G4_hma_anomaly_2025_26_c.png"), ...SZ["G4_hma_anomaly_2025_26.png"], M, 1.35, 9.3, 5.5, "hma map", "Map of 2025–26 storage anomaly across High Mountain Asia");
  points(s, [{ b: "Biggest falls:", t: "GB −34 cm, Ladakh −30, Pamir −24." },
    { b: "Little change:", t: "western Kunlun −3, central Tibet 0." },
    { b: "So it is real:", t: "a uniform satellite offset would move every region alike." }], 10.2, 1.5, 2.55, 5, "hma points", 14);
  s.addNotes("CSR RL06.3 mascons; per-cell monthly climatology 2004–2022 removed; mean Jan 2025–Aug 2026 minus mean 2019–2023. Box means: GB core 35–37N 72.5–77E −34.1; Ladakh −30.2; Pamir 37.5–40N 71–75E −23.8; W Kunlun −2.5; C Tibet −0.2; Hindu Kush −5.7; Nepal Himalaya −14.9 cm.");

  // 8 Heat (native)
  pres.addSection({ title: "Drivers" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Drivers" });
  s.addText("Hot summers, not missing snow, drive the melt", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [{ name: "Summer temperature vs 2001–2020 (°C)", labels: D.jja_years, values: D.jja_anom }], {
    x: M, y: 1.4, w: 8.3, h: 5.1, barDir: "col", barGapWidthPct: 35, ...chartText, chartColors: [H.accent2], invertIfNegative: true, invertedColors: [H.accent3], showLegend: false,
    valAxisMinVal: -2, valAxisMaxVal: 3, valAxisMajorUnit: 1, showValAxisTitle: true, valAxisTitle: "Jun–Aug temperature vs 2001–2020 (°C)", catAxisLabelFrequency: 5, objectName: "heat chart" });
  note(s, "ERA5-Land monthly, GB area mean.");
  callouts(s, [{ v: "+2.8 °C", l: "Summer 2025", d: "Warmest in the record; 2026 +1.4 °C." },
    { v: "−5 %", l: "Winter precipitation 2025, 2026", d: "Near normal: missing snowfall does not explain the low.", col: C.accent3 },
    { v: "r = −0.79", l: "Warm summer ↔ bare glaciers", d: "ERA5 vs MODIS, 26 years, p ≈ 10⁻⁶.", col: C.accent4 }], 9.3, 3.45, "heat");
  s.addNotes("Test: Pearson r between ERA5-Land JJA temperature and MODIS August snow fraction on RGI 7.0 glacier area, 2001–2026: −0.79 (p 1.3e-6); Spearman −0.83. Winter (Oct–Mar) precipitation 2025: 400 mm, 2026: 399 mm vs 420 mm 2001–20 normal.");

  // 9 August snow (native)
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Drivers" });
  s.addText("Less snow survives on the ice each August", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [{ name: "August snow on glaciers (%)", labels: D.aug_years, values: D.aug_snow }], {
    x: M, y: 1.4, w: 8.3, h: 5.1, barDir: "col", barGapWidthPct: 35, ...chartText, chartColors: ["8FBFE0"], showLegend: false,
    valAxisMinVal: 40, valAxisMaxVal: 80, valAxisMajorUnit: 10, showValAxisTitle: true, valAxisTitle: "% of glacier area snow-covered (August mean)", catAxisLabelFrequency: 5, objectName: "aug snow chart" });
  note(s, "MODIS Terra MOD10A1 v6.1, NDSI snow cover ≥ 40, cloud-free days, RGI 7.0 glacier area.");
  callouts(s, [{ v: "−0.4 pts/yr", l: "August glacier snow trend", d: "Mann-Kendall p = 0.04; OLS p = 0.005." },
    { v: "2022 · 2024 · 2025", l: "The three barest Augusts", d: "51–53 % snow against a 63 % normal." },
    { v: "No trend", l: "in seasonal snow over GB", d: "Spring varies ±20 % a year; 2025 −14 %, 2026 normal.", col: C.text2 }], 9.3, 3.45, "aug");
  s.addNotes("August snow fraction on glaciers: 2001–20 mean 63.2 %; 2022 51.3 %, 2024 52.6 %, 2025 52.9 %, 2026 55.0 %. Spring (Apr–Jun) GB snow: no trend (MK p 0.63). Snow extent, not water equivalent.");

  // 10 Key glaciers S2
  pres.addSection({ title: "Key glaciers" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Key glaciers" });
  s.addText("Six key glaciers: 2025–26 are the barest yet", { placeholder: "title" });
  figure(s, IMG("G8_s2_end_of_season_snow_c.png"), ...SZ.G8, M, 1.35, 12.1, 5.0, "s2 series", "End-of-summer snow cover on six key glaciers, Sentinel-2");
  s.addText("Bars: % snow-covered at the scene nearest 1 September; numbers: snow-line altitude (m). Only Hispar's decline is significant (p 0.03). Passu is clean ice: not interpretable.",
    { x: M, y: 6.5, w: W - 2 * M, h: 0.4, fontSize: 12, color: C.accent6, margin: 0, isTextBox: true, objectName: "s2 note" });
  s.addNotes("Copernicus Sentinel-2 L2A (harmonised), same-date tiles mosaicked, in-outline coverage ≥ 90 %, cloud ≤ 10 %, NDSI ≥ 0.40. Lowest year: Baltoro 2025, Biafo 2025, Hispar 2026, Batura 2025, Shisper 2025, Passu 2025. Baltoro snow line 4,400–4,500 m → 4,800 m in 2025–26.");

  // 11+ Earth Pro then/now, one glacier per slide
  const OBS = JSON.parse(fs.readFileSync(path.join(__dirname, "earth_observations.json"), "utf8"));
  for (const k of ["shisper", "hispar", "batura", "baltoro", "biafo", "passu"]) {
    const f = path.join(EARTH, `${k}_tongue_then_now_annotated.jpg`);
    if (!fs.existsSync(f) || !OBS[k]) continue;
    s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Key glaciers" });
    s.addText(OBS[k].title, { placeholder: "title" });
    const meta = await_size(f);
    const { h } = figure(s, f, meta[0], meta[1], M, 1.35, W - 2 * M, 3.4, `earth ${k}`, `Google Earth Pro imagery of the ${k} glacier tongue at three dates with its RGI outline`);
    points(s, OBS[k].points, M, 1.35 + h + 0.35, W - 2 * M, 6.85 - (1.35 + h + 0.35), `earth ${k} notes`, 15);
    s.addNotes("Google Earth Pro historical high-resolution imagery (provider credits burned into each frame: Airbus, Maxar Technologies, CNES), top-down, 9 km range, captured by script from a KML camera; yellow line = RGI 7.0 outline rendered by Earth itself from KML (historical snapshot). Imagery dates read from Earth's status bar and checked by eye for Shisper. Pre-2010 imagery over GB is Landsat-grade only, so 2010 is the earliest high-resolution date. " + (OBS[k].note || ""));
  }

  // 13 Copernicus
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Key glaciers" });
  s.addText("Latest clear scenes in the Copernicus Browser", { placeholder: "title" });
  figure(s, IMG("G10_copernicus_browser_recent_scenes_c.png"), ...SZ.G10, M, 1.35, 6.2, 5.55, "copernicus panel", "Copernicus Browser captures of recent Sentinel-2 scenes");
  points(s, [{ b: "3 Oct 2026:", t: "Baltoro and Biafo, 1.5–3.3 % cloud." }, { b: "1 Oct 2026:", t: "Hispar, 8.4 % cloud." },
    { b: "17 Aug 2026:", t: "Batura, Passu and Attabad Lake, 1 % cloud." }, { b: "16 Oct 2026:", t: "first autumn snow buries Hispar, so melt is measured nearest 1 September." }], 7.2, 1.5, 5.5, 5, "cb points", 15);
  s.addNotes("Copernicus Data Space Ecosystem Browser, Sentinel-2 L2A true colour; scenes picked from the CDSE OData catalogue (no login). Contains modified Copernicus Sentinel data 2026.");

  // 14 Going forward (native)
  pres.addSection({ title: "Going forward" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Going forward" });
  s.addText("Going forward: summers warm 1.3–1.7 °C by mid-century", { placeholder: "title" });
  s.addChart(pres.charts.LINE, [{ name: "SSP2-4.5", labels: D.cmip_years, values: D.cmip245 }, { name: "SSP5-8.5", labels: D.cmip_years, values: D.cmip585 }], {
    x: M, y: 1.4, w: 7.6, h: 5.1, ...chartText, chartColors: [H.accent3, H.accent2], lineSize: 2, lineDataSymbol: "none", showLegend: true, legendPos: "t", legendFontSize: 12, legendColor: H.dk1,
    valAxisMinVal: -1, valAxisMaxVal: 8, valAxisMajorUnit: 1, showValAxisTitle: true, valAxisTitle: "Summer temperature vs 1995–2014 (°C, 12-model median)", catAxisLabelFrequency: 10, objectName: "cmip chart" });
  note(s, "NASA NEX-GDDP-CMIP6, GB mean; each model vs its own 1995–2014. Modelled, not a forecast.", 7.6);
  const P_ = D.proj, f1 = (x) => (x >= 0 ? "+" : "") + x.toFixed(1), f0 = (x) => (x >= 0 ? "+" : "") + x.toFixed(0);
  s.addTable([
    [{ text: "", options: { fill: { color: H.dk2 } } }, { text: "2041–60", options: { bold: true, color: H.lt1, fill: { color: H.dk2 } } }, { text: "2081–2100", options: { bold: true, color: H.lt1, fill: { color: H.dk2 } } }],
    ["SSP2-4.5 summer °C", `${f1(P_.ssp245["2041-2060"].dT_median)} (${f1(P_.ssp245["2041-2060"].dT_min)}…${f1(P_.ssp245["2041-2060"].dT_max)})`, `${f1(P_.ssp245["2081-2100"].dT_median)} (${f1(P_.ssp245["2081-2100"].dT_min)}…${f1(P_.ssp245["2081-2100"].dT_max)})`],
    ["SSP5-8.5 summer °C", `${f1(P_.ssp585["2041-2060"].dT_median)} (${f1(P_.ssp585["2041-2060"].dT_min)}…${f1(P_.ssp585["2041-2060"].dT_max)})`, `${f1(P_.ssp585["2081-2100"].dT_median)} (${f1(P_.ssp585["2081-2100"].dT_min)}…${f1(P_.ssp585["2081-2100"].dT_max)})`],
    ["SSP2-4.5 precip %", `${f0(P_.ssp245["2041-2060"].dP_pct_median)} (${f0(P_.ssp245["2041-2060"].dP_pct_min)}…${f0(P_.ssp245["2041-2060"].dP_pct_max)})`, `${f0(P_.ssp245["2081-2100"].dP_pct_median)} (${f0(P_.ssp245["2081-2100"].dP_pct_min)}…${f0(P_.ssp245["2081-2100"].dP_pct_max)})`],
    ["SSP5-8.5 precip %", `${f0(P_.ssp585["2041-2060"].dP_pct_median)} (${f0(P_.ssp585["2041-2060"].dP_pct_min)}…${f0(P_.ssp585["2041-2060"].dP_pct_max)})`, `${f0(P_.ssp585["2081-2100"].dP_pct_median)} (${f0(P_.ssp585["2081-2100"].dP_pct_min)}…${f0(P_.ssp585["2081-2100"].dP_pct_max)})`],
  ].map((r, i) => r.map((c) => (typeof c === "string" ? { text: c, options: { bold: false, fill: { color: i % 2 ? "FFFFFF" : H.lt2 } } } : c))), {
    x: 8.5, y: 1.5, w: 4.23, colW: [1.6, 1.3, 1.33], rowH: 0.48, fontSize: 12, color: H.dk1, valign: "middle", border: { type: "solid", color: "D5DCD8", pt: 0.5 }, margin: [0.02, 0.06, 0.02, 0.06], objectName: "projection table" });
  points(s, [{ b: "More melt first:", t: "warmer summers spend more ice, as 2025 showed." }, { b: "Then less:", t: "flow falls once there is too little ice left — timing not modelled here." },
    { b: "Rain or snow:", t: "models disagree, even on sign before 2060." }], 8.5, 4.2, 4.23, 2.6, "forward points", 13);
  s.addNotes("Median (min…max) across 12 models: ACCESS-CM2, CanESM5, CNRM-ESM2-1, EC-Earth3, GFDL-ESM4, INM-CM5-0, IPSL-CM6A-LR, MIROC6, MPI-ESM1-2-HR, MRI-ESM2-0, NorESM2-MM, UKESM1-0-LL. Test: model 2000–25 summer warming (median +0.26 °C/decade, range 0.10–1.74) brackets ERA5-Land (+0.31). Peak-water timing was not modelled; no date is claimed.");

  // 15 Validation
  pres.addSection({ title: "Validation" });
  s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Validation" });
  s.addText("Validation scorecard: what passed, what did not", { placeholder: "title" });
  const st = { PASS: ["E3EFD8", H.accent4], FAIL: ["F6E0D6", H.accent2], PARTLY: ["F4ECD4", "6B5200"], NO: ["F4ECD4", "6B5200"] };
  const rows = [["RGI 7.0 copy vs NSIDC download", "Shisper identical: 36.83 km², 1997-08-10, surge 3", "PASS"],
    ["Three GRACE solutions", "r = 0.95–0.97; 2024 within 1 cm", "PASS"],
    ["2025–26 drop in GFZ too", "Same direction, 35 % smaller", "PARTLY"],
    ["Drop is regional, not an offset", "GB −34, Pamir −24; Tibet 0 cm", "PASS"],
    ["Robust without Siachen sector", "Acceleration −0.10 vs −0.11 m w.e./yr/decade", "PASS"],
    ["Warm summers ↔ bare glaciers", "r = −0.79, p ≈ 10⁻⁶ (two sensors)", "PASS"],
    ["Models vs observed warming", "ERA5 +0.31 inside model range 0.10–1.74 °C/dec", "PASS"],
    ["Sentinel-2 record low 2025–26", "6 of 6 glaciers", "PASS"],
    ["Snowfall explains 2025–26?", "Winters −5 %; spring snow 2026 normal", "NO"],
    ["GRACE closes glacier budget", "−0.33 km³/yr vs −1.17 Gt/yr glaciers (2010–19)", "FAIL"]];
  s.addTable([[{ text: "Test", options: { bold: true, color: H.lt1, fill: { color: H.dk2 } } }, { text: "Evidence", options: { bold: true, color: H.lt1, fill: { color: H.dk2 } } }, { text: "Outcome", options: { bold: true, color: H.lt1, fill: { color: H.dk2 }, align: "center" } }],
    ...rows.map(([a, b, c], i) => [{ text: a, options: { bold: true, fill: { color: i % 2 ? H.lt2 : "FFFFFF" } } }, { text: b, options: { fill: { color: i % 2 ? H.lt2 : "FFFFFF" } } },
      { text: c, options: { bold: true, align: "center", color: st[c][1], fill: { color: st[c][0] } } }])],
    { x: M, y: 1.35, w: W - 2 * M, colW: [4.0, 6.33, 1.8], rowH: 0.44, fontSize: 14, color: H.dk1, valign: "middle", border: { type: "solid", color: "D5DCD8", pt: 0.5 }, margin: [0.02, 0.1, 0.02, 0.1], objectName: "validation table" });
  s.addNotes("The GRACE–glacier mismatch is reported as a failure: GB is one or two mascons wide, so GRACE blurs a loss concentrated in a few valleys and on the GB boundary. Single GRACE months are noisy (65 cm swing Jul→Aug 2026); only annual means are used.");

  // 16 Next
  pres.addSection({ title: "Next steps" });
  s = pres.addSlide({ masterName: "CLOSING_DARK", sectionTitle: "Next steps" });
  s.addText("What the evidence supports next", { placeholder: "title" });
  const aW = (W - 2 * M - 3 * 0.3) / 4;
  [[ic.gauge, "Add river gauges", "Pair Indus and Hunza discharge with this storage record to measure, not infer, the melt contribution."],
   [ic.temp, "Plan for hot years", "Summers like 2025 (+2.8 °C) strip the glaciers. Treat them as the planning case, not the outlier."],
   [ic.radar, "Watch the surging glaciers", "Shisper's surge shows ice can advance and dam valleys even while GB loses mass."],
   [ic.sync, "Refresh every season", "Re-run GRACE, MODIS and Sentinel-2 each autumn as new months land."]].forEach(([ico, hd, body], i) => {
    const x = M + i * (aW + 0.3), y = 1.6;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: aW, h: 4.1, rectRadius: 0.08, fill: { color: "17404D" }, line: { type: "none" }, objectName: `action ${i + 1} card` });
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: y + 0.3, w: 0.8, h: 0.8, fill: { color: C.accent1 }, line: { type: "none" }, objectName: `action ${i + 1} badge` });
    s.addImage({ data: ico, x: x + 0.5, y: y + 0.5, w: 0.4, h: 0.4, objectName: `action ${i + 1} icon`, altText: hd });
    s.addText(hd, { x: x + 0.3, y: y + 1.3, w: aW - 0.6, h: 0.9, fontFace: THEME.headFontFace, fontSize: 19, bold: true, color: C.background1, valign: "top", margin: 0, isTextBox: true, objectName: `action ${i + 1} head` });
    s.addText(body, { x: x + 0.3, y: y + 2.25, w: aW - 0.6, h: 1.75, fontSize: 14, color: "D6E4DF", valign: "top", margin: 0, isTextBox: true, objectName: `action ${i + 1} body` });
  });
  s.addText([{ text: "RegenX.eco Geospatial Computational Model", options: { bold: true, breakLine: true } }, { text: "Designed and prepared by Mr. Dinar Wali  ·  dinar.wali@regenx.eco  ·  20 October 2026" }],
    { x: M, y: 6.1, w: 10, h: 0.8, fontSize: 14, color: C.background1, margin: 0, isTextBox: true, objectName: "closing credit" });
  s.addNotes("Each action follows from a tested finding: river flow was not measured (gauges); 2025 heat drove the barest glaciers and lowest storage; Shisper's 2018–20 surge is visible against its 1997 outline; the pipeline re-runs from scripts in the project folder.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})().catch((e) => { console.error(e); process.exit(1); });

function await_size(f) {
  const buf = fs.readFileSync(f);
  // JPEG SOF scan for dimensions
  let i = 2;
  while (i < buf.length) {
    if (buf[i] !== 0xff) { i++; continue; }
    const m = buf[i + 1], len = buf.readUInt16BE(i + 2);
    if (m >= 0xc0 && m <= 0xc3) return [buf.readUInt16BE(i + 7), buf.readUInt16BE(i + 5)];
    i += 2 + len;
  }
  throw new Error("no size " + f);
}
