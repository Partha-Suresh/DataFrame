"""
Master State-Level Analytical Siting Panel Builder
Project: Hybrid Geospatial AI/ML Decision Framework for Data Center Site Selection in India
Integrates:
  1. Base Geography: clean/dim_state.csv
  2. Grid Intelligence: clean/fact_substation_state_features.csv
  3. Renewable Energy & Headroom: clean/mnre_features.csv
  4. Surface Water Availability: clean/fact_state_waterbodies.csv
  5. Groundwater Telemetry: clean/groundwater_features_final.csv
  6. Land Economics: data/statewise land cost.csv
  7. Data Center Presence: clean/fact_market_datacentres.csv

Outputs:
  - clean/fact_state_land_cost.csv
  - clean/master_state_siting_panel.csv (36 rows x 57 features)
  - checkpoint/master_siting_panel_checkpoint.md
"""

import os
import numpy as np
import pandas as pd

DIM_STATE_PATH = "clean/dim_state.csv"
SUBSTATION_PATH = "clean/fact_substation_state_features.csv"
MNRE_PATH = "clean/mnre_features.csv"
WATERBODIES_PATH = "clean/fact_state_waterbodies.csv"
GROUNDWATER_PATH = "clean/groundwater_features_final.csv"
LAND_COST_RAW_PATH = "data/statewise land cost.csv"
DATACENTERS_PATH = "clean/fact_market_datacentres.csv"

OUT_LAND_COST = "clean/fact_state_land_cost.csv"
OUT_MASTER_PANEL = "clean/master_state_siting_panel.csv"
CHECKPOINT_PATH = "checkpoint/master_siting_panel_checkpoint.md"

