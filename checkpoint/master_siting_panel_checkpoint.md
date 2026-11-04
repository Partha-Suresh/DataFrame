# Master State-Level Analytical Siting Panel Summary

## 1. Overview & Dimensions
- **Grain:** One row per canonical Indian State/UT (`state_id`).
- **Dimensions:** 36 states/UTs × 60 engineered features.
- **Coverage:** 100% of India's 36 States/UTs represented.

## 2. Integrated Feature Domains

### A. Power Grid Intelligence (`fact_substation_state_features.csv`)
- `substation_count_total`: Total physical transmission substations.
- `substation_count_765kv_plus`: High-reliability bulk national grid nodes.
- `substation_count_400kv`: Direct transmission nodes for hyperscale DCs.
- `transformation_capacity_total_mva`: Total installed transformation capacity.
- `transformation_capacity_400kv_plus_mva`: Heavy transmission capacity.
- `substation_density_per_10k_km2`: Spatial grid asset density.
- `mva_per_sq_km`: MVA transformation capacity per km².
- `capacity_added_last_5yr_mva`: Grid modernization/expansion (2021–2026).

### B. Renewable Energy & Headroom (`mnre_features.csv`)
- `solar_power_mw`: Installed solar capacity.
- `wind_power_mw`: Installed wind capacity.
- `total_re_mw`: Total installed renewable energy.
- `total_re_potential_mw`: Resource potential estimate.
- `renewable_headroom_mw`: Remaining unexploited renewable potential (`potential - installed`).
- `renewable_utilization_pct`: Ratio of installed to potential capacity.
- `re_capacity_cagr_pct`: 8-year compound annual growth rate.

### C. Surface Water Availability (`fact_state_waterbodies.csv`)
- `waterbody_count_total`: Total inland waterbodies.
- `waterbody_density_per_1000_km2`: Waterbody concentration per 1,000 km².
- `large_waterbodies_count`: High-volume reservoirs (≥50 ha).
- `large_waterbody_share_pct`: Proportion of high-volume surface reservoirs.

### D. Groundwater Telemetry (CGWB 1994–2025)
- `gw_depth_mean_mbgl`: Average depth to water table in meters below ground level.
- `gw_depletion_trend_mbgl_per_yr`: Multi-decadal depletion slope (positive = falling water table).
- `gw_recent_vs_early_change_mbgl`: Shift in water table depth (2021–2025 vs 2015–2019).
- `gw_telemetry_available_flag`: 1 if covered by CGWB well network (33 states), 0 for LD, SK, LA.

### E. Industrial Land Economics (`data/statewise land cost.csv`)
- `land_cost_low_rs_acre`, `land_cost_avg_rs_acre`, `land_cost_high_rs_acre`: Benchmark circle rates.
- `land_cost_log_avg`: Log-transformed average cost for scale stabilization.
- `land_cost_high_low_spread`: Intra-state land cost variation.
- `land_cost_cagr_pct`: 5-year historical land price appreciation rate.
- `land_cost_data_present_flag`: 1 for 12 benchmark states, 0 outside.

### F. Data Center Adoption Baseline (`fact_market_datacentres.csv`)
- `dc_count_state`: Total active data centers in the state.
- `dc_market_count_state`: Number of established commercial markets.
- `has_datacenter_presence`: Binary flag (1 if active market exists).
- `is_primary_dc_hub`: Binary flag (1 if ≥10 active facilities).
