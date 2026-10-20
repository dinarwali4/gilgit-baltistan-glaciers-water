# Gilgit-Baltistan Glaciers & Water 2000–2026

**RegenX.eco Geospatial Computational Model · Designed and prepared by Mr. Dinar Wali**
Contact: dinar.wali@regenx.eco · Assessment date 20 October 2026

**Live report:** https://dinarwali4.github.io/gilgit-baltistan-glaciers-water/

A satellite assessment of Gilgit-Baltistan's glaciers, snow and stored water: how fast the ice is going, what is driving it, and what that means for water downstream. Each figure names its sensor, dates and resolution, and the report includes a validation table that lists failures as well as passes.

## Headline findings

| Finding | Value | Type |
|---|---|---|
| Glaciers with centre in GB (RGI 7.0) | 8,633 · 12,880 km² (10,738 km² excluding the Siachen sector, administered by India) | Measured |
| Glacier mass balance by five-year period | +0.043 → −0.044 → −0.066 → −0.120 m w.e./yr (2015–19 ≈ −1.5 Gt/yr) | Measured |
| GB total water storage since 2018 | −2.4 to −4.1 km³/yr (GFZ to CSR); 2026 is the lowest year | Measured |
| Summer 2025 temperature | +2.8 °C above 2001–2020, warmest on record; winters near normal | Measured |
| Warm summers vs bare glaciers in August | r = −0.79 (ERA5-Land vs MODIS, 2001–2026) | Test |
| Summer warming by 2041–60 | +1.3 to +1.7 °C (12-model CMIP6 medians) | Modelled |

## Contents

| Path | What it is |
|---|---|
| `index.html` | The report (GitHub Pages) |
| `maps/` | Figures G1–G10 |
| `earth/` | Google Earth Pro then-and-now captures of six key glacier tongues, annotated |
| `copernicus/` | Copernicus Browser captures of the latest clear Sentinel-2 scenes |
| `downloads/` | Presentation (PDF) and Google Earth KMZ |
| `data/` | Computed results (JSON) and geoBoundaries ADM1/ADM2 |
| `scripts/` | The pipeline (Python + Earth Engine), Earth Pro capture scripts, deck builder |

## Data sources

- **Glacier outlines:** Randolph Glacier Inventory 7.0 (GLIMS / NSIDC 0770), via the Earth Engine community catalogue.
- **Glacier change:** Hugonnet, R. et al. (2021) Accelerated global glacier mass loss in the early twenty-first century. *Nature* 592, 726–731. doi:10.1038/s41586-021-03436-z.
- **Stored water:** GRACE / GRACE-FO RL06 solutions from UT-CSR (mascons), GFZ GravIS (doi:10.5880/GFZ.GRAVIS_06_L3_TWS) and NASA-JPL (CRI mascons).
- **Snow:** MODIS Terra MOD10A1 v6.1.
- **Climate:** ECMWF ERA5-Land; NASA NEX-GDDP-CMIP6.
- **Imagery:** Copernicus Sentinel-2 L2A. Contains modified Copernicus Sentinel data 2017–2026. Google Earth Pro historical imagery © Airbus, Maxar Technologies, CNES as credited on each frame.
- **Terrain and boundaries:** Copernicus GLO-30 DEM; geoBoundaries gbOpen (CC BY 4.0).

## Reproduce

Python 3 with `earthengine-api`, `numpy`, `scipy`, `xarray`, `shapely`, `pyproj`, `matplotlib`, `Pillow`. Set `EE_PROJECT` to your Earth Engine cloud project.

```
python scripts/glaciers.py            # RGI 7.0 census + Hugonnet mass change
python scripts/export_outlines.py     # outlines for KML and maps
python scripts/snow_climate.py        # MODIS snow + ERA5-Land climate
python scripts/cmip6.py               # NEX-GDDP-CMIP6 projections
python scripts/s2_glaciers.py         # Sentinel-2 end-of-summer snow, six glaciers
python scripts/grace_gb.py <gfz.nc> <csr.nc> <jpl_twsa.npz>
python scripts/analyse.py             # combine layers, run validation tests
python scripts/maps_gb.py && python scripts/maps_s2.py
```

The GRACE inputs are public downloads: UT-CSR RL06.3 mascons (download.csr.utexas.edu/outgoing/grace/RL0603_mascons/) and GFZ GravIS (isdc-data.gfz.de/grace/GravIS/GFZ/Level-3/TWS/). The Earth Pro capture scripts (`scripts/earth/`) drive a local Google Earth Pro on macOS through a KML NetworkLink and need small helper binaries (window id, mouse, OCR) that are not included.

## Limits

River flow was not measured, so effects on Indus flow are inferred. Ice volume and "peak water" timing were not modelled. At GB's size GRACE cannot close the glacier mass budget; this is reported as a failed test. RGI outlines are a 1997–2002 historical snapshot.

## Licence

Code (`scripts/`): MIT. Report text, figures and computed data by RegenX.eco: CC BY 4.0, with credit to "RegenX.eco Geospatial Computational Model, Mr. Dinar Wali". Third-party imagery and data remain under their providers' terms (Google Earth imagery providers, Copernicus, NASA, ECMWF, GLIMS, GFZ, UT-CSR).
