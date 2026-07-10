---
name: gaia-dr3-plot-with-dust
description: Retrieve nearby Gaia DR3 stars (via the AIP TAP service) and produce a two-panel research-paper figure — RA/Dec on the left, a Galactic XY projection overlaid with the SFD all-sky dust-extinction map on the right (dustmaps package).
version: 2.0.0
author: Hermi (sorgenfresser) / AIP
license: MIT
prerequisites:
  python:
    - pyvo
    - pandas
    - pyarrow
    - matplotlib
    - seaborn
    - dustmaps
    - scipy
metadata:
  hermes:
    tags: [astronomy, gaia-dr3, dust, extinction, plotting, pyvo]
    category: astronomy
    related_skills: [gaia-dr3-tap-query, cmd-plotting, seaborn-paper-plots]
---

# Gaia DR3 — paper-style figure with dust overlay

## When to Use
Use when you want a polished, manuscript-style figure of a Gaia sample set against
the Milky Way's dust lanes. For plain Gaia queries (no dust), use `gaia-dr3-tap-query`.

> Dependencies are pre-installed in this skill's dedicated venv. Run every command
> with `{{SKILL_PYTHON}}`; never `pip install`. The SFD dust map (~167 MB) downloads
> once on first use via `dustmaps.sfd.fetch()` (needs internet); it is cached after.

## Procedure

### 1. Query Gaia DR3 (nearest stars)
```python
import warnings, os
warnings.filterwarnings("ignore")
import pyvo, pandas as pd
service = pyvo.dal.TAPService("https://gaia.aip.de/tap/")
q = """SELECT TOP 100 source_id, ra, dec, l, b, parallax, phot_g_mean_mag, bp_rp
       FROM gaiadr3.gaia_source
       WHERE parallax > 10
       ORDER BY parallax DESC"""
df = service.run_sync(q).to_table().to_pandas()
out = "gaia-dr3-dust"; os.makedirs(out, exist_ok=True)
df.to_parquet(f"{out}/gaia_dr3_closest.parquet", index=False)
```

### 2. Build the dust-extinction background (SFD)
```python
import dustmaps.sfd
dustmaps.sfd.fetch()                       # one-time download; cached afterwards
from dustmaps.sfd import SFDQuery
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
l_grid = np.linspace(0, 360, 720); b_grid = np.linspace(-90, 90, 360)
L, B = np.meshgrid(l_grid, b_grid)
ebv = SFDQuery()(SkyCoord(l=L*u.deg, b=B*u.deg, frame="galactic"))   # E(B-V), mag
```

### 3. Two-panel figure
```python
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 2, figsize=(12, 6), facecolor="white")
# Left: RA/Dec
sc = axs[0].scatter(df["ra"], df["dec"], c=df["parallax"], cmap="viridis",
                    s=60, edgecolor="black", linewidth=0.4)
axs[0].set_xlabel("RA [deg]"); axs[0].set_ylabel("Dec [deg]")
axs[0].set_title("Gaia DR3 — closest stars (RA/Dec)")
fig.colorbar(sc, ax=axs[0], label="parallax [mas]")
# Right: Galactic XY + dust
axs[1].imshow(ebv, extent=[-1.1, 1.1, -1.1, 1.1], origin="lower",
              cmap="gray_r", alpha=0.4)
lr = np.radians(df["l"].values); br = np.radians(df["b"].values)
x = np.cos(br)*np.cos(lr); y = np.cos(br)*np.sin(lr)
sc2 = axs[1].scatter(x, y, c=df["parallax"], cmap="viridis", s=70,
                     edgecolor="black", linewidth=0.5)
axs[1].scatter(0, 0, c="gold", s=300, marker="o", edgecolor="orange")
axs[1].annotate("Sun", xy=(0, 0), xytext=(0.07, 0.07), color="darkorange", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="darkorange"))
axs[1].set_xlabel("x = cos(b)·cos(l)"); axs[1].set_ylabel("y = cos(b)·sin(l)")
axs[1].set_title("Galactic XY (dust overlay)"); axs[1].set_aspect("equal")
axs[1].set_xlim(-1.1, 1.1); axs[1].set_ylim(-1.1, 1.1)
fig.colorbar(sc2, ax=axs[1], label="parallax [mas]")
plt.tight_layout(); plt.savefig(f"{out}/gaia_dr3_with_dust.png", dpi=300, bbox_inches="tight")
print(f"saved {out}/gaia_dr3_with_dust.png")
```

## Pitfalls
- The SFD map downloads once (`dustmaps.sfd.fetch()`); needs internet the first time.
- Use `TOP N` (not `LIMIT`); a parallax floor (`WHERE parallax > 10`) bounds the sort.
- 0.5° grid steps give a smooth background at modest memory; coarsen for speed.
- Save outputs under the workspace topic folder — never `/home/hermes/` or `/tmp`.

## Verification
- `{out}/gaia_dr3_closest.parquet` and `{out}/gaia_dr3_with_dust.png` exist.
- The figure shows stars colour-coded by parallax over a faint dust background.