def build_master_panel():
    print("Building Master State-Level Siting Panel...")
    
    # 1. Base Geography
    dim_state = pd.read_csv(DIM_STATE_PATH)
    state_name_to_id = dict(zip(dim_state['state_name'], dim_state['state_id']))
    state_name_to_id['Orissa'] = 'IN-OR'
    state_name_to_id['Pondicherry'] = 'IN-PY'

    master = dim_state[['state_id', 'state_name', 'region', 'area_km2', 'national_share_pct']].copy()

    # 2. Grid Substation Features
    sub_feat = pd.read_csv(SUBSTATION_PATH)
    grid_cols = [c for c in sub_feat.columns if c not in ['state_id', 'state_name', 'region', 'area_km2']]
    master = master.merge(sub_feat[['state_id'] + grid_cols], on='state_id', how='left')

    # 3. Renewable Energy & Headroom Features
    mnre = pd.read_csv(MNRE_PATH)
    mnre_cols = [c for c in mnre.columns if c not in ['state_id', 'state_name']]
    master = master.merge(mnre[['state_id'] + mnre_cols], on='state_id', how='left')

    # 4. Surface Waterbodies Features
    wb = pd.read_csv(WATERBODIES_PATH)
    wb_cols = [c for c in wb.columns if c not in ['state_id', 'state_name']]
    master = master.merge(wb[['state_id'] + wb_cols], on='state_id', how='left')
    
    # Derived surface water features
    master['waterbody_density_per_1000_km2'] = (
        (master['waterbody_count_total'] / master['area_km2']) * 1000.0
    ).fillna(0.0)
    master['large_waterbodies_count'] = (
        master['waterbody_count_gte_100ha'] + master['waterbody_count_50_100ha']
    ).fillna(0.0)
    master['large_waterbody_share_pct'] = (
        (master['large_waterbodies_count'] / master['waterbody_count_total']) * 100.0
    ).fillna(0.0)

    # 5. Groundwater Telemetry (CGWB)
    gw = pd.read_csv(GROUNDWATER_PATH)
    gw['state_name_std'] = gw['State_Standard'].replace({
        'Andaman And Nicobar Islands': 'Andaman and Nicobar Islands',
        'Dadra And Nagar Haveli And Daman And Diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'Jammu And Kashmir': 'Jammu and Kashmir',
    })
    gw['state_id'] = gw['state_name_std'].map(state_name_to_id)

    gw_agg = gw.groupby('state_id').agg(
        gw_depth_mean_mbgl=('GW_2015_2025_Mean', 'mean'),
        gw_depth_median_mbgl=('GW_2015_2025_Median', 'median'),
        gw_depletion_trend_mbgl_per_yr=('GW_2015_2025_Trend', 'mean'),
        gw_recent_vs_early_change_mbgl=('GW_Recent_vs_Early_Change', 'mean'),
        gw_districts_monitored_count=('District_Standard', 'count')
    ).reset_index()

    master = master.merge(gw_agg, on='state_id', how='left')
    master['gw_telemetry_available_flag'] = master['gw_depth_mean_mbgl'].notnull().astype(int)

    # 6. Industrial Land Economics
    land_raw = pd.read_csv(LAND_COST_RAW_PATH)
    land = pd.DataFrame()
    land['state_name'] = land_raw['State']
    land['state_id'] = land['state_name'].map(state_name_to_id)
    land['land_cost_low_rs_acre'] = land_raw['Lowest (Rs/Acre)'].str.replace('₹','', regex=False).str.replace(',','', regex=False).str.strip().astype(float)
    land['land_cost_avg_rs_acre'] = land_raw['Average (Rs/Acre)'].str.replace('₹','', regex=False).str.replace(',','', regex=False).str.strip().astype(float)
    land['land_cost_high_rs_acre'] = land_raw['Highest (Rs/Acre)'].str.replace('₹','', regex=False).str.replace(',','', regex=False).str.strip().astype(float)
    land['land_cost_cagr_pct'] = land_raw['5-Year CAGR'].str.replace('%','', regex=False).str.strip().astype(float)
    land['land_cost_log_avg'] = np.log1p(land['land_cost_avg_rs_acre'])
    land['land_cost_high_low_spread'] = land['land_cost_high_rs_acre'] - land['land_cost_low_rs_acre']

    # Save cleaned land cost dataset
    land.to_csv(OUT_LAND_COST, index=False)
    print(f"Saved {OUT_LAND_COST} ({len(land)} rows).")

    master = master.merge(
        land[['state_id', 'land_cost_low_rs_acre', 'land_cost_avg_rs_acre', 'land_cost_high_rs_acre',
              'land_cost_log_avg', 'land_cost_high_low_spread', 'land_cost_cagr_pct']],
        on='state_id', how='left'
    )
    master['land_cost_data_present_flag'] = master['land_cost_avg_rs_acre'].notnull().astype(int)

    # 7. Data Center Landscape
    dc = pd.read_csv(DATACENTERS_PATH)
    dc_agg = dc.groupby('state_id').agg(
        dc_count_state=('data_center_count', 'sum'),
        dc_market_count_state=('market', 'count')
    ).reset_index()

    master = master.merge(dc_agg, on='state_id', how='left')
    master['dc_count_state'] = master['dc_count_state'].fillna(0).astype(int)
    master['dc_market_count_state'] = master['dc_market_count_state'].fillna(0).astype(int)
    master['has_datacenter_presence'] = (master['dc_count_state'] > 0).astype(int)
    master['is_primary_dc_hub'] = (master['dc_count_state'] >= 10).astype(int)

    # Export master panel
    master.to_csv(OUT_MASTER_PANEL, index=False)
    print(f"Saved {OUT_MASTER_PANEL} ({len(master)} rows x {len(master.columns)} cols).")

    # Document checkpoint
    write_checkpoint(master)

