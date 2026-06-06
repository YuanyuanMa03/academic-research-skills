---
name: nature-crop-simple
description: >-
  A Nature-standard skill for the SIMPLE (Soil-Plant-Atmosphere Interactions for 
  Model Evaluation and Learning) crop model. Handles model setup, input preparation, 
  parameter calibration, batch simulation, result analysis, and visualization for 
  wheat, maize, rice, soybean, and other crops. Use proactively when the user asks 
  to run, calibrate, modify, or analyse the SIMPLE crop model.
---

# nature-crop-simple — SIMPLE Crop Model Skill

## Overview

SIMPLE is a process-based crop model that simulates crop growth and yield driven by weather, soil, and management inputs. This Python implementation (`core.py` + `run.py`) is derived from the original R version.

**Repository:** `https://github.com/YuanyuanMa03/a-simple-crop-model`

## Project Structure

```
a-simple-crop-model/
├── core.py              # Core simulation engine
├── run.py               # Main execution orchestrator
├── Input/               # Input configuration files
│   ├── Simulation Management.csv  # Experiment on/off and water toggle
│   ├── Treatment.csv              # Treatment × experiment definitions
│   ├── Cultivar.csv               # Cultivar genetic parameters
│   ├── Soil.csv                   # Soil physical properties
│   ├── Species parameter.csv      # Species-level physiological parameters
│   └── Irrigation.csv             # Supplemental irrigation schedules
├── Weather/             # .WTH or .csv weather files (50+ stations)
└── Output/              # Simulation results
    ├── Res_daily_all.csv          # Daily time-series output
    └── Res_summary_all.csv        # Per-treatment summary
```

---

## Core Rules

| Domain | Rule |
|--------|------|
| Data integrity | Do not fabricate input parameters, weather data, simulation outputs, or calibration results. All values must come from provided files or user specification. |
| Parameter accuracy | Species parameters (Tbase, Topt, RUE) and cultivar parameters (Tsum, HI, I50A, I50B) must be read from their source files, not guessed. |
| Calibration discipline | When calibrating, clearly distinguish between *observed* data (user-provided) and *simulated* data (model output). Report goodness-of-fit metrics. |
| Weather handling | Respect the WTH format specification (4 header lines, then DATE SRAD TMAX TMIN RAIN DEWP WIND). When converting formats, preserve all fields. |
| Output interpretation | Yield = Biomass × HI at maturity. Stress factors (F_Temp, F_Heat, F_Water) are 0–1 scalars where 1 = no stress. |
| Unit consistency | Biomass and yield in kg/ha. SRAD in MJ/m²/day. Temperature in °C. Rainfall in mm. |

---

## Workflows

### Workflow A: Run a single simulation

1. **Check the working directory** — confirm `Input/`, `Weather/`, `core.py`, and `run.py` are present.
2. **Inspect input files** — verify column names (note: `Species*` in CSVs maps to `Species.` after column rename), check `ON_Off = 1` in Simulation Management.
3. **Execute** `python run.py` — or call `simple_crop_model()` directly from `core.py`.
4. **Read output** — load `Output/Res_daily_all.csv` and `Output/Res_summary_all.csv`.
5. **Visualise** — plot daily biomass accumulation, yield progression, or stress factor time series.

### Workflow B: Parameter calibration (GLUE / manual)

1. **Load observed data** — the user provides observed yield, biomass, phenology, or time-series data.
2. **Select calibration target** — typically yield (primary), biomass (secondary), or phenology dates.
3. **Set parameter bounds** — read the current species/cultivar values as baseline. Common calibration parameters:
   - Species: `RUE`, `Topt`, `S_Water`, `CO2_RUE`
   - Cultivar: `Tsum`, `HI`, `I50A`, `I50B`
