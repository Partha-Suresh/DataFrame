# Substation & Grid Infrastructure Preprocessing Summary

## 1. Raw Data & Quality Control
- **Source:** `data/Substation_Details_1789031375809.csv` (NITI Aayog ICED platform).
- **Row Count:** 2,851 raw rows -> **2,846 valid transmission substation records** (5 footer/licensing rows excluded).
- **State Resolution Coverage:** **2,846 / 2,846 (100.0%)** mapped to canonical `state_id`.
  - 2,352 matched via State Transmission Utility (UPPTCL, GETCO, MSETCL, TANTRANSCO, etc.).
  - 241 matched via Major Renewable & Grid Pooling Station hubs (Bhadla, Khavda, Fatehgarh, Vemagiri, etc.).
  - 110 matched via Indian District gazetteer lookup.
  - 143 matched via name state tags and parenthetical district matches.
- **District Resolution:** 811 substations matched directly to specific Indian districts.

## 2. Voltage & Technical Feature Engineering
- Parsed `Voltage Ratio (kV/kV)` into standardized numerical and categorical indicators:
  - **HVDC (≥500 kV):** 14 bulk transmission terminals (e.g., ±800 kV Champa-Kurukshetra, Biswanath-Agra, Raigarh-Pugalur).
  - **765 kV Class:** 136 extra-high-voltage substations (national transmission backbone).
  - **400 kV Class:** 676 high-voltage substations (primary interconnect voltage for large hyperscale data centers).
  - **220/230 kV Class:** 2,020 sub-transmission substations.
- **Transformation Capacity (`capacity_mva`):** Numeric float MVA capacity (Mean: 312.5 MVA, Max: 4,500 MVA).
- **Asset Age & Commissioning:** Converted fiscal year strings to commissioning year (`completion_year`) and computed asset age (`asset_age_years`).

## 3. Output Datasets Created
1. **`clean/fact_substation_cleaned.csv`** (2,846 rows × 19 columns):
   - Grain: One row per physical transmission substation / ICT bank.
   - Key attributes: `substation_name`, `state_id`, `state_name`, `district_name`, `voltage_class`, `high_voltage_kv`, `low_voltage_kv`, `is_hvdc`, `capacity_mva`, `completion_fy`, `asset_age_years`.
2. **`clean/fact_substation_state_features.csv`** (36 rows × 17 columns):
   - Grain: One row per canonical Indian State/UT (`dim_state`).
   - Engineered Features:
     - `substation_count_total`: Total substations in state.
     - `substation_count_765kv_plus`: High-reliability bulk transmission count.
     - `substation_count_400kv`: Direct data center transmission interconnect count.
     - `substation_count_220kv`: Regional sub-transmission interconnect count.
     - `transformation_capacity_total_mva`: Total transformation capacity.
     - `transformation_capacity_400kv_plus_mva`: Total capacity at ≥400 kV.
     - `max_voltage_kv`: Peak transmission grid voltage class available.
     - `capacity_added_last_5yr_mva`: Capacity added from 2021 to 2026.
     - `avg_substation_age_years`: Average asset age.
     - `substation_density_per_10k_km2`: Spatial grid asset density per 10,000 km².
     - `mva_per_sq_km`: Installed grid transformation capacity density.
