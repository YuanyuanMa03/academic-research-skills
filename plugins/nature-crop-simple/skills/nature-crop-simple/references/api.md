# API Reference — SIMPLE Crop Model Core Functions

## `doy_to_date(date_str)`

Convert 5-digit DOY format (YYDDD) to Python datetime object.

```python
def doy_to_date(date_str: str | int | float) -> datetime
```

- `date_str`: 5-digit string or number, e.g., `18150` or `"18150"` → 2018-05-30
- Year ≤ 20 → 2000s; Year > 20 → 1900s
- Returns: `datetime.datetime`

**Example:**
```python
>>> doy_to_date(95355)
datetime.datetime(1995, 12, 21, 0, 0)
>>> doy_to_date("07001")
datetime.datetime(2007, 1, 1, 0, 0)
```

---

## `read_weather(weather_name, irrigation=None)`

Read a .WTH or .csv weather file and optionally add irrigation to rainfall.

```python
def read_weather(
    weather_name: str,
    irrigation: pd.DataFrame | None = None
) -> pd.DataFrame
```

- `weather_name`: File path without extension (`.WTH` or `.csv` appended automatically)
- `irrigation`: DataFrame with columns `IrrDate`, `IrrAmount`; irrigations are added to `RAIN`
- Returns: DataFrame with columns `DATE` (str, YYDDD), `IDATE` (datetime), `TMAX`, `TMIN`, `SRAD`, `RAIN`

**WTH format expected:**
```
*WEATHER DATA : Station Name
@ INSI      LAT     LONG  ELEV   TAV   AMP REFHT WNDHT
  ST01  33.069   -114.53   361  21.0  11.3 -99.0 -99.0
DATE  SRAD  TMAX  TMIN  RAIN  DEWP  WIND
07001  12.6  17.0   1.0   0.0   1.8  80.0
```

- Skips 4 header lines (rows 0–3)
- If `.WTH` not found, tries `.csv`
- Returns weather data starting from row 4

---

## `calculate_dtt(tmean, tbase)`

Daily thermal time (growing degree days).

```python
def calculate_dtt(tmean: float, tbase: float) -> float
```

- Formula: `max(Tmean − Tbase, 0)`
- Returns: GDD for one day (°C·day)

---

## `calculate_daily_biomass(f_solar, srad, f_co2, f_temp, f_water, f_heat, rue)`

Daily biomass increment.

```python
def calculate_daily_biomass(
    f_solar: float,
    srad: float,
    f_co2: float,
    f_temp: float,
    f_water: float,
    f_heat: float,
    rue: float
) -> float
```

- Formula: `10 × RUE × fSolar × SRAD × F_CO2 × F_Temp × min(F_Water, F_Heat)`
- Returns: daily biomass increment (kg/ha/day)

---

## `temperature_response(tmean, tbase, topt)`

Temperature stress factor.

```python
def temperature_response(tmean: float, tbase: float, topt: float) -> float
```

- If `Tmean >= Topt`: returns 1.0 (no stress)
- Otherwise: `max((Tmean − Tbase) / (Topt − Tbase), 0)`
- Returns: 0 (full stress) to 1 (no stress)

---

## `co2_response(co2, co2_rue)`

CO₂ fertilisation factor.

```python
def co2_response(co2: float, co2_rue: float) -> float
```

- If `CO2 >= 700`: `1 + CO2_RUE × 350 / 100`
- Otherwise: `max(CO2_RUE × CO2 × 0.01 + 1 − 0.01 × 350 × CO2_RUE, 1)`
- Returns: ≥ 1.0 (no reduction)

---

## `water_response(arid, s_water)`

Water stress factor from ARID index.

```python
def water_response(arid: float, s_water: float) -> float
```

- Formula: `max(0, 1 − S_Water × ARID)`
- Returns: 0 (full drought stress) to 1 (no water stress)

---

## `heat_response(tmax, max_t, extreme_t)`

Heat stress factor.

```python
def heat_response(tmax: float, max_t: float, extreme_t: float) -> float
```

- If `Tmax <= MaxT`: 1.0 (no stress)
- If `Tmax > ExtremeT`: 0.0 (complete stress)
- Otherwise: `max(1 − (Tmax − MaxT) / (ExtremeT − MaxT), 0)`
- Returns: 0 (full heat stress) to 1 (no heat stress)

---

## `priestley_taylor_pet(albedo, srad, tmax, tmin, xhlai)`

Priestley-Taylor potential evapotranspiration.

```python
def priestley_taylor_pet(
    albedo: float,
    srad: float,
    tmax: float,
    tmin: float,
    xhlai: float
) -> float
```

- Calculates albedo as function of LAI if `xhlai > 0`
- Reference: Priestley & Taylor (1972)
- Returns: ET₀ (mm/day), minimum 0.0001

---

## `calculate_arid(weather, soil_params, lat, elev)`

Calculate ARID drought index and reference evapotranspiration.

```python
def calculate_arid(
    weather: pd.DataFrame,
    soil_params: dict,
    lat: float,
    elev: float
) -> pd.DataFrame
```

- `weather`: Must contain `SRAD`, `TMAX`, `TMIN`, `RAIN`, `DATE` (YYDDD), `IDATE` (datetime)
- `soil_params`: `{"AWC": float, "DDC": float, "RCN": float, "RZD": float, "WUC": float}`
  - AWC = available water capacity (fraction)
  - DDC = drainage coefficient
  - RCN = runoff curve number
  - RZD = root zone depth (mm)
  - WUC = water use coefficient (default 0.096)
- `lat`: Latitude (decimal degrees)
- `elev`: Elevation (m)
- Returns: DataFrame with `DATE`, `ARID` (0–1), `ETO` (mm/day)

---

## `simple_crop_model(para, weather, arid_data)`

Main simulation engine.

```python
def simple_crop_model(
    para: dict,
    weather: pd.DataFrame,
    arid_data: pd.DataFrame
) -> pd.DataFrame
```

- `para`: Parameter dictionary (see SKILL.md for full schema)
- `weather`: Weather data from sowing date forward
- `arid_data`: ARID/ETO data (must match weather length)
- Returns: DataFrame with columns:
  `Day`, `DATE`, `ETO`, `TT`, `Biomass`, `Tmax`, `Tmin`, `Radiation`, `HI`,
  `ARID`, `F_Water`, `dETO`, `F_Heat`, `Tmean`, `F_Temp`, `F_CO2`, `dTT`,
  `Yield`, `I50A`, `I50B`, `fSolar_water`, `fSolar`, `dBiomass`, `MaturityDay`

**Simulation logic:**

1. Canopy development via double-logistic curve of fSolar vs. thermal time
2. Stress-modified I50B (senescence accelerates under stress)
3. Premature senescence check (stop if fSolar drops below 0.005 + 1e-6)
4. Maturity = min(thermal time reached Tsum, senescence day)
5. Biomass = Σ daily increments
6. Yield = Biomass × HI

**Key outputs at maturity:**
- `result["Biomass"].iloc[-1]` — final above-ground biomass (kg/ha)
- `result["Yield"].iloc[-1]` — final yield (kg/ha)
- `result["MaturityDay"].iloc[0]` — day of maturity
