After Groundwater — Concise Summary
1. Land Cost
   - Cleaned 12-state land-cost dataset.
   - Converted ₹/acre and CAGR strings to numeric.
   - Added canonical state_id.
   - Engineered land_cost_log_avg and land_cost_high_low_spread.
   - Finalized 8-column state-level dataset.
2. Datacenter Distribution
   - Inspected 34 markets / 305 total datacenters.
   - Standardized columns to market, data_center_count.
   - Created verified market → state mapping.
   - Added state_id and state_name.
   - Kept it at market level; no state aggregation.
   - Output: fact_market_datacentres.csv.
3. Region Coordinates
   - Skipped as not essential.
4. CEA Regional Generation
   - Inspected 2017–2020 daily data: 4,945 rows, 5 regions.
   - Cleaned dates and thermal numeric fields.
   - Preserved systematic nuclear NaNs for Eastern/NorthEastern.
   - Preserved valid hydro zero values.
   - Created daily clean layer:
     fact_regional_generation_daily.csv
   - Engineered regional features:
     - Mean
     - Standard deviation
     - Actual − estimated deviation
     - Generation trend
     - Days available