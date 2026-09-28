# Groundwater Feature Engineering Summary

## 1. Groundwater CSV → Final Dataset

### Raw cleaning
- Started with **394,689 rows**.
- Removed **249 exact duplicate rows**.
- Standardized State/District names.
- Parsed dates and numeric fields.

### Station × Year
- Grouped observations by monitoring location and year.
- Calculated mean, minimum, maximum, standard deviation, and observation count.
- Result: **390,667 station-year records**.

### District × Year
- Aggregated stations to district-year.
- Calculated mean, median, minimum/maximum, standard deviation, Q25/Q75, station count, and total observations.
- Result: **20,559 district-year records**.

### Temporal features
- **1994–2025** — long-term condition
- **2015–2025** — modeling period
- **2021–2025** — recent condition
- **2025** — latest condition
- **2015–2019 vs 2021–2025** — historical change

### Coverage features
- Years available
- 2015–2025 coverage ratio
- 2021–2025 coverage ratio
- 2025 availability

### Final dataset
`gw_final` contains **717 districts** with groundwater level, trend, variability, recent change, latest condition, and data-coverage features.

---

## 2. Feature-Engineering Formulae

### 1. Station-year mean

`GW_mean = (1/n) × Σ GW_i`

### 2. Station-year minimum / maximum

`GW_min = min(GW_i)`

`GW_max = max(GW_i)`

### 3. District-year mean

`GW_district,mean = (1/S) × Σ GW_station,j`

### 4. District-year median

`GW_district,median = Median(GW_station)`

### 5. District-year standard deviation

`GW_std = StdDev(GW_station)`

### 6. Quartiles

`GW_Q25 = 25th percentile`

`GW_Q75 = 75th percentile`

### 7. Temporal mean

For a period from Y1 to Y2:

`GW_period,mean = (1/N) × Σ GW_y`

Used for 1994–2025, 2015–2025, and 2021–2025.

### 8. Temporal trend

Linear regression:

`GW_y = a + bY`

where:

`Trend = b`

Trend represents the change in groundwater depth in **metres per year**.

### 9. Recent vs early change

`GW_Recent_vs_Early = GW_mean(2021–2025) − GW_mean(2015–2019)`

### 10. Coverage ratio

`Coverage_2015–2025 = YearsAvailable(2015–2025) / 11`

`Coverage_2021–2025 = YearsAvailable(2021–2025) / 5`

### 11. 2025 availability

`GW_2025_Available = 1 if 2025 data exists; otherwise 0`

---

## Trend Interpretation

Trend is measured in **metres of groundwater depth (mbgl) per year**.

- **Positive trend** → groundwater depth is increasing, meaning groundwater is deeper below ground level.
- **Negative trend** → groundwater depth is decreasing, meaning groundwater is becoming shallower.
- Trend should be interpreted together with `Years_Available`, because sparse observations can produce extreme slopes.
