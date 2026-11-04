"""
Stage 2: Multi-Objective Siting Optimization & Pareto Ranking Engine
Project: Hybrid Geospatial AI/ML Decision Framework for Multi-Objective Data Center Site Selection in India

Formulates 5 normalized objective dimensions:
  1. Power Grid Reliability & Capacity Score (S_Grid)
  2. Clean Renewable Energy & Headroom Score (S_Renewable)
  3. Water Security & Hydrogeological Sustainability Score (S_Water)
  4. Land Economics & Acquisition Affordability Score (S_Land_Affordability)
  5. Ecosystem & Market Connectivity Score (S_Ecosystem)

Calculates:
  - Strict Pareto Dominance (Non-dominated optimal candidate set)
  - TOPSIS Multi-Criteria Decision Analysis across 4 Strategic Archetypes:
      * Balanced Enterprise (Equal 20% weights)
      * Green Hyperscale (Grid 35%, RE 35%, Water 15%, Land 10%, Eco 5%)
      * Low-Cost / Sovereign Compute (Land 35%, Grid 25%, Water 20%, RE 15%, Eco 5%)
      * Market & Connectivity-First (Eco 35%, Grid 25%, Water 15%, RE 15%, Land 10%)

Outputs:
  - clean/stage2_multiobjective_ranking.csv
  - checkpoint/stage2_multiobjective_checkpoint.md
"""

import os
import numpy as np
import pandas as pd

FEASIBILITY_PATH = "clean/stage1_feasibility_results.csv"
MASTER_PANEL_PATH = "clean/master_state_siting_panel.csv"
OUT_RANKING_PATH = "clean/stage2_multiobjective_ranking.csv"
CHECKPOINT_PATH = "checkpoint/stage2_multiobjective_checkpoint.md"

def min_max(s):
    denom = s.max() - s.min()
    return (s - s.min()) / denom if denom > 0 else np.zeros(len(s))

