---
name: jubik
category: research
description: J-UBIK (JAX-accelerated Universal Bayesian Imaging Kit) + NIFTy 9.x re API for variational inference.
prerequisites:
  python:
    - "nifty[re]>=9.2.0"
    - "jubik @ git+https://github.com/NIFTy-PPL/J-UBIK"
---

# J-UBIK / NIFTy 9 `re` (JAX) API

## Prerequisites

(Declared in frontmatter — auto-provisioned via `.hermes/envs/jubik`)

## Setup

- **Creating/editing this skill via `skill_manage` auto-provisions** the venv at `.hermes/envs/jubik`.
- **Do NOT** pip-install anything manually or create a venv by hand.
- **Do NOT** edit SKILL.md via terminal commands — provisioning fires ONLY through `skill_manage create/edit`. If you need to re-provision, edit via `skill_manage`.
- All jubik/nifty work **must** use the skill venv python at `.hermes/envs/jubik/bin/python`.
- If provisioning fails, show the error — do not improvise a workaround.

## Critical facts (correct past failures)

- NIFTy v9+ ships on PyPI as **`nifty`** (currently 9.2.0).
- The **JAX API** is `nifty.re` (`import nifty.re as jft`).
- The **classic numpy API** is `nifty.cl`.
- **NEVER** install or import `nifty8` — that is the dead pre-2026 line and is incompatible with J-UBIK.
- **J-UBIK** = JAX-accelerated Universal Bayesian Imaging Kit (import name `jubik`), installed from git, requires `nifty>=9.0.0`.
- Importing `jubik` sets JAX to float64 globally.
- Chandra (CIAO/MARX) and eROSITA (eSASS) instrument tooling is **NOT** available in this environment — only the pure-Python core (and the pip-installable `[jwst]` extra) can be used here.

## API — NIFTy.re v9.2.0

> **IMPORTANT: `jft.optimize_kl` WORKS in nifty 9.2.0.** The official upstream demo (`demos/re/0_intro.py`) runs cleanly with healthy chi-squared diagnostics. When the API fights you, do NOT conclude the library is broken — curl the official demo, adapt it, and compare your usage to the upstream reference.

### Domain construction

```python
grid = jft.Grid(shape0=N, splits=1)      # 1D Cartesian grid
```

### CorrelatedFieldMaker (prior)

```python
maker = jft.CorrelatedFieldMaker('cf')   # prefix REQUIRED
```

`add_fluctuations()` arguments are **tuples** `(mean, std)`, NOT lists:

```python
maker.add_fluctuations(
    shape=(N,),                           # tuple shape
    distances=1.0/N,                      # match official demo convention
    fluctuations=(1e-1, 5e-3),            # lognormal: mean>0, std>0
    loglogavgslope=(-2.0, 1e-2),          # normal: mean, std
    flexibility=(1e0, 5e-1),
    asperity=(5e-1, 5e-2),
)
```

Lognormal prior requires **mean > 0**. Normal prior accepts any mean.

Set the amplitude offset before finalizing:

```python
cf_zm = dict(offset_mean=0.0, offset_std=(1e-3, 1e-4))
cf_fl = dict(fluctuations=(1e-1, 5e-3), loglogavgslope=(-2.0, 1e-2),
             flexibility=(1e0, 5e-1), asperity=(5e-1, 5e-2))
cfm = jft.CorrelatedFieldMaker("cf")
cfm.set_amplitude_total_offset(**cf_zm)
cfm.add_fluctuations(shape, distances, **cf_fl, prefix="ax1", non_parametric_kind="power")
cf = cfm.finalize()                      # returns a jft.Model
```

### Compound models (Signal = prior × scaling)

Compose init methods with `|` (pipe operator) to merge multiple sub-model domains:

```python
scaling = jft.LogNormalPrior(3.0, 1.0, name="scaling", shape=(1,))

class Signal(jft.Model):
    def __init__(self, correlated_field, scaling):
        self.cf = correlated_field
        self.scaling = scaling
        super().__init__(init=self.cf.init | self.scaling.init)
    def __call__(self, x):
        return self.scaling(x) * jnp.exp(self.cf(x))

signal = Signal(cf, scaling)
```

