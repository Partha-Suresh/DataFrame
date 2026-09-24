1. State foundation

Replaced old GeoJSON with updated 36-state/UT geography.
Created canonical state_id using shapeISO (IN-KA, IN-MH, etc.).
Standardized state names and regions.

2. MNRE installed capacity

Cleaned malformed state rows and aliases.
Removed Others/Total.
Validated all 36 states/UTs.
Recalculated totals successfully.
Saved as fact_re_state_2025.csv.

3. MNRE renewable potential

Standardized aliases (Orissa → Odisha, etc.).
Removed Others/Total.
Validated all 36 states/UTs.
Recalculated totals successfully.
Saved as fact_re_state_potential.csv.

4. MNRE historical capacity

Cleaned report totals and state-name issues.
Converted 2017–18 → 2024–25 from wide → long format.
35 states/UTs × 8 years = 280 rows.
Andaman & Nicobar was genuinely absent, so no values were invented.
Saved as fact_re_capacity_long.csv.

5. MNRE features
Created:

renewable_headroom_mw
renewable_utilization_pct
re_capacity_growth_mw
re_capacity_growth_pct
re_capacity_cagr_pct

Special handling:

Ladakh: keep absolute growth; don't calculate % growth/CAGR from zero baseline; add a zero-baseline indicator.
Chandigarh: preserve the negative headroom because the source potential is lower than installed capacity rather than artificially correcting it.
Current clean layer
dim_state.csv
fact_re_state_2025.csv
fact_re_state_potential.csv
fact_re_capacity_long.csv
mnre_features.csv

State + MNRE preprocessing is essentially complete.