def run_stage2_optimization():
    print("Loading Feasibility Results and Master Panel...")
    feas = pd.read_csv(FEASIBILITY_PATH)
    master = pd.read_csv(MASTER_PANEL_PATH)

    # Filter to 26 Feasible States from Stage 1
    df = master[master['state_id'].isin(feas[feas['is_enterprise_feasible'] == 1]['state_id'])].copy()
    print(f"Processing {len(df)} feasible candidate states...")

    # -------------------------------------------------------------
    # 1. Objective Dimension 1: Power Grid Capacity & Reliability
    # -------------------------------------------------------------
    # Evaluates total transformation MVA, high-voltage substations (>=400 kV), and MVA density
    grid_raw = (
        0.40 * min_max(np.log1p(df['transformation_capacity_total_mva'].fillna(0.0))) +
        0.35 * min_max(np.log1p(df['substation_count_400kv'].fillna(0.0) + df['substation_count_765kv_plus'].fillna(0.0))) +
        0.25 * min_max(np.log1p(df['mva_per_sq_km'].fillna(0.0)))
    )
    df['score_grid'] = min_max(grid_raw)

    # -------------------------------------------------------------
    # 2. Objective Dimension 2: Clean Renewable Energy & Headroom
    # -------------------------------------------------------------
    # Evaluates remaining clean headroom (MW), installed capacity (MW), and 8-year growth CAGR (%)
    cagr_clean = df['re_capacity_cagr_pct'].fillna(0.0).clip(lower=0)
    re_raw = (
        0.45 * min_max(np.log1p(df['renewable_headroom_mw'].clip(lower=0).fillna(0.0))) +
        0.35 * min_max(np.log1p(df['total_re_mw'].fillna(0.0))) +
        0.20 * min_max(cagr_clean)
    )
    df['score_renewable'] = min_max(re_raw)

    # -------------------------------------------------------------
    # 3. Objective Dimension 3: Water Security & Hydrogeological Sustainability
    # -------------------------------------------------------------
    # Evaluates surface reservoir counts and rewards stable/recharging groundwater trends
    gw_stable = (0.15 - df['gw_depletion_trend_mbgl_per_yr'].fillna(0.0)).clip(lower=0)
    water_raw = (
        0.50 * min_max(np.log1p(df['waterbody_count_total'].fillna(0.0))) +
        0.50 * min_max(gw_stable)
    )
    df['score_water'] = min_max(water_raw)

    # -------------------------------------------------------------
    # 4. Objective Dimension 4: Land Economics & Affordability
    # -------------------------------------------------------------
    # Minimizes acquisition cost (higher score = lower circle rate per acre)
    reg_medians = df.groupby('region')['land_cost_avg_rs_acre'].transform('median')
    overall_median = df['land_cost_avg_rs_acre'].median()
    cost_imputed = df['land_cost_avg_rs_acre'].fillna(reg_medians).fillna(overall_median)
    land_raw = 1.0 - min_max(np.log1p(cost_imputed))
    df['score_land_affordability'] = min_max(land_raw)

    # -------------------------------------------------------------
    # 5. Objective Dimension 5: Ecosystem & Market Connectivity
    # -------------------------------------------------------------
    # Evaluates established data center facilities and commercial market clusters
    eco_raw = (
        0.70 * min_max(np.log1p(df['dc_count_state'].fillna(0.0))) +
        0.30 * min_max(df['dc_market_count_state'].fillna(0.0))
    )
    df['score_ecosystem'] = min_max(eco_raw)

    # -------------------------------------------------------------
    # 6. Strict Pareto Dominance Engine
    # -------------------------------------------------------------
    dims = ['score_grid', 'score_renewable', 'score_water', 'score_land_affordability', 'score_ecosystem']
    scores_matrix = df[dims].values
    n = len(df)
    is_dominated = np.zeros(n, dtype=bool)

    for i in range(n):
        for j in range(n):
            if i != j:
                # State j dominates state i if j >= i across all 5 dimensions and j > i in at least one
                if np.all(scores_matrix[j] >= scores_matrix[i]) and np.any(scores_matrix[j] > scores_matrix[i]):
                    is_dominated[i] = True
                    break

    df['is_pareto_optimal'] = (~is_dominated).astype(int)

    # -------------------------------------------------------------
    # 7. TOPSIS Multi-Criteria Decision Analysis (4 Archetype Profiles)
    # -------------------------------------------------------------
    def compute_topsis(weights):
        w = np.array(weights)
        ideal_pos = np.ones(len(w))
        ideal_neg = np.zeros(len(w))
        dist_pos = np.sqrt(np.sum(w * (scores_matrix - ideal_pos)**2, axis=1))
        dist_neg = np.sqrt(np.sum(w * (scores_matrix - ideal_neg)**2, axis=1))
        return dist_neg / (dist_pos + dist_neg)

    df['topsis_balanced'] = compute_topsis([0.20, 0.20, 0.20, 0.20, 0.20])
    df['topsis_green_hyperscale'] = compute_topsis([0.35, 0.35, 0.15, 0.10, 0.05])
    df['topsis_cost_optimized'] = compute_topsis([0.25, 0.15, 0.20, 0.35, 0.05])
    df['topsis_market_first'] = compute_topsis([0.25, 0.15, 0.15, 0.10, 0.35])

    # Assign ranks
    df['rank_balanced'] = df['topsis_balanced'].rank(ascending=False, method='min').astype(int)
    df['rank_green_hyperscale'] = df['topsis_green_hyperscale'].rank(ascending=False, method='min').astype(int)
    df['rank_cost_optimized'] = df['topsis_cost_optimized'].rank(ascending=False, method='min').astype(int)
    df['rank_market_first'] = df['topsis_market_first'].rank(ascending=False, method='min').astype(int)

    # Export clean results
    cols_export = [
        'state_id', 'state_name', 'region', 'is_pareto_optimal',
        'score_grid', 'score_renewable', 'score_water', 'score_land_affordability', 'score_ecosystem',
        'topsis_balanced', 'rank_balanced',
        'topsis_green_hyperscale', 'rank_green_hyperscale',
        'topsis_cost_optimized', 'rank_cost_optimized',
        'topsis_market_first', 'rank_market_first',
        'transformation_capacity_total_mva', 'renewable_headroom_mw', 'waterbody_count_total',
        'gw_depletion_trend_mbgl_per_yr', 'land_cost_avg_rs_acre', 'dc_count_state'
    ]
    df_sorted = df[cols_export].sort_values(by='topsis_balanced', ascending=False)
    os.makedirs("clean", exist_ok=True)
    df_sorted.to_csv(OUT_RANKING_PATH, index=False)
    print(f"Saved {OUT_RANKING_PATH} ({len(df_sorted)} rows).")

    # Document checkpoint
    write_checkpoint(df_sorted)