4. **Run GLUE** — Monte Carlo sampling (e.g., 10,000 runs) with the SIMPLE model, compute Nash–Sutcliffe Efficiency (NSE) or RMSE against observed data.
5. **Select best parameter sets** — top 5–10% by NSE. Report mean ± SD of posterior parameters.
6. **Validate** — run best parameter set(s) against independent observations. Report validation RMSE.

### Workflow C: Batch sensitivity analysis

1. **Define perturbation range** — vary one parameter at a time (e.g., `Tbase` ± 20%, `RUE` ± 30%).
2. **Run model** for each parameter value while holding others constant.
3. **Compute sensitivity index** — `(ΔYield / Yield_base) / (ΔParam / Param_base)`.
4. **Rank parameters** by sensitivity. Report the top-3 most influential parameters.

### Workflow D: Multi-treatment comparison

1. **Identify treatment groups** — by `Exp`, `Treatment`, `Cultivar`, CO2 level, or irrigation regime.
2. **Extract summary data** — final yield, biomass, duration, and mean stress factors for each treatment.
3. **Statistical comparison** — compute mean ± SD per group, optionally run t-test or ANOVA.
4. **Visualise** — grouped bar plot (yield by treatment × CO2 level), or yield vs. water stress scatter.

### Workflow E: Modify model code

1. **Read `core.py`** to understand the current implementation before proposing changes.
2. **Identify the target function** — e.g., `temperature_response()`, `water_response()`, `calculate_daily_biomass()`.
3. **Implement changes** with clear comments explaining the modification.
4. **Test** — run against at least 3 treatments spanning different crops and compare to original output.

---

## Functions Reference

All core functions are in `core.py`:

| Function | Signature | Purpose |
|----------|-----------|---------|
| `doy_to_date(date_str)` | `(str) → datetime` | Convert 5-digit DOY format (YYDDD) to Python date |
| `read_weather(weather_name, irrigation)` | `(str, DataFrame|None) → DataFrame` | Read .WTH or .csv weather file, add irrigation to rainfall |
| `calculate_dtt(tmean, tbase)` | `(float, float) → float` | Daily thermal time: max(Tmean − Tbase, 0) |
| `calculate_daily_biomass(f_solar, srad, f_co2, f_temp, f_water, f_heat, rue)` | `(float...) → float` | Daily biomass: 10 × RUE × fSolar × SRAD × F_CO2 × F_Temp × min(F_Water, F_Heat) |
| `temperature_response(tmean, tbase, topt)` | `(float, float, float) → float` | Temperature stress factor |
| `co2_response(co2, co2_rue)` | `(float, float) → float` | CO₂ fertilisation factor |
| `water_response(arid, s_water)` | `(float, float) → float` | Water stress factor from ARID index |
| `heat_response(tmax, max_t, extreme_t)` | `(float, float, float) → float` | Heat stress factor |
| `priestley_taylor_pet(albedo, srad, tmax, tmin, xhlai)` | `(float...) → float` | Priestley-Taylor potential evapotranspiration |
| `calculate_arid(weather, soil_params, lat, elev)` | `(DataFrame, dict, float, float) → DataFrame` | ARID drought index and ETO |
| `simple_crop_model(para, weather, arid_data)` | `(dict, DataFrame, DataFrame) → DataFrame` | Main simulation engine |

### Parameter dictionary (`para`) structure

