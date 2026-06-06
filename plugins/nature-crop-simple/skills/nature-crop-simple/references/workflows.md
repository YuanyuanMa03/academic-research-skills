# Workflow Scripts — SIMPLE Crop Model

## Workflow 1: Run a single treatment from the command line

```bash
cd /path/to/a-simple-crop-model
python run.py
```

To run programmatically:

```python
import os, pandas as pd
from core import simple_crop_model, read_weather, calculate_arid, doy_to_date

os.chdir("/path/to/a-simple-crop-model")
treatment = pd.read_csv("Input/Treatment.csv")
cultivar = pd.read_csv("Input/Cultivar.csv")

# Pick one treatment
treat = treatment.iloc[0]

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
        "InitialFsolar": 0.001
    }
}

weather = read_weather(f"./Weather/{treat['weather']}")
soil_params = {"AWC": 0.12, "DDC": 0.3, "RCN": 70, "RZD": 800, "WUC": 0.096}
lat, elev = 33.069, 361  # from WTH header
arid_data = calculate_arid(weather, soil_params, lat, elev)
result = simple_crop_model(para, weather, arid_data)

print(f"Yield: {result['Yield'].iloc[-1]:.0f} kg/ha")
```

---

## Workflow 2: GLUE parameter calibration

```python
import numpy as np
import pandas as pd
from core import simple_crop_model, read_weather, calculate_arid, doy_to_date

# ============================================
# USER INPUT: observed data
# ============================================
observed_yield = 6500  # kg/ha
treatment_idx = 0      # which treatment row to use
n_samples = 5000       # Monte Carlo iterations

# ============================================
# Load base data
# ============================================
treatment = pd.read_csv("Input/Treatment.csv")
cultivar = pd.read_csv("Input/Cultivar.csv")
treat = treatment.iloc[treatment_idx]
cult = cultivar[(cultivar["Species."] == treat["Species."]) &
                (cultivar["Cultivar."] == treat["Cultivar"])].iloc[0]

# ============================================
# Define parameter bounds
# ============================================
param_bounds = {
    "Tsum":  (cult["Tsum"] * 0.85, cult["Tsum"] * 1.15),
    "HI":    (cult["HI"] * 0.80,   cult["HI"] * 1.20),
    "I50A":  (cult["I50A"] * 0.70, cult["I50A"] * 1.30),
    "I50B":  (cult["I50B"] * 0.50, cult["I50B"] * 1.50),
    "RUE":   (treat["RUE"] * 0.80, treat["RUE"] * 1.20),
    "S_Water": (treat["S_Water"] * 0.50, treat["S_Water"] * 1.50),
}

# ============================================
# Monte Carlo sampling
# ============================================
weather = read_weather(f"./Weather/{treat['weather']}")
sowing_date = doy_to_date(treat["SowingDate"])
sow_idx = weather[weather["IDATE"] == sowing_date].index[0]
weather_sow = weather.iloc[sow_idx:].copy().reset_index(drop=True)
soil_params = {"AWC": 0.12, "DDC": 0.3, "RCN": 70, "RZD": 800, "WUC": 0.096}
arid_data = calculate_arid(weather_sow, soil_params, lat=33.069, elev=361)

results = []
for i in range(n_samples):
    params = {k: np.random.uniform(v[0], v[1]) for k, v in param_bounds.items()}

    para = {
        "Species": {k: treat[k] for k in ["Tbase","Topt","I50maxH","I50maxW",
                                           "MaxT","ExtremeT","CO2_RUE"]},
        "Cultivar": {
            "Tsum": params["Tsum"],
            "HI": params["HI"],
            "I50A": params["I50A"],
            "I50B": params["I50B"]
        },
        "treatment": {
            "CO2": treat["CO2"],
            "SowingDate": sowing_date,
            "Water": True,
            "MaxIntercept": 0.95,
            "InitialFsolar": 0.001
        }
    }
    para["Species"]["RUE"] = params["RUE"]
    para["Species"]["S_Water"] = params["S_Water"]

    try:
        sim = simple_crop_model(para, weather_sow, arid_data)
        sim_yield = sim["Yield"].iloc[-1] if len(sim) > 0 else 0
    except:
        sim_yield = 0

    rmse = np.sqrt((sim_yield - observed_yield) ** 2)
    nse = 1 - (observed_yield - sim_yield) ** 2 / (observed_yield - np.mean([observed_yield])) ** 2 \
          if observed_yield != 0 else -999

    results.append({**params, "Yield": sim_yield, "RMSE": rmse, "NSE": nse})

# ============================================
# Select best parameter sets
# ============================================
results_df = pd.DataFrame(results)
results_df = results_df[results_df["Yield"] > 0]  # filter failed runs
best = results_df.nsmallest(int(n_samples * 0.05), "RMSE")

print("=== GLUE Calibration Result ===")
print(f"Top 5% (n={len(best)}) parameter sets:")
for col in ["Tsum", "HI", "I50A", "I50B", "RUE", "S_Water"]:
    print(f"  {col}: {best[col].mean():.2f} ± {best[col].std():.2f}  "
          f"[{best[col].min():.2f} – {best[col].max():.2f}]")
print(f"  Yield: {best['Yield'].mean():.0f} ± {best['Yield'].std():.0f} kg/ha")
print(f"  NSE:   {best['NSE'].mean():.2f}")

# Save best set
best.iloc[0].to_dict()
```

---

## Workflow 3: Sensitivity analysis

