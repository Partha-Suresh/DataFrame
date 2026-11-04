# Stage 1: Hard Feasibility Constraints Summary

## 1. Mathematical Formulation & Siting Rules

A location is passed to the Multi-Objective Ranking stage (Stage 2) if and only if it satisfies all four non-negotiable physical viability constraints:

$$\text{Feasible}_{\text{Enterprise}} = C_1 \wedge C_2 \wedge C_3 \wedge C_4$$

where:
- **$C_1$ (Bulk Transmission Grid Viability):** $\text{Capacity}_{\text{MVA}} \ge 1,000 \wedge \text{MaxVoltage}_{\text{kV}} \ge 220$.
- **$C_2$ (Renewable Energy Headroom):** $\text{Headroom}_{\text{MW}} > 0 \wedge \text{InstalledRE}_{\text{MW}} \ge 50$.
- **$C_3$ (Water Resource Availability):** $\text{Waterbodies} \ge 100 \vee \text{GW}_{\text{trend}} \le +0.15\text{ mbgl/yr}$.
- **$C_4$ (National Grid Synchronous Connection):** $\text{StateID} \notin \{\text{IN-LD}, \text{IN-AN}\}.$

### Hyperscale Tier Qualification ($C_{\text{Hyperscale}}$)
$$\text{Feasible}_{\text{Hyperscale}} = \text{Feasible}_{\text{Enterprise}} \wedge (N_{400\text{kV}} + N_{765\text{kV}} > 0) \wedge \text{Capacity}_{\text{MVA}} \ge 10,000 \wedge \text{Headroom}_{\text{MW}} \ge 10,000$$

## 2. Evaluation Results Across 36 States/UTs

- **Enterprise Feasible States:** 26 / 36 (72.2%)
- **Hyperscale Feasible States:** 15 / 36 (41.7%)
- **Infeasible States Filtered Out:** 10 / 36

### Filtered Infeasible States Breakdown
- **Puducherry (IN-PY):** Failed C1 (Bulk Grid <1,000 MVA or <220 kV)
- **Lakshadweep (IN-LD):** Failed C1 (Bulk Grid <1,000 MVA or <220 kV); Failed C2 (RE Capacity <50 MW or Negative Headroom); Failed C4 (Offshore Island / Non-Synchronous Grid)
- **Sikkim (IN-SK):** Failed C1 (Bulk Grid <1,000 MVA or <220 kV)
- **Tripura (IN-TR):** Failed C2 (RE Capacity <50 MW or Negative Headroom)
- **Mizoram (IN-MZ):** Failed C1 (Bulk Grid <1,000 MVA or <220 kV)
- **Arunachal Pradesh (IN-AR):** Failed C1 (Bulk Grid <1,000 MVA or <220 kV)
- **Manipur (IN-MN):** Failed C1 (Bulk Grid <1,000 MVA or <220 kV)
- **Dadra and Nagar Haveli and Daman and Diu (IN-DH):** Failed C1 (Bulk Grid <1,000 MVA or <220 kV)
- **Chandigarh (IN-CH):** Failed C1 (Bulk Grid <1,000 MVA or <220 kV); Failed C2 (RE Capacity <50 MW or Negative Headroom); Failed C3 (Water Resource Deficit / Extreme Depletion)
- **Andaman and Nicobar Islands (IN-AN):** Failed C1 (Bulk Grid <1,000 MVA or <220 kV); Failed C2 (RE Capacity <50 MW or Negative Headroom); Failed C4 (Offshore Island / Non-Synchronous Grid)

### Qualified Hyperscale Candidates (15 States)
- **Rajasthan (IN-RJ):** Grid Capacity: 121,400 MVA | 400kV+ Substations: 106 | RE Headroom: 1,080,657 MW
- **Uttar Pradesh (IN-UP):** Grid Capacity: 120,915 MVA | 400kV+ Substations: 129 | RE Headroom: 100,817 MW
- **Gujarat (IN-GJ):** Grid Capacity: 116,935 MVA | 400kV+ Substations: 73 | RE Headroom: 394,561 MW
- **Maharashtra (IN-MH):** Grid Capacity: 62,076 MVA | 400kV+ Substations: 52 | RE Headroom: 648,622 MW
- **Tamil Nadu (IN-TN):** Grid Capacity: 58,550 MVA | 400kV+ Substations: 62 | RE Headroom: 279,220 MW
- **Andhra Pradesh (IN-AP):** Grid Capacity: 57,740 MVA | 400kV+ Substations: 62 | RE Headroom: 415,818 MW
- **Bihar (IN-BR):** Grid Capacity: 46,955 MVA | 400kV+ Substations: 51 | RE Headroom: 38,443 MW
- **Madhya Pradesh (IN-MP):** Grid Capacity: 43,785 MVA | 400kV+ Substations: 44 | RE Headroom: 369,723 MW
- **Karnataka (IN-KA):** Grid Capacity: 40,595 MVA | 400kV+ Substations: 32 | RE Headroom: 380,309 MW
- **Telangana (IN-TG):** Grid Capacity: 35,939 MVA | 400kV+ Substations: 43 | RE Headroom: 190,680 MW
- **Chhattisgarh (IN-CT):** Grid Capacity: 33,130 MVA | 400kV+ Substations: 29 | RE Headroom: 130,168 MW
- **West Bengal (IN-WB):** Grid Capacity: 22,260 MVA | 400kV+ Substations: 22 | RE Headroom: 24,854 MW
- **Punjab (IN-PB):** Grid Capacity: 21,225 MVA | 400kV+ Substations: 21 | RE Headroom: 11,683 MW
- **Odisha (IN-OR):** Grid Capacity: 20,692 MVA | 400kV+ Substations: 16 | RE Headroom: 152,054 MW
- **Jharkhand (IN-JH):** Grid Capacity: 13,265 MVA | 400kV+ Substations: 15 | RE Headroom: 52,088 MW

### Qualified Regional / Edge Candidates (11 States)
- **Haryana (IN-HR):** Grid Capacity: 27,895 MVA | Substations: 173 | RE Headroom: 6,434 MW
- **Delhi (IN-DL):** Grid Capacity: 9,940 MVA | Substations: 36 | RE Headroom: 153 MW
- **Uttarakhand (IN-UT):** Grid Capacity: 6,595 MVA | Substations: 15 | RE Headroom: 492 MW
- **Assam (IN-AS):** Grid Capacity: 5,920 MVA | Substations: 22 | RE Headroom: 20,216 MW
- **Himachal Pradesh (IN-HP):** Grid Capacity: 5,452 MVA | Substations: 23 | RE Headroom: 31,379 MW
- **Kerala (IN-KL):** Grid Capacity: 5,306 MVA | Substations: 23 | RE Headroom: 15,071 MW
- **Jammu and Kashmir (IN-JK):** Grid Capacity: 3,470 MVA | Substations: 16 | RE Headroom: 19,726 MW
- **Ladakh (IN-LA):** Grid Capacity: 1,675 MVA | Substations: 3 | RE Headroom: 8,415 MW
- **Nagaland (IN-NL):** Grid Capacity: 1,310 MVA | Substations: 5 | RE Headroom: 641 MW
- **Goa (IN-GA):** Grid Capacity: 1,126 MVA | Substations: 3 | RE Headroom: 6,746 MW
- **Meghalaya (IN-ML):** Grid Capacity: 1,060 MVA | Substations: 4 | RE Headroom: 16,659 MW
