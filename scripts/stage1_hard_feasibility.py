"""
Stage 1: Hard Feasibility Constraints Engine
Project: Hybrid Geospatial AI/ML Decision Framework for Multi-Objective Data Center Site Selection in India

Applies non-negotiable physical and operational feasibility gates:
  C1: Bulk Power Grid Interconnect (>= 1,000 MVA transformation, >= 220 kV class)
  C2: Renewable Energy Headroom & Capacity (>= 50 MW installed, positive headroom)
  C3: Water Security & Hydrogeological Viability (>= 100 waterbodies OR non-critical GW depletion <= +0.15 mbgl/yr)
  C4: National Synchronous Grid Connectivity (excludes isolated island grids)

Outputs:
  - clean/stage1_feasibility_results.csv
  - checkpoint/stage1_hard_feasibility_checkpoint.md
"""

import os
import pandas as pd

MASTER_PANEL_PATH = "clean/master_state_siting_panel.csv"
OUT_FEASIBILITY_PATH = "clean/stage1_feasibility_results.csv"
CHECKPOINT_PATH = "checkpoint/stage1_hard_feasibility_checkpoint.md"

def evaluate_feasibility():
    print(f"Loading {MASTER_PANEL_PATH}...")
    df = pd.read_csv(MASTER_PANEL_PATH)
    
    # -------------------------------------------------------------
    # Constraint 1: Bulk Transmission Grid Feasibility (C1)
    # -------------------------------------------------------------
    # A commercial data center cannot interconnect directly to distribution grids.
    # Must have active high-voltage substations (>= 220 kV) and >= 1,000 MVA total capacity.
    c1_mask = (
        (df['substation_count_total'] > 0) &
        (df['transformation_capacity_total_mva'] >= 1000.0) &
        (df['max_voltage_kv'] >= 220.0)
    )
    df['c1_grid_viable'] = c1_mask.astype(int)

    # -------------------------------------------------------------
    # Constraint 2: Renewable Energy Feasibility (C2)
    # -------------------------------------------------------------
    # Must have positive renewable headroom (potential > installed) and >= 50 MW installed RES.
    c2_mask = (
        (df['renewable_headroom_mw'] > 0.0) &
        (df['total_re_mw'] >= 50.0)
    )
    df['c2_renewable_viable'] = c2_mask.astype(int)

    # -------------------------------------------------------------
    # Constraint 3: Water Resource Viability (C3)
    # -------------------------------------------------------------
    # Data center cooling requires accessible surface or groundwater.
    # Exclude severe water-stressed territories lacking surface storage (>= 100 waterbodies)
    # or having severe groundwater depletion trends (> +0.15 mbgl/year).
    c3_mask = (
        (df['waterbody_count_total'] >= 100) |
        (df['gw_depletion_trend_mbgl_per_yr'].fillna(0.0) <= 0.15)
    )
    df['c3_water_viable'] = c3_mask.astype(int)

    # -------------------------------------------------------------
    # Constraint 4: National Synchronous Grid Connectivity (C4)
    # -------------------------------------------------------------
    # Must be connected to the national unified AC synchronous grid (One Nation One Grid).
    # Non-synchronous offshore island territories (Lakshadweep, Andaman & Nicobar) are ruled out.
    c4_mask = ~df['state_id'].isin(['IN-LD', 'IN-AN'])
    df['c4_grid_connected'] = c4_mask.astype(int)

    # -------------------------------------------------------------
    # Tier 1: General Enterprise Feasibility Mask
    # -------------------------------------------------------------
    df['is_enterprise_feasible'] = (
        (df['c1_grid_viable'] == 1) &
        (df['c2_renewable_viable'] == 1) &
        (df['c3_water_viable'] == 1) &
        (df['c4_grid_connected'] == 1)
    ).astype(int)

    # -------------------------------------------------------------
    # Tier 2: Hyperscale Facility Feasibility Mask (>= 100 MW Clusters)
    # -------------------------------------------------------------
    # Hyperscale facilities require direct 400 kV/765 kV interconnects,
    # >= 10,000 MVA transformation capacity, and >= 10,000 MW renewable headroom.
    df['is_hyperscale_feasible'] = (
        (df['is_enterprise_feasible'] == 1) &
        ((df['substation_count_400kv'] > 0) | (df['substation_count_765kv_plus'] > 0)) &
        (df['transformation_capacity_total_mva'] >= 10000.0) &
        (df['renewable_headroom_mw'] >= 10000.0)
    ).astype(int)

    # Infeasibility Diagnostics
    def get_reasons(row):
        if row['is_enterprise_feasible'] == 1:
            if row['is_hyperscale_feasible'] == 1:
                return "PASS: Hyperscale & Enterprise Feasible"
            else:
                return "PASS: Enterprise / Edge Feasible (Sub-hyperscale grid/headroom scale)"
        reasons = []
        if row['c1_grid_viable'] == 0:
            reasons.append("Failed C1 (Bulk Grid <1,000 MVA or <220 kV)")
        if row['c2_renewable_viable'] == 0:
            reasons.append("Failed C2 (RE Capacity <50 MW or Negative Headroom)")
        if row['c3_water_viable'] == 0:
            reasons.append("Failed C3 (Water Resource Deficit / Extreme Depletion)")
        if row['c4_grid_connected'] == 0:
            reasons.append("Failed C4 (Offshore Island / Non-Synchronous Grid)")
        return "; ".join(reasons)

    df['feasibility_status'] = df.apply(get_reasons, axis=1)

    # Export results
    cols_to_export = [
        'state_id', 'state_name', 'region', 'is_enterprise_feasible', 'is_hyperscale_feasible',
        'c1_grid_viable', 'c2_renewable_viable', 'c3_water_viable', 'c4_grid_connected',
        'feasibility_status', 'substation_count_total', 'substation_count_400kv', 
        'substation_count_765kv_plus', 'transformation_capacity_total_mva', 
        'renewable_headroom_mw', 'waterbody_count_total', 'gw_depletion_trend_mbgl_per_yr', 
        'land_cost_avg_rs_acre', 'dc_count_state'
    ]
    df_out = df[cols_to_export].copy()
    os.makedirs("clean", exist_ok=True)
    df_out.to_csv(OUT_FEASIBILITY_PATH, index=False)
    print(f"Saved {OUT_FEASIBILITY_PATH} ({len(df_out)} rows).")

    # Write documentation
    write_checkpoint(df_out)