```python
import numpy as np
import pandas as pd
from core import simple_crop_model, read_weather, calculate_arid, doy_to_date

treatment = pd.read_csv("Input/Treatment.csv")
cultivar = pd.read_csv("Input/Cultivar.csv")
treat = treatment.iloc[0]

# Base simulation
weather = read_weather(f"./Weather/{treat['weather']}")
sowing_date = doy_to_date(treat["SowingDate"])
sow_idx = weather[weather["IDATE"] == sowing_date].index[0]
weather_sow = weather.iloc[sow_idx:].copy().reset_index(drop=True)
soil_params = {"AWC": 0.12, "DDC": 0.3, "RCN": 70, "RZD": 800, "WUC": 0.096}
arid_data = calculate_arid(weather_sow, soil_params, lat=33.069, elev=361)

def run_model(**overrides):
    cult = cultivar.iloc[0]
    para = {
        "Species": {k: treat[k] for k in ["Tbase","Topt","I50maxH","I50maxW",
                                           "MaxT","ExtremeT","CO2_RUE"]},
        "Cultivar": {
            "Tsum": cult["Tsum"], "HI": cult["HI"],
            "I50A": cult["I50A"], "I50B": cult["I50B"]
        },
        "treatment": {
            "CO2": treat["CO2"], "SowingDate": sowing_date,
            "Water": True, "MaxIntercept": 0.95, "InitialFsolar": 0.001
        }
    }
    para["Species"]["RUE"] = overrides.get("RUE", treat["RUE"])
    para["Species"]["S_Water"] = overrides.get("S_Water", treat["S_Water"])
    for k, v in overrides.items():
        if k in para["Cultivar"]:
            para["Cultivar"][k] = v
    sim = simple_crop_model(para, weather_sow, arid_data)
    return sim["Yield"].iloc[-1]

base_yield = run_model()
print(f"Base yield: {base_yield:.0f} kg/ha")

parameters = {
    "Tsum": cultivar.iloc[0]["Tsum"],
    "HI": cultivar.iloc[0]["HI"],
    "I50A": cultivar.iloc[0]["I50A"],
    "I50B": cultivar.iloc[0]["I50B"],
    "RUE": treat["RUE"],
    "S_Water": treat["S_Water"]
}

print("\n=== Sensitivity Analysis ===")
print(f"{'Parameter':<12} {'-20%':>10} {'-10%':>10} {'base':>10} {'+10%':>10} {'+20%':>10} {'Sensitivity':>12}")
print("-" * 76)

for pname, pbase in parameters.items():
    if pbase == 0:
        continue
    results_line = []
    deltas = [-0.2, -0.1, 0, 0.1, 0.2]
    yields = []
    for d in deltas:
        pval = pbase * (1 + d)
        y = run_model(**{pname: pval})
        yields.append(y)

    # Sensitivity = avg |ΔYield/Yield| / |ΔParam/Param|
    sens = np.mean([abs((y - base_yield) / base_yield) / abs(d))
                    for y, d in zip(yields, deltas) if d != 0])

    print(f"{pname:<12} {yields[0]:>10.0f} {yields[1]:>10.0f} {yields[2]:>10.0f} "
          f"{yields[3]:>10.0f} {yields[4]:>10.0f} {sens:>12.2f}")
```

---

## Workflow 4: Multi-treatment comparison with statistics

```python
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

summary = pd.read_csv("Output/Res_summary_all.csv")

# Group by experiment and treatment
pivot = summary.pivot_table(
    index="Exp", columns="Trt", values="Yield",
    aggfunc=["mean", "std", "count"]
)
print("=== Yield by Treatment ===")
print(pivot)

# ANOVA across treatments
groups = [g["Yield"].values for _, g in summary.groupby("Trt")]
f_stat, p_value = stats.f_oneway(*groups)
print(f"\nANOVA: F = {f_stat:.2f}, p = {p_value:.4f}")

# Visualise
fig, ax = plt.subplots(figsize=(8, 5))
summary.boxplot(column="Yield", by="Trt", ax=ax)
ax.set_ylabel("Yield (kg/ha)")
ax.set_title("Yield by Treatment")
plt.suptitle("")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("yield_by_treatment.png", dpi=150)
```

---

## Workflow 5: Visualisation — daily stress dynamics

```python
import pandas as pd
import matplotlib.pyplot as plt

daily = pd.read_csv("Output/Res_daily_all.csv")

# Filter one treatment
one_trt = daily[daily["Trt"] == 1].iloc[:120]  # first 120 days

fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

# Panel 1: Biomass and Yield
axes[0].plot(one_trt["Day"], one_trt["Biomass"], "g-", label="Biomass")
axes[0].plot(one_trt["Day"], one_trt["Yield"], "orange", label="Yield")
axes[0].set_ylabel("kg/ha")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Panel 2: Stress factors
axes[1].plot(one_trt["Day"], one_trt["F_Temp"], label="F_Temp")
axes[1].plot(one_trt["Day"], one_trt["F_Heat"], label="F_Heat")
axes[1].plot(one_trt["Day"], one_trt["F_Water"], label="F_Water")
axes[1].set_ylabel("Stress (0–1)")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Panel 3: Canopy interception
axes[2].plot(one_trt["Day"], one_trt["fSolar"], "b-", label="fSolar")
axes[2].set_ylabel("Light interception")
axes[2].legend()
axes[2].grid(True, alpha=0.3)

# Panel 4: ARID and temperature
axes[3].plot(one_trt["Day"], one_trt["ARID"], "r-", label="ARID")
ax_temp = axes[3].twinx()
ax_temp.plot(one_trt["Day"], one_trt["Tmean"], "k--", alpha=0.5, label="Tmean")
axes[3].set_ylabel("ARID")
ax_temp.set_ylabel("Tmean (°C)")
axes[3].set_xlabel("Day from sowing")
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("stress_dynamics.png", dpi=150)
print("Saved: stress_dynamics.png")
```