def write_checkpoint(df):
    os.makedirs("checkpoint", exist_ok=True)
    with open(CHECKPOINT_PATH, "w") as f:
        f.write("# Stage 2: Multi-Objective Siting Optimization & Pareto Ranking Summary\n\n")
        f.write("## 1. Mathematical Formulation\n\n")
        f.write("The framework solves the multi-objective siting problem without invented black-box labels by jointly evaluating 5 grounded objective vectors:\n\n")
        f.write("$$\\max_{x \\in \\mathcal{X}} \\left\\{ S_{\\text{Grid}}(x), S_{\\text{Renewable}}(x), S_{\\text{Water}}(x), S_{\\text{LandAffordability}}(x), S_{\\text{Ecosystem}}(x) \\right\\}$$\n\n")

        f.write("### Objective Vector Definitions:\n")
        f.write("1. **$S_{\\text{Grid}}$ (Bulk Power Grid Capacity & Density):** Fuses $\\log(1 + \\text{MVA})$, high-voltage substations count ($N_{400\\text{kV+}}$), and installed capacity density ($\\text{MVA}/\\text{km}^2$).\n")
        f.write("2. **$S_{\\text{Renewable}}$ (Clean Energy Headroom):** Fuses available clean headroom ($\\log(1 + \\text{Headroom}_{\\text{MW}})$), installed RE capacity, and 8-year historical growth CAGR.\n")
        f.write("3. **$S_{\\text{Water}}$ (Water Security & Sustainability):** Fuses surface reservoir volume ($\\log(1 + \\text{Waterbodies})$) and multi-decadal groundwater trend stability (rewarding aquifer recharge, penalizing depletion).\n")
        f.write("4. **$S_{\\text{LandAffordability}}$ (Economic Efficiency):** Inverts circle rates ($1 - \\text{MinMax}(\\log(\\text{AvgCost}))$) to maximize cost-efficiency.\n")
        f.write("5. **$S_{\\text{Ecosystem}}$ (Market & Fiber Connectivity):** Evaluates established commercial facilities and enterprise connectivity.\n\n")

        f.write("## 2. Pareto Optimal Set (10 Non-Dominated States)\n\n")
        f.write("A state $x^*$ belongs to the **Pareto Optimal Frontier** $\\mathcal{P}^*$ if no other feasible state $x$ achieves strictly equal or superior scores across all 5 dimensions simultaneously:\n\n")
        f.write("| State | Grid Score | RE Score | Water Score | Land Affordability | Ecosystem Score | Dominant Advantage |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :--- |\n")
        pareto = df[df['is_pareto_optimal'] == 1]
        for _, r in pareto.iterrows():
            f.write(f"| **{r['state_name']} ({r['state_id']})** | {r['score_grid']:.2f} | {r['score_renewable']:.2f} | {r['score_water']:.2f} | {r['score_land_affordability']:.2f} | {r['score_ecosystem']:.2f} | ")
            # Identify highest relative advantage
            advantages = {
                'Power Grid Backbone': r['score_grid'],
                'Clean Renewable Headroom': r['score_renewable'],
                'Water Security & Recharge': r['score_water'],
                'Lowest Land Cost': r['score_land_affordability'],
                'Market Connectivity & Submarine Cables': r['score_ecosystem']
            }
            top_adv = max(advantages, key=advantages.get)
            f.write(f"{top_adv} ({advantages[top_adv]:.2f}) |\n")

        f.write("\n## 3. TOPSIS Siting Rankings by Strategic Archetype\n\n")
        f.write("| Rank | Balanced Enterprise | Green Hyperscale (AI) | Low-Cost / Sovereign | Market-First |\n")
        f.write("| :---: | :--- | :--- | :--- | :--- |\n")
        
        r_bal = df.sort_values(by='rank_balanced')['state_name'].tolist()
        r_hyp = df.sort_values(by='rank_green_hyperscale')['state_name'].tolist()
        r_cost = df.sort_values(by='rank_cost_optimized')['state_name'].tolist()
        r_mkt = df.sort_values(by='rank_market_first')['state_name'].tolist()

        for rank_idx in range(10):
            f.write(f"| **{rank_idx+1}** | {r_bal[rank_idx]} | {r_hyp[rank_idx]} | {r_cost[rank_idx]} | {r_mkt[rank_idx]} |\n")

    print(f"Saved {CHECKPOINT_PATH}.")

if __name__ == "__main__":
    run_stage2_optimization()