def write_checkpoint(master):
    with open(CHECKPOINT_PATH, "w") as f:
        f.write("# Master State-Level Analytical Siting Panel Summary\n\n")
        f.write("## 1. Overview & Dimensions\n")
        f.write(f"- **Grain:** One row per canonical Indian State/UT (`state_id`).\n")
        f.write(f"- **Dimensions:** {master.shape[0]} states/UTs × {master.shape[1]} engineered features.\n")
        f.write("- **Coverage:** 100% of India's 36 States/UTs represented.\n\n")

        f.write("## 2. Integrated Feature Domains\n\n")
        f.write("### A. Power Grid Intelligence (`fact_substation_state_features.csv`)\n")
        f.write("- `substation_count_total`: Total physical transmission substations.\n")
        f.write("- `substation_count_765kv_plus`: High-reliability bulk national grid nodes.\n")
        f.write("- `substation_count_400kv`: Direct transmission nodes for hyperscale DCs.\n")
        f.write("- `transformation_capacity_total_mva`: Total installed transformation capacity.\n")
        f.write("- `transformation_capacity_400kv_plus_mva`: Heavy transmission capacity.\n")
        f.write("- `substation_density_per_10k_km2`: Spatial grid asset density.\n")
        f.write("- `mva_per_sq_km`: MVA transformation capacity per km².\n")
        f.write("- `capacity_added_last_5yr_mva`: Grid modernization/expansion (2021–2026).\n\n")

        f.write("### B. Renewable Energy & Headroom (`mnre_features.csv`)\n")
        f.write("- `solar_power_mw`: Installed solar capacity.\n")
        f.write("- `wind_power_mw`: Installed wind capacity.\n")
        f.write("- `total_re_mw`: Total installed renewable energy.\n")
        f.write("- `total_re_potential_mw`: Resource potential estimate.\n")
        f.write("- `renewable_headroom_mw`: Remaining unexploited renewable potential (`potential - installed`).\n")
        f.write("- `renewable_utilization_pct`: Ratio of installed to potential capacity.\n")
        f.write("- `re_capacity_cagr_pct`: 8-year compound annual growth rate.\n\n")

        f.write("### C. Surface Water Availability (`fact_state_waterbodies.csv`)\n")
        f.write("- `waterbody_count_total`: Total inland waterbodies.\n")
        f.write("- `waterbody_density_per_1000_km2`: Waterbody concentration per 1,000 km².\n")
        f.write("- `large_waterbodies_count`: High-volume reservoirs (≥50 ha).\n")
        f.write("- `large_waterbody_share_pct`: Proportion of high-volume surface reservoirs.\n\n")

        f.write("### D. Groundwater Telemetry (CGWB 1994–2025)\n")
        f.write("- `gw_depth_mean_mbgl`: Average depth to water table in meters below ground level.\n")
        f.write("- `gw_depletion_trend_mbgl_per_yr`: Multi-decadal depletion slope (positive = falling water table).\n")
        f.write("- `gw_recent_vs_early_change_mbgl`: Shift in water table depth (2021–2025 vs 2015–2019).\n")
        f.write("- `gw_telemetry_available_flag`: 1 if covered by CGWB well network (33 states), 0 for LD, SK, LA.\n\n")

        f.write("### E. Industrial Land Economics (`data/statewise land cost.csv`)\n")
        f.write("- `land_cost_low_rs_acre`, `land_cost_avg_rs_acre`, `land_cost_high_rs_acre`: Benchmark circle rates.\n")
        f.write("- `land_cost_log_avg`: Log-transformed average cost for scale stabilization.\n")
        f.write("- `land_cost_high_low_spread`: Intra-state land cost variation.\n")
        f.write("- `land_cost_cagr_pct`: 5-year historical land price appreciation rate.\n")
        f.write("- `land_cost_data_present_flag`: 1 for 12 benchmark states, 0 outside.\n\n")

        f.write("### F. Data Center Adoption Baseline (`fact_market_datacentres.csv`)\n")
        f.write("- `dc_count_state`: Total active data centers in the state.\n")
        f.write("- `dc_market_count_state`: Number of established commercial markets.\n")
        f.write("- `has_datacenter_presence`: Binary flag (1 if active market exists).\n")
        f.write("- `is_primary_dc_hub`: Binary flag (1 if ≥10 active facilities).\n")
    print(f"Saved {CHECKPOINT_PATH}.")

if __name__ == "__main__":
    build_master_panel()