### Calling a Model (evaluating the prior)

`Model.__call__` takes a **single dict argument**, NOT `**kwargs`:

```python
# WRONG:  model(**params)
# RIGHT:
signal_val = model(params_dict)
```

### Likelihoods

```python
noise_cov = lambda x: noise_std**2 * x
noise_cov_inv = lambda x: noise_std**-2 * x
lh = jft.Gaussian(data, noise_cov_inv).amend(signal_response)
```

### Variational Inference — the official pattern

From `demos/re/0_intro.py`:

```python
from jax import random
import nifty.re as jft

n_vi_iterations = 6
delta = 1e-4
n_samples = 4

key, k_i, k_o = random.split(key, 3)
samples, state = jft.optimize_kl(
    lh,
    jft.Vector(lh.init(k_i)),             # INITIAL: wrap lh.init() in Vector
    n_total_iterations=n_vi_iterations,
    n_samples=lambda i: n_samples // 2 if i < 2 else n_samples,
    key=k_o,
    draw_linear_kwargs=dict(
        cg_name="SL",
        cg_kwargs=dict(absdelta=delta * jft.size(lh.domain) / 10.0, maxiter=100),
    ),
    nonlinearly_update_kwargs=dict(
        minimize_kwargs=dict(name="SN", xtol=delta, cg_kwargs=dict(name=None), maxiter=5)
    ),
    kl_kwargs=dict(
        minimize_kwargs=dict(name="M", xtol=delta, cg_kwargs=dict(name=None), maxiter=35)
    ),
    sample_mode="nonlinear_resample",
    odir="results",                         # optional output dir
    resume=False,
)
```

**Key API points:**
- **Initial position**: `jft.Vector(lh.init(k_i))` — use `lh.init()` (the likelihood's init, which inherits the prior), wrapped in `jft.Vector`.
- **Posterior mean**: `jft.mean(tuple(signal(s) for s in samples))` — evaluate the full model at each sample, then average.
- **Chi-squared diagnostics**: each VI iteration prints `reduced Chi²` for likelihood and all prior parameters. Healthy values are near 1.0.

### Plotting

Set `MPLCONFIGDIR` to a writable directory **before** importing matplotlib:

```python
import os
os.environ['MPLCONFIGDIR'] = '/path/to/writable/cache'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

## Troubleshooting

- **ImportError on `nifty.re`**: you may be running the wrong python (not the skill venv). Verify with `import nifty; print(nifty.__version__)`.
- **JAX out-of-memory on GPU**: set `export JAX_PLATFORMS=cpu` or reduce domain size.
- **`nifty8` present**: uninstall it. It conflicts with nifty v9.
- **Matplotlib permission error**: set `MPLCONFIGDIR` to a writable directory before importing.

## Lessons from failed approaches

1. **`optimize_kl` is NOT broken.** Early attempts failed due to API misuse (passing raw dict instead of `jft.Vector(lh.init(key))`, using `**kwargs` instead of single-dict arg, wrong `noise_std_inv` signature). Once the official demo pattern was adopted, inference completed in ~25s with χ² ≈ 1.0 and signal recovery correlation of 0.977.

2. **When the API fights you, consult the upstream demo.** The authoritative reference is `demos/re/0_intro.py` at https://gitlab.mpcdf.mpg.de/ift/nifty (raw path: `demos/re/0_intro.py`, ref: `nifty`). Adapt it verbatim wherever possible — don't guess at signatures.

3. **Frontmatter `prerequisites` are mandatory for auto-provisioning.** Putting prerequisites inside a body code-block (rather than YAML frontmatter) prevents `skill_manage` from provisioning the venv. Provisioning fires ONLY on `skill_manage create/edit`.

4. **`CorrelatedFieldMaker` requires a prefix** in `add_fluctuations()` (e.g., `prefix="ax1"`). The field names in the resulting domain are prefixed (e.g., `cfax1xi`, `cfax1spectrum`).