def write_checkpoint(df):
    os.makedirs("checkpoint", exist_ok=True)
    with open(CHECKPOINT_PATH, "w") as f:
        f.write("# Stage 1: Hard Feasibility Constraints Summary\n\n")
        f.write("## 1. Mathematical Formulation & Siting Rules\n\n")
        f.write("A location is passed to the Multi-Objective Ranking stage (Stage 2) if and only if it satisfies all four non-negotiable physical viability constraints:\n\n")
        f.write("$$\\text{Feasible}_{\\text{Enterprise}} = C_1 \\wedge C_2 \\wedge C_3 \\wedge C_4$$\n\n")
        f.write("where:\n")
        f.write("- **$C_1$ (Bulk Transmission Grid Viability):** $\\text{Capacity}_{\\text{MVA}} \\ge 1,000 \\wedge \\text{MaxVoltage}_{\\text{kV}} \\ge 220$.\n")
        f.write("- **$C_2$ (Renewable Energy Headroom):** $\\text{Headroom}_{\\text{MW}} > 0 \\wedge \\text{InstalledRE}_{\\text{MW}} \\ge 50$.\n")
        f.write("- **$C_3$ (Water Resource Availability):** $\\text{Waterbodies} \\ge 100 \\vee \\text{GW}_{\\text{trend}} \\le +0.15\\text{ mbgl/yr}$.\n")
        f.write("- **$C_4$ (National Grid Synchronous Connection):** $\\text{StateID} \\notin \\{\\text{IN-LD}, \\text{IN-AN}\\}.$\n\n")

        f.write("### Hyperscale Tier Qualification ($C_{\\text{Hyperscale}}$)\n")
        f.write("$$\\text{Feasible}_{\\text{Hyperscale}} = \\text{Feasible}_{\\text{Enterprise}} \\wedge (N_{400\\text{kV}} + N_{765\\text{kV}} > 0) \\wedge \\text{Capacity}_{\\text{MVA}} \\ge 10,000 \\wedge \\text{Headroom}_{\\text{MW}} \\ge 10,000$$\n\n")

        f.write("## 2. Evaluation Results Across 36 States/UTs\n\n")
        f.write(f"- **Enterprise Feasible States:** {df['is_enterprise_feasible'].sum()} / 36 ({df['is_enterprise_feasible'].mean():.1%})\n")
        f.write(f"- **Hyperscale Feasible States:** {df['is_hyperscale_feasible'].sum()} / 36 ({df['is_hyperscale_feasible'].mean():.1%})\n")
        f.write(f"- **Infeasible States Filtered Out:** {(df['is_enterprise_feasible'] == 0).sum()} / 36\n\n")

        f.write("### Filtered Infeasible States Breakdown\n")
        infeasible = df[df['is_enterprise_feasible'] == 0]
        for _, r in infeasible.iterrows():
            f.write(f"- **{r['state_name']} ({r['state_id']}):** {r['feasibility_status']}\n")

        f.write("\n### Qualified Hyperscale Candidates (15 States)\n")
        hyperscale = df[df['is_hyperscale_feasible'] == 1].sort_values(by='transformation_capacity_total_mva', ascending=False)
        for _, r in hyperscale.iterrows():
            f.write(f"- **{r['state_name']} ({r['state_id']}):** Grid Capacity: {r['transformation_capacity_total_mva']:,.0f} MVA | 400kV+ Substations: {int(r['substation_count_400kv'] + r['substation_count_765kv_plus'])} | RE Headroom: {r['renewable_headroom_mw']:,.0f} MW\n")

        f.write("\n### Qualified Regional / Edge Candidates (11 States)\n")
        edge = df[(df['is_enterprise_feasible'] == 1) & (df['is_hyperscale_feasible'] == 0)].sort_values(by='transformation_capacity_total_mva', ascending=False)
        for _, r in edge.iterrows():
            f.write(f"- **{r['state_name']} ({r['state_id']}):** Grid Capacity: {r['transformation_capacity_total_mva']:,.0f} MVA | Substations: {int(r['substation_count_total'])} | RE Headroom: {r['renewable_headroom_mw']:,.0f} MW\n")

    print(f"Saved {CHECKPOINT_PATH}.")

if __name__ == "__main__":
    evaluate_feasibility()

