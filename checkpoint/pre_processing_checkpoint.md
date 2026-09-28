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

MNRE Bio/Solar Breakdown
- Inspected mnre_bio_and_solar_breakdown_2025.csv.
- Dataset initially had 41 rows × 9 columns.
- Removed report-level rows:
  - Others
  - Total (MW)
- Standardized split/variant state names:
  - Andaman & + Nicobar Islands → Andaman and Nicobar Islands
  - Dadra & Nagar + Haveli / + Daman & Diu → Dadra and Nagar Haveli and Daman and Diu
  - Jammu & Kashmir → Jammu and Kashmir
  - Pondicherry → Puducherry
- Aggregated the split state/UT rows, resulting in 36 canonical states/UTs.
- Added canonical state_id using dim_state.
- Created derived totals:
  - biomass_breakdown_total_mw
  - waste_to_energy_total_mw
  - solar_breakdown_total_mw
- Standardized all feature names to lowercase.
- Kept the detailed biomass, waste-to-energy, and solar components rather than collapsing them.
- Final dataset: 36 × 13.
- Saved as:
fact_re_bio_solar_breakdown_2025.csv