```python
para = {
    "Species": {
        "Tbase": float,    # Base temperature (°C)
        "Topt": float,     # Optimal temperature (°C)
        "RUE": float,      # Radiation use efficiency (g/MJ)
        "I50maxH": float,  # Max heat-induced I50B change
        "I50maxW": float,  # Max water-induced I50B change
        "MaxT": float,     # Heat stress onset temperature (°C)
        "ExtremeT": float, # Heat stress lethal temperature (°C)
        "S_Water": float,  # Water stress sensitivity
        "CO2_RUE": float   # CO₂ fertilisation coefficient
    },
    "Cultivar": {
        "Tsum": float,     # Thermal time to maturity (GDD)
        "HI": float,       # Harvest index
        "I50A": float,     # Logistic midpoint for canopy rise
        "I50B": float      # Logistic midpoint for senescence
    },
    "treatment": {
        "CO2": float,           # Atmospheric CO₂ concentration (ppm)
        "SowingDate": datetime, # Sowing date
        "HarvestDate": datetime_or_None,
        "MaxIntercept": float,  # Maximum light interception (default 0.95)
        "Water": bool,          # Enable water stress?
        "InitialBio": float,    # Initial biomass (kg/ha)
        "InitialTT": float,     # Initial thermal time (GDD)
        "InitialFsolar": float  # Initial light interception fraction
    }
}
```

---

## Input File Specifications

### `Species parameter.csv`

| Column | Unit | Description |
|--------|------|-------------|
| Species* | — | Crop species name |
| Tbase | °C | Base temperature for growth |
| Topt | °C | Optimal temperature |
| RUE | g/MJ | Radiation use efficiency |
| I50maxH | — | Max I50B adjustment under heat stress |
| I50maxW | — | Max I50B adjustment under water stress |
| MaxT | °C | Heat stress threshold |
| ExtremeT | °C | Lethal temperature |
| CO2_RUE | — | CO₂ response rate |
| S_Water | — | Water stress slope |

### `Cultivar.csv`

| Column | Unit | Description |
|--------|------|-------------|
| Species. | — | Crop species |
| Cultivar. | — | Cultivar name |
| Tsum | GDD | Total thermal requirement to maturity |
| HI | — | Harvest index (yield/biomass ratio) |
| I50A | GDD | Logistic midpoint for canopy development |
| I50B | GDD | Logistic midpoint for canopy senescence |

### Output columns (`Res_daily_all.csv`)

| Column | Unit | Description |
|--------|------|-------------|
| Day | — | Day number from sowing |
| DATE | date | Calendar date |
| Tmax / Tmin | °C | Max/min temperature |
| Radiation | MJ/m² | Solar radiation |
| TT | GDD | Cumulative thermal time |
| fSolar | — | Fraction of intercepted radiation |
| Biomass | kg/ha | Above-ground biomass |
| dBiomass | kg/ha/day | Daily biomass increment |
| HI | — | Harvest index |
| Yield | kg/ha | Predicted yield (Biomass × HI) |
| F_Temp | 0–1 | Temperature stress factor |
| F_Heat | 0–1 | Heat stress factor |
| F_Water | 0–1 | Water stress factor |
| ARID | — | Aridity index |
| ETO | mm | Reference evapotranspiration |
| MaturityDay | — | Day of maturity |

---

## Example Workflow (Python)

```python
import pandas as pd
from core import simple_crop_model, read_weather, calculate_arid, doy_to_date

# 1. Load input files
treatment = pd.read_csv("Input/Treatment.csv")
cultivar = pd.read_csv("Input/Cultivar.csv")

# 2. Select one treatment (e.g., row 0)
treat = treatment.iloc[0]

# 3. Prepare parameter dict
para = {
    "Species": {k: treat[k] for k in ["Tbase","Topt","RUE","I50maxH","I50maxW",
                                       "MaxT","ExtremeT","S_Water","CO2_RUE"]},
    "Cultivar": {
        "Tsum": cultivar.loc[0, "Tsum"],
        "HI": cultivar.loc[0, "HI"],
        "I50A": cultivar.loc[0, "I50A"],
        "I50B": cultivar.loc[0, "I50B"]
    },
    "treatment": {
        "CO2": treat["CO2"],
        "SowingDate": doy_to_date(treat["SowingDate"]),
        "Water": True,
        "MaxIntercept": 0.95,
        "InitialBio": 0,
        "InitialTT": 0,
        "InitialFsolar": 0.001
    }
}

# 4. Read weather
weather = read_weather(f"./Weather/{treat['weather']}")

# 5. Calculate ARID
soil_params = {"AWC": 0.12, "DDC": 0.3, "RCN": 70, "RZD": 800, "WUC": 0.096}
arid_data = calculate_arid(weather, soil_params, lat=33.069, elev=361)

# 6. Run model
result = simple_crop_model(para, weather, arid_data)

# 7. Print final yield
print(f"Final yield: {result['Yield'].iloc[-1]:.0f} kg/ha")
```

