# Parameter Reference — SIMPLE Crop Model

## Species Parameters (Input/Species parameter.csv)

| Parameter | Unit | Typical range | Description |
|-----------|------|---------------|-------------|
| Tbase | °C | 0–10 | Base temperature below which no growth occurs |
| Topt | °C | 15–28 | Optimal temperature for growth |
| RUE | g/MJ | 0.8–2.2 | Radiation use efficiency (biomass per intercepted radiation) |
| I50maxH | — | 50–150 | Maximum increase in I50B under heat stress |
| I50maxW | — | 10–30 | Maximum increase in I50B under water stress |
| MaxT | °C | 34–38 | Heat stress threshold temperature |
| ExtremeT | °C | 40–55 | Lethal temperature (complete heat stress) |
| CO2_RUE | — | 0.01–0.10 | CO₂ fertilisation rate parameter |
| S_Water | — | 0.4–2.0 | Water stress sensitivity slope |

### Default species values

| Crop | Tbase | Topt | RUE | I50maxH | I50maxW | MaxT | ExtremeT | CO2_RUE | S_Water |
|------|-------|------|-----|---------|---------|------|----------|---------|---------|
| Wheat | 0 | 15 | 1.24 | 100 | 25 | 34 | 45 | 0.08 | 0.4 |
| Rice | 9 | 26 | 1.24 | 100 | 10 | 34 | 50 | 0.08 | 1.0 |
| Maize | 8 | 28 | 2.10 | 100 | 12 | 34 | 50 | 0.01 | 1.5 |
| Soybean | 6 | 27 | 0.86 | 120 | 20 | 36 | 50 | 0.07 | 0.9 |

---

## Cultivar Parameters (Input/Cultivar.csv)

| Parameter | Unit | Typical range | Description |
|-----------|------|---------------|-------------|
| Tsum | GDD | 1500–3000 | Total thermal time requirement from sowing to maturity |
| HI | — | 0.30–0.55 | Harvest index (yield / total biomass ratio) |
| I50A | GDD | 200–800 | Logistic midpoint for canopy development (rising phase) |
| I50B | GDD | 50–400 | Logistic midpoint for canopy senescence (declining phase) |

### Default cultivar examples

| Crop | Cultivar | Tsum | HI | I50A | I50B |
|------|----------|------|----|------|------|
| Wheat | Yecora Rojo | 2550 | 0.36 | 480 | 200 |
| Wheat | Batten | 2550 | 0.34 | 280 | 50 |
| Soybean | Bragg | 2500 | 0.35 | 680 | 300 |
| Soybean | Williams82 | 2350 | 0.40 | 600 | 200 |

---

## Soil Parameters (Input/Soil.csv)

| Parameter | Unit | Typical range | Description |
|-----------|------|---------------|-------------|
| AWC | fraction | 0.05–0.25 | Available water capacity (volumetric) |
| RCN | — | 50–85 | Runoff curve number |
| DDC | — | 0.3–0.8 | Drainage coefficient |
| RZD | mm | 400–2000 | Root zone depth |

---

## Management Parameters (Input/Treatment.csv)

| Parameter | Unit | Description |
|-----------|------|-------------|
| CO2 | ppm | Atmospheric CO₂ concentration (e.g., 350 ambient, 550 elevated) |
| SowingDate | YYDDD | Sowing date in 5-digit DOY format |
| HarvestDate | YYDDD | Optional harvest date override |
| MaxIntercept | — | Maximum fraction of light interception (default 0.95) |
| Water | bool | Enable water stress simulation |
| InitialBio | kg/ha | Initial above-ground biomass at sowing |
| InitialTT | GDD | Initial thermal time accumulation |
| InitialFsolar | — | Initial light interception fraction (default ~0.001) |

---

## Weather Data Fields

| Field | Unit | Description |
|-------|------|-------------|
| DATE | YYDDD | Date in 5-digit DOY format |
| SRAD | MJ/m²/day | Solar radiation |
| TMAX | °C | Daily maximum temperature |
| TMIN | °C | Daily minimum temperature |
| RAIN | mm | Daily rainfall (plus irrigation additions) |
| DEWP | °C | Dew point temperature (for ARID calculation) |
| WIND | km/day | Wind speed |

---

## Output Variables (Res_daily_all.csv)

| Variable | Unit | Description | Derived from |
|----------|------|-------------|-------------|
| Day | — | Day number from sowing | Sequential |
| DATE | datetime | Calendar date | doy_to_date() |
| Tmax | °C | Daily maximum temperature | Weather input |
| Tmin | °C | Daily minimum temperature | Weather input |
| Radiation | MJ/m² | Solar radiation | Weather input |
| TT | GDD | Cumulative thermal time | Σ dTT |
| fSolar | — | Fraction of intercepted radiation | Double-logistic curve |
| Biomass | kg/ha | Above-ground biomass | Σ dBiomass |
| dBiomass | kg/ha/day | Daily biomass increment | calculate_daily_biomass() |
| HI | — | Harvest index | Cultivar parameter |
| Yield | kg/ha | Predicted yield | Biomass × HI |
| F_Temp | 0–1 | Temperature stress factor | temperature_response() |
| F_Heat | 0–1 | Heat stress factor | heat_response() |
| F_Water | 0–1 | Water stress factor | water_response() |
| ARID | — | Aridity index | calculate_arid() |
| ETO | mm | Reference evapotranspiration | calculate_arid() |
| MaturityDay | — | Day of maturity determination | min(TT≥Tsum, senescence) |

---

## Stress Response Summary

### Temperature stress (F_Temp)
```
Tmean < Tbase → F_Temp = 0
Tbase ≤ Tmean < Topt → F_Temp = (Tmean − Tbase) / (Topt − Tbase)
Tmean ≥ Topt → F_Temp = 1
```

### Heat stress (F_Heat)
```
Tmax ≤ MaxT → F_Heat = 1
MaxT < Tmax ≤ ExtremeT → F_Heat = 1 − (Tmax − MaxT) / (ExtremeT − MaxT)
Tmax > ExtremeT → F_Heat = 0
```

### Water stress (F_Water)
```
F_Water = max(0, 1 − S_Water × ARID)
```

### CO₂ fertilisation (F_CO2)
```
CO₂ ≥ 700 → F_CO2 = 1 + CO2_RUE × 350 / 100
CO₂ < 700 → F_CO2 = max(CO2_RUE × CO₂ × 0.01 + 1 − 3.5 × CO2_RUE, 1)
```

### Daily biomass
```
dBiomass = 10 × RUE × fSolar × SRAD × F_CO2 × F_Temp × min(F_Water, F_Heat)
```
