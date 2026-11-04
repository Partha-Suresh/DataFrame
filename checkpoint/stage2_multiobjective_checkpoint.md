# Stage 2: Multi-Objective Siting Optimization & Pareto Ranking Summary

## 1. Mathematical Formulation

The framework solves the multi-objective siting problem without invented black-box labels by jointly evaluating 5 grounded objective vectors:

$$\max_{x \in \mathcal{X}} \left\{ S_{\text{Grid}}(x), S_{\text{Renewable}}(x), S_{\text{Water}}(x), S_{\text{LandAffordability}}(x), S_{\text{Ecosystem}}(x) \right\}$$

### Objective Vector Definitions:
1. **$S_{\text{Grid}}$ (Bulk Power Grid Capacity & Density):** Fuses $\log(1 + \text{MVA})$, high-voltage substations count ($N_{400\text{kV+}}$), and installed capacity density ($\text{MVA}/\text{km}^2$).
2. **$S_{\text{Renewable}}$ (Clean Energy Headroom):** Fuses available clean headroom ($\log(1 + \text{Headroom}_{\text{MW}})$), installed RE capacity, and 8-year historical growth CAGR.
3. **$S_{\text{Water}}$ (Water Security & Sustainability):** Fuses surface reservoir volume ($\log(1 + \text{Waterbodies})$) and multi-decadal groundwater trend stability (rewarding aquifer recharge, penalizing depletion).
4. **$S_{\text{LandAffordability}}$ (Economic Efficiency):** Inverts circle rates ($1 - \text{MinMax}(\log(\text{AvgCost}))$) to maximize cost-efficiency.
5. **$S_{\text{Ecosystem}}$ (Market & Fiber Connectivity):** Evaluates established commercial facilities and enterprise connectivity.

## 2. Pareto Optimal Set (10 Non-Dominated States)

A state $x^*$ belongs to the **Pareto Optimal Frontier** $\mathcal{P}^*$ if no other feasible state $x$ achieves strictly equal or superior scores across all 5 dimensions simultaneously:

| State | Grid Score | RE Score | Water Score | Land Affordability | Ecosystem Score | Dominant Advantage |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Maharashtra (IN-MH)** | 0.81 | 0.88 | 0.85 | 0.44 | 1.00 | Market Connectivity & Submarine Cables (1.00) |
| **Gujarat (IN-GJ)** | 0.95 | 0.91 | 0.82 | 0.52 | 0.54 | Power Grid Backbone (0.95) |
| **Madhya Pradesh (IN-MP)** | 0.75 | 0.79 | 0.77 | 1.00 | 0.39 | Lowest Land Cost (1.00) |
| **Tamil Nadu (IN-TN)** | 0.85 | 0.83 | 1.00 | 0.30 | 0.77 | Water Security & Recharge (1.00) |
| **Rajasthan (IN-RJ)** | 0.97 | 1.00 | 0.44 | 0.80 | 0.44 | Clean Renewable Headroom (1.00) |
| **Telangana (IN-TG)** | 0.75 | 0.70 | 0.79 | 0.52 | 0.62 | Water Security & Recharge (0.79) |
| **Karnataka (IN-KA)** | 0.73 | 0.84 | 0.86 | 0.40 | 0.60 | Water Security & Recharge (0.86) |
| **Uttar Pradesh (IN-UP)** | 1.00 | 0.66 | 0.46 | 0.62 | 0.61 | Power Grid Backbone (1.00) |
| **West Bengal (IN-WB)** | 0.63 | 0.47 | 0.61 | 0.70 | 0.50 | Lowest Land Cost (0.70) |
| **Bihar (IN-BR)** | 0.82 | 0.41 | 0.67 | 0.70 | 0.18 | Power Grid Backbone (0.82) |

## 3. TOPSIS Siting Rankings by Strategic Archetype

| Rank | Balanced Enterprise | Green Hyperscale (AI) | Low-Cost / Sovereign | Market-First |
| :---: | :--- | :--- | :--- | :--- |
| **1** | Maharashtra | Gujarat | Madhya Pradesh | Maharashtra |
| **2** | Gujarat | Maharashtra | Chhattisgarh | Tamil Nadu |
| **3** | Madhya Pradesh | Rajasthan | Rajasthan | Gujarat |
| **4** | Tamil Nadu | Tamil Nadu | Gujarat | Telangana |
| **5** | Rajasthan | Madhya Pradesh | Maharashtra | Karnataka |
| **6** | Telangana | Karnataka | Uttar Pradesh | Uttar Pradesh |
| **7** | Karnataka | Telangana | Telangana | Rajasthan |
| **8** | Uttar Pradesh | Uttar Pradesh | Bihar | Madhya Pradesh |
| **9** | Chhattisgarh | Andhra Pradesh | Tamil Nadu | Andhra Pradesh |
| **10** | Andhra Pradesh | Chhattisgarh | Odisha | West Bengal |