---

## Output Interpretation Guide

### Yield diagnostics

- If `Yield = 0`: check maturity was reached (`MaturityDay` > 1). If not, check thermal time accumulation (Tsum too high? Tbase too low?).
- If `Yield` is much lower than expected: examine stress factors. `F_Water` near 0 indicates severe drought; `F_Heat` near 0 indicates heat stress.
- If `Biomass` is low but stress factors are ~1: check RUE, SRAD values, or fSolar dynamics.

### Stress diagnosis

| Symptom | Likely cause | Check |
|---------|-------------|-------|
| F_Water < 0.3 throughout | Drought or high S_Water | ARID index, rainfall, soil AWC |
| F_Heat drops suddenly | Heat wave (Tmax > MaxT) | Temperature time series |
| F_Temp < 1 throughout | Tmean below Topt growth range | Tbase, Topt settings |
| Premature senescence | I50B reached early | I50B dynamics, stress on I50B |
| Biomass accumulates but HI low | Late stress during grain filling | Check stress post-anthesis |

---

## Calibration Guidelines

### Recommended parameters to calibrate (by priority)

1. **Cultivar parameters** (first): `Tsum`, `HI`, `I50A`, `I50B`
2. **Species parameters** (second): `RUE`, `S_Water`
3. **CO₂ response** (if CO₂ experiments): `CO2_RUE`

### Goodness-of-fit metrics

| Metric | Formula | Target |
|--------|---------|--------|
| RMSE | sqrt(mean((obs − sim)²)) | < 15% of mean observed |
| NRMSE | RMSE / mean(obs) × 100 | < 20% |
| NSE | 1 − Σ(obs−sim)² / Σ(obs−mean(obs))² | > 0.5 (acceptable), > 0.7 (good) |
| d-index | 1 − Σ(obs−sim)² / Σ(|sim−mean(obs)|+|obs−mean(obs)|)² | > 0.7 |

### Reporting format

```
Calibration result:
  NSE = 0.78  |  RMSE = 452 kg/ha (12.3%)  |  d = 0.91
  Calibrated: Tsum 2550→2680, HI 0.36→0.34, RUE 1.24→1.30
  Validation (independent): NSE = 0.65, RMSE = 589 kg/ha
```

---

## Visualisation Templates

### Daily time series
```python
import matplotlib.pyplot as plt
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
axes[0].plot(result["Day"], result["Biomass"], label="Biomass")
axes[0].plot(result["Day"], result["Yield"], label="Yield")
axes[0].set_ylabel("kg/ha")
axes[1].plot(result["Day"], result["F_Water"], label="Water stress")
axes[1].plot(result["Day"], result["F_Heat"], label="Heat stress")
axes[1].plot(result["Day"], result["F_Temp"], label="Temp stress")
axes[1].set_ylabel("Stress (0–1)")
axes[2].plot(result["Day"], result["fSolar"], label="fSolar")
axes[2].set_ylabel("Interception")
axes[2].set_xlabel("Day from sowing")
for ax in axes: ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
```

### Multi-treatment bar plot
```python
summary = pd.read_csv("Output/Res_summary_all.csv")
pivot = summary.pivot_table(index="Exp", columns="Trt", values="Yield", aggfunc="mean")
pivot.plot(kind="bar", figsize=(8, 5))
plt.ylabel("Yield (kg/ha)")
plt.grid(axis="y", alpha=0.3)
```
