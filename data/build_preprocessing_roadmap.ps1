$ErrorActionPreference = 'Stop'

$outputPath = Join-Path (Get-Location) 'Data_Preprocessing_and_Feature_Engineering_Roadmap.docx'

function WordColor([int]$r, [int]$g, [int]$b) {
    return $r + ($g * 256) + ($b * 65536)
}

$blue = WordColor 46 116 181
$darkBlue = WordColor 31 77 120
$ink = WordColor 11 37 69
$muted = WordColor 89 89 89
$lightBlue = WordColor 232 238 245
$lightGray = WordColor 242 244 247
$callout = WordColor 244 246 249
$white = WordColor 255 255 255
$black = WordColor 0 0 0

$word = $null
$doc = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Add()
    $section = $doc.Sections.Item(1)
    $section.PageSetup.TopMargin = 72
    $section.PageSetup.BottomMargin = 72
    $section.PageSetup.LeftMargin = 72
    $section.PageSetup.RightMargin = 72
    $section.PageSetup.HeaderDistance = 35.4
    $section.PageSetup.FooterDistance = 35.4

    function New-ParaStyle([string]$name, [double]$size, [int]$color, [double]$before, [double]$after, [double]$lineSpacing, [bool]$bold = $false) {
        $style = $doc.Styles.Add($name, 1)
        $style.Font.Name = 'Calibri'
        $style.Font.Size = $size
        $style.Font.Color = $color
        $style.Font.Bold = [int]$bold
        $style.ParagraphFormat.SpaceBefore = $before
        $style.ParagraphFormat.SpaceAfter = $after
        $style.ParagraphFormat.LineSpacing = $lineSpacing
        return $style
    }

    $null = New-ParaStyle 'Roadmap Body' 11 $black 0 6 13.75 $false
    $null = New-ParaStyle 'Roadmap Title' 24 $ink 0 6 28 $true
    $null = New-ParaStyle 'Roadmap Subtitle' 12 $muted 0 15 15 $false
    $null = New-ParaStyle 'Roadmap H1' 16 $blue 18 10 19 $true
    $null = New-ParaStyle 'Roadmap H2' 13 $blue 14 7 16 $true
    $null = New-ParaStyle 'Roadmap H3' 12 $darkBlue 10 5 15 $true
    $null = New-ParaStyle 'Roadmap Small' 9 $muted 0 4 11 $false

    $header = $section.Headers.Item(1).Range
    $header.Text = 'DATA PREPARATION ROADMAP | INDIA ENERGY AND DATA-CENTRE DATA'
    $header.Font.Name = 'Calibri'
    $header.Font.Size = 8.5
    $header.Font.Color = $muted
    $header.ParagraphFormat.Alignment = 0
    $header.ParagraphFormat.SpaceAfter = 0

    $footer = $section.Footers.Item(1).Range
    $footer.Text = 'Data preprocessing guide | Page '
    $footer.Font.Name = 'Calibri'
    $footer.Font.Size = 8.5
    $footer.Font.Color = $muted
    $footer.ParagraphFormat.Alignment = 2
    $null = $footer.Fields.Add($footer, 33)

    $sel = $word.Selection

    function Add-Text([string]$text, [string]$style = 'Roadmap Body') {
        $sel.Style = $style
        $sel.TypeText($text)
        $sel.TypeParagraph()
    }

    function Add-Heading([string]$text, [int]$level = 1) {
        $style = switch ($level) {
            1 { 'Roadmap H1' }
            2 { 'Roadmap H2' }
            default { 'Roadmap H3' }
        }
        Add-Text $text $style
    }

    function Add-Bullet([string]$text) {
        $sel.Style = 'Roadmap Body'
        $sel.TypeText($text)
        $sel.Range.ListFormat.ApplyBulletDefault()
        $sel.TypeParagraph()
    }

    function Add-Note([string]$text) {
        $table = $doc.Tables.Add($sel.Range, 1, 1)
        $table.AutoFitBehavior(0)
        $table.PreferredWidthType = 3
        $table.PreferredWidth = 468
        $table.Columns.Item(1).Width = 468
        $table.Rows.SetLeftIndent(6, 0)
        $cell = $table.Cell(1, 1)
        $cell.Range.Text = $text
        $cell.Range.Font.Name = 'Calibri'
        $cell.Range.Font.Size = 10.5
        $cell.Range.Font.Color = $ink
        $cell.Range.ParagraphFormat.SpaceBefore = 3
        $cell.Range.ParagraphFormat.SpaceAfter = 3
        $cell.Shading.BackgroundPatternColor = $callout
        $table.Borders.Enable = 1
        $sel.SetRange($table.Range.End, $table.Range.End)
        $sel.TypeParagraph()
    }

    function Add-Table([object[]]$rows, [double[]]$widths) {
        $table = $doc.Tables.Add($sel.Range, $rows.Count, $widths.Count)
        $table.AutoFitBehavior(0)
        $table.PreferredWidthType = 3
        $table.PreferredWidth = 468
        $table.Rows.SetLeftIndent(6, 0)
        $table.Borders.Enable = 1
        for ($c = 1; $c -le $widths.Count; $c++) {
            $table.Columns.Item($c).Width = $widths[$c - 1]
            $table.Columns.Item($c).PreferredWidthType = 3
            $table.Columns.Item($c).PreferredWidth = $widths[$c - 1]
        }
        for ($r = 1; $r -le $rows.Count; $r++) {
            for ($c = 1; $c -le $widths.Count; $c++) {
                $cell = $table.Cell($r, $c)
                $cell.Range.Text = [string]$rows[$r - 1][$c - 1]
                $cell.Range.Font.Name = 'Calibri'
                $cell.Range.Font.Size = if ($r -eq 1) { 9.2 } else { 9.0 }
                $cell.Range.ParagraphFormat.SpaceBefore = 1.5
                $cell.Range.ParagraphFormat.SpaceAfter = 1.5
                $cell.VerticalAlignment = 0
                if ($r -eq 1) {
                    $cell.Range.Font.Bold = 1
                    $cell.Range.Font.Color = $ink
                    $cell.Shading.BackgroundPatternColor = $lightBlue
                } else {
                    $cell.Range.Font.Color = $black
                    if (($r % 2) -eq 0) { $cell.Shading.BackgroundPatternColor = $white } else { $cell.Shading.BackgroundPatternColor = $lightGray }
                }
            }
        }
        $table.Rows.Item(1).HeadingFormat = $true
        $sel.SetRange($table.Range.End, $table.Range.End)
        $sel.TypeParagraph()
    }

    function Add-PageBreak() { $sel.InsertBreak(7) }

    # Title block: named override for this report (24 pt ink-blue title, compact metadata).
    Add-Text 'DATA PREPROCESSING AND FEATURE ENGINEERING ROADMAP' 'Roadmap Title'
    Add-Text 'File-by-file guidance for the India energy, infrastructure, water and data-centre datasets' 'Roadmap Subtitle'
    Add-Text 'Prepared: 22 September 2026 | Scope: source assessment, preprocessing order and ML-ready feature planning' 'Roadmap Small'
    Add-Note 'Decision: begin with a state-level analytical panel and keep regional daily generation as a separate time-series track. Do not force all files into one training table. A prediction target has not yet been selected, so this guide creates auditable, target-agnostic assets and quarantines unsafe source extracts.'

    Add-Heading '1. Executive decision: where to start', 1
    Add-Text 'The useful starting point is a state dimension plus a 2025 renewable-energy and resource snapshot. It is the only coherent join path across renewable capacity, potential, water availability proxies, land costs and the geography file. The data-centre file is city-level; map its 34 markets to the same state key before using it as a target, a ranking input or a descriptive outcome.'
    Add-Table @(
        @('Build order', 'Files to use first', 'Why this comes first'),
        @('1. Canonical geography', 'archive\\india_states.geojson; State_Region_corrected.csv', 'Creates state_id, canonical state name, region, area and geometry. Every state-level join depends on this.'),
        @('2. Renewable snapshot', 'mnre_re_installed_capacity_by_source_2025.csv; mnre_re_estimated_potential_by_state.csv; mnre_re_cumulative_capacity_timeseries_2018_2025.csv', 'Best foundation for capacity, resource headroom and historical growth. Repair aliases and remove report totals before merging.'),
        @('3. Resource and cost enrichments', 'area-wise-waterbodies-india-statewise.csv; state-ground-water-level-information.csv; statewise land cost.csv', 'Useful siting inputs. Waterbody data is complete; groundwater and land cost need explicit missingness treatment.'),
        @('4. Data-centre outcome layer', 'Datacenters distribution in india.csv', 'Maps 305 data centres across 34 markets. Add a verified market-to-state crosswalk and retain city grain.'),
        @('5. Separate temporal track', 'file_02.csv; clean CEA time series where approved', 'Daily regional generation supports time-series work. It must not be cross-joined to the state snapshot without an explicit aggregation or target design.')
    ) @(102, 172, 194)

    Add-Heading '2. Non-negotiable preprocessing contract', 1
    Add-Bullet 'Keep raw files immutable. Write each repaired output to a clean layer and retain source_file, source_row and processing_version fields for lineage.'
    Add-Bullet 'Read text CSVs as UTF-8. The land-cost rupee symbol and the substation plus/minus voltage symbol render correctly in UTF-8; default Windows decoding makes them appear corrupted.'
    Add-Bullet 'Create a dim_state_alias table before any merge. Use state_id as the join key, not display labels. Normalise trim, case and punctuation, then explicitly map historical names such as Pondicherry/Puducherry, Odisha/Orissa and union-territory variants.'
    Add-Bullet 'Remove national, regional and report-total rows from state facts before joining. Recompute totals from components and keep a total_recomputed flag rather than trusting malformed report totals.'
    Add-Bullet 'Never encode a label, name, address, source URL or row index as a numeric feature. Preserve identifiers for joins and diagnostics only.'
    Add-Bullet 'Use train-only fitting for imputation, scaling, frequency encoding and target encoding. For time series split by time; for state/site work use group-aware or spatially aware validation rather than random row splits.'

    Add-Heading '3. Recommended clean-layer outputs', 1
    Add-Table @(
        @('Output asset', 'Grain / key', 'Content and gate'),
        @('dim_state.csv', 'one row per state_id', 'GeoJSON name, corrected region, area_km2, geometry reference and aliases. Extend the 34-row regional file to the GeoJSON coverage; no unmatched usable fact key is allowed.'),
        @('bridge_market_state.csv', 'one row per market', 'Verified market, state_id, city name, source and confidence. Keep Mumbai and Navi Mumbai as distinct markets while allowing a state aggregate.'),
        @('fact_re_state_2025.csv', 'state_id, snapshot_date', 'Installed capacity and estimated potential by source, after removal or repair of continuation, Others and Total rows.'),
        @('fact_re_capacity_long.csv', 'state_id, financial_year', 'Wide cumulative-capacity file reshaped to long form. Keep regional totals in a separate table, never as state rows.'),
        @('fact_state_resources.csv', 'state_id', 'Waterbody counts, groundwater range fields and land-cost fields with coverage flags.'),
        @('fact_market_datacentres.csv', 'market, snapshot_date', 'Current data-centre count plus state_id through the bridge. Do not pretend this has an observed historical date if none is present.'),
        @('fact_regional_generation_daily.csv', 'date, region', 'Actual and estimated thermal, nuclear and hydro values from file_02, plus availability flags and time features.'),
        @('quarantine_manifest.csv', 'source file / reason', 'Every file or row blocked from ML use, the failing test and the approved remediation path.')
    ) @(130, 130, 208)

    Add-Heading '4. Features to engineer after the clean layer', 1
    Add-Table @(
        @('Feature family', 'Examples', 'Rules / leakage controls'),
        @('Renewable capacity and headroom', 'source capacity shares; re_capacity_mw / re_potential_mw; potential_remaining_mw; source diversity index', 'Align snapshot dates. Divide only after zero checks; keep numerator and denominator. Capacity/potential ratios are descriptive unless both were available before the prediction date.'),
        @('Growth', 'year-on-year capacity delta; growth rate; 3-year CAGR; rank within region', 'Derive only from the long capacity fact and use lagged values. No future years in a training feature.'),
        @('Water and land', 'waterbody_count_total; small/large waterbody share; water_level_range; log_land_cost; land_cost_spread', 'Water-level columns are reported ranges, not a validated water-stress score. Do not infer stress direction without metadata. Land data covers only 12 states; include land_cost_missing.'),
        @('Grid and substations', 'count, capacity sum, median voltage, asset age, sector mix', 'Use only once state/city geography is resolved. Capacity is labeled MW/MVA in the large file; preserve unit uncertainty and do not mix it with MW generation.'),
        @('Data-centre market', 'market count; state aggregate; centres per area; market present flag', 'Keep city and state metrics separate. If data-centre count is the target, do not use a same-date count-derived feature as a predictor.'),
        @('Regional daily generation', 'actual-minus-estimated; absolute percentage error; weekday/month/monsoon proxy; 7/30-day rolling means; lags', 'Sort by date within region, use only prior observations for lags/rolls and retain structural nuclear-missing flags.'),
        @('Geography', 'region one-hot; centroid latitude/longitude; area', 'Use region coordinates only for display or a coarse regional reference. Prefer state geometry-derived centroids for state-level model features.')
    ) @(118, 174, 176)

    Add-Heading '5. Encoding and missing-data rules', 1
    Add-Table @(
        @('Field type', 'Treatment', 'Do not do this'),
        @('Low-cardinality category', 'One-hot encode region and substation sector; keep an explicit Unknown category where valid.', 'Do not ordinal-encode nominal labels such as Northern=1, Southern=2.'),
        @('High-cardinality category', 'For executive agency use train-fold frequency encoding or a regularised target encoder only after target and split are defined.', 'Do not label-encode agency, market, name or address as arbitrary integers.'),
        @('Dates / fiscal years', 'Parse into a date or financial-year start/end; derive cyclical calendar variables only for daily data.', 'Do not treat 2017-18 as a continuous numeric measurement without defining its temporal convention.'),
        @('Currency / percentage text', 'Strip rupee symbols, Indian digit separators and percent signs; store numeric rupees per acre and CAGR as decimal.', 'Do not cast strings such as Rs 8,00,000 or 14% directly without cleaning and range tests.'),
        @('Structural missing values', 'Use an availability flag. In file_02, nuclear values are missing for most Eastern and NorthEastern records; distinguish not-reported from zero.', 'Do not blindly impute structural nuclear missingness to the global mean or zero.'),
        @('Sparse coverage', 'For groundwater and land use missingness flags; evaluate model performance with and without these features.', 'Do not claim nationwide coverage from 29 groundwater or 12 land-cost records.')
    ) @(120, 183, 165)

    Add-PageBreak
    Add-Heading '6. File-by-file register: start and core inputs', 1
    Add-Text 'The following files are the first pass. “Repair” means create a documented clean copy; it does not mean overwrite the supplied file.'
    Add-Table @(
        @('File', 'Disposition', 'File-specific preprocessing and feature work'),
        @('archive\\india_states.geojson', 'START - core dimension', '35 Polygon/MultiPolygon features. Retain NAME_1, ID_1 and geometry; make a canonical state_id. Do not use free-text VARNAME_1 as a model feature. Build centroid only after geometry validation.'),
        @('State_Region_corrected.csv', 'START - core dimension', '34 rows with area and region. Rename headers to snake_case, parse area and national_share_pct, standardise state names and reconcile its incomplete coverage against GeoJSON.'),
        @('mnre_re_installed_capacity_by_source_2025.csv', 'START after entity repair', '37 filtered detail rows reconcile to source components. Reassemble broken union-territory continuation rows, drop Others/Total, numeric-cast MWs and recompute total_res_mw from components.'),
        @('mnre_re_estimated_potential_by_state.csv', 'START after alias mapping', '35 filtered detail rows reconcile to reported total. Drop Others/Total, numeric-cast MWs and derive source potential shares and remaining potential only when joined to a same-definition capacity snapshot.'),
        @('mnre_re_cumulative_capacity_timeseries_2018_2025.csv', 'START after reshape', '42 rows include regional totals, Grand Total and Others. Remove non-state rows, map the abbreviated Dadra and Nagar label, melt year columns to financial_year and derive lagged growth.'),
        @('area-wise-waterbodies-india-statewise.csv', 'START - resource feature', '37 complete state rows. Rename size bands, numeric-cast counts, sum to waterbody_count_total and derive size-band shares. Reconcile six names not matching GeoJSON after normalisation.'),
        @('state-ground-water-level-information.csv', 'START with coverage flag', '29 state rows. Numeric-cast station count and min/max ranges; check min <= max; derive observed_range_width. Preserve the source semantics and unit uncertainty.'),
        @('statewise land cost.csv', 'START as sparse feature', '12 rows. Read UTF-8; parse rupee/Indian-grouped strings and CAGR. Derive log_avg_land_cost and high_low_spread, retain land_cost_missing outside the 12 covered states.'),
        @('Datacenters distribution in india.csv', 'START - outcome layer', '34 unique markets and 305 total centres. Rename to market and data_center_count, integer-cast count, add a verified market-to-state bridge, then retain both city and state aggregate grains.'),
        @('region_cordinates.csv', 'START for maps only', 'Five regional reference points; trim the trailing space in Western. Use for presentation or a coarse regional join, not as a substitute for state centroids.'),
        @('file_02.csv', 'START - separate time series', '4,945 unique date-region records from 2017-09-01 to 2020-08-01. Drop index (310 duplicate values); parse comma-formatted MU fields, date and region; derive residuals, lags and rolling features within region.'),
        @('mnre_re_share_in_total_capacity_2025.csv', 'START after recomputation', 'Detail rows are largely usable, but Delhi, Lakshadweep and Pondicherry report zero total RE despite non-zero components. Drop Others/Total and recompute total_re, grand_total and shares from components for every state.')
    ) @(126, 105, 237)

    Add-Heading '7. File-by-file register: conditional or repair-first inputs', 1
    Add-Table @(
        @('File', 'Disposition', 'File-specific preprocessing and feature work'),
        @('mnre_bio_and_solar_breakdown_2025.csv', 'REPAIR FIRST', 'State names are split across continuation rows for Andaman/Nicobar and Dadra/Nagar Haveli/Daman/Diu; Others and a malformed Total row exist. Reassemble entities from source, remove report rows, then use source MW shares.'),
        @('mnre_re_generation_by_source_statewise_2024_2025.csv', 'QUARANTINE pending re-extract', '11 of 36 filtered state rows have total generation values that contradict component sums by material amounts. Do not train on it or silently replace totals; re-extract the official table and reconcile all components.'),
        @('cea_installed_capacity_statewise_fuelwise_jul2026.csv', 'QUARANTINE pending re-extract', '177 rows have internally consistent arithmetic, but most state labels have been lost/replaced by regional labels and broken total text. Re-extract from the CEA source before any state-level use.'),
        @('Substation_Details_1789031375809.csv', 'CONDITIONAL - useful asset table', '2,851 rows; remove five non-record/footer rows and rows with blank key fields. Parse UTF-8 voltage, numeric capacity, month-year date and fiscal year. Extract high/low kV, HVDC flag, asset age and agency/sector features after resolving location.'),
        @('Electricity Substation.csv', 'CONDITIONAL - Aizawl only', '12 coordinate-level Aizawl records. Parse MMM-YY dates, transformer expressions such as 2 x 25 into summed MVA, voltage from name and geospatial deduplication key. Useful only for local case work, not a national model.'),
        @('sub-stations-220-kv-and.csv', 'CONDITIONAL - reconstruct schema', '20 HTML-contaminated descriptions; the second “State Sector” field is numeric but does not contain a state. Rename to raw_description and reported_capacity_delta_mva only after source verification; extract voltage ratios and place names.'),
        @('cubems-smart-building-energy-and-iaq-summary.csv', 'CONTEXT / benchmark', '14 floor-year summaries for seven floors in 2018-19, not Indian data-centre operations. Derive average kW per recorded row only with sampling-frequency documentation; do not merge into the India state panel.'),
        @('cea_historical_energy_requirement_availability_2003_2026.csv', 'CONDITIONAL - clean national series', '23 unique annual rows through 2025-26. Parse fiscal year, validate supplied deficit/growth calculations and use only for national temporal context or forecasting with time-based validation.'),
        @('cea_historical_peak_demand_met_2003_2026.csv', 'CONDITIONAL - clean national series', '23 unique annual rows through 2025-26. Treat as a separate national series; derive peak deficit and growth only from earlier fiscal years.'),
        @('cea_historical_cost_of_power_supply_and_realisation.csv', 'CONTEXT ONLY', 'Nine clean rows ending 2012-13. Numeric-cast paise/kWh and derive supply-realisation gaps, but it is too small and stale for a standalone ML feature set.'),
        @('cea_historical_power_capacity_growth_since_1985.csv', 'CONTEXT ONLY', 'Eight plan-end snapshots. Extract the terminal year from Plan_Year and recompute component totals for checks; use for EDA, not model training.'),
        @('cea_transmission_grid_voltage_classes.csv', 'LOOKUP ONLY', 'Five voltage-class definitions. Standardise voltage_kv and use to validate/explain substation voltage parsing; it has no modelling sample size by itself.')
    ) @(126, 105, 237)

    Add-Heading '8. File-by-file register: exclude, duplicate or reference-only', 1
    Add-Table @(
        @('File', 'Disposition', 'Reason and action'),
        @('cea_historical_coal_consumption_2004_2023.csv', 'QUARANTINE', '43 rows contain 17 duplicate fiscal years with conflicting values under one coal column. This is an accidental multi-series append, not a deduplication problem. Re-extract before use.'),
        @('cea_historical_per_capita_consumption_2005_2023.csv', 'QUARANTINE', '34 rows contain 10 duplicate fiscal years with conflicting values under one per-capita column. Re-extract the official series; do not select one duplicate by position.'),
        @('Datacenters distribution in india.xlsx', 'DUPLICATE EXPORT', 'Same one-sheet, 34-row, two-column structure as the CSV. Use the UTF-8 CSV as canonical and retain XLSX only for source verification.'),
        @('Substation_Details_1789031375809.xlsx', 'DUPLICATE EXPORT', 'Same one-sheet, 2,851-row, seven-column structure as the CSV. Use one canonical export to avoid double loading; CSV is simpler for an auditable pipeline.'),
        @('Executive_Summary_July_2026_Actual.pdf', 'REFERENCE ONLY', '66-page CEA source report. It documents supply, capacity and substation tables; use it to re-extract/reconcile damaged CEA CSVs, not as a direct ML input.'),
        @('statewise and national renewable energy stats.pdf', 'REFERENCE ONLY', '121-page MNRE source report. Use for lineage and re-extraction of malformed MNRE rows/totals, not as direct tabular training data.'),
        @('Unrequired data\\global-data-center-dataset.csv', 'EXCLUDE', 'Explicitly in Unrequired data; includes Unnamed columns and substantial missingness. It is global, not a compatible India site-level panel.'),
        @('Unrequired data\\global-data-center-dataset-original.csv', 'EXCLUDE', 'Explicitly in Unrequired data and contains qualitative/approximate global values. Do not blend with measured Indian market counts.'),
        @('Unrequired data\\global-data-center-energy-consumption.csv', 'EXCLUDE', 'Explicitly in Unrequired data and has a multi-row header/schema loss. Keep outside automatic ingestion.')
    ) @(126, 105, 237)

    Add-Heading '9. Pipeline gates before modelling', 1
    Add-Table @(
        @('Gate', 'Pass condition', 'Failure action'),
        @('Schema', 'Expected columns, numeric types, UTF-8 decode and source row count are versioned.', 'Stop the build and record a schema-drift issue.'),
        @('Keys', 'No duplicate state_id/snapshot_date or date/region fact keys; state joins have an explicit match report.', 'Repair aliases or hold unmatched rows in quarantine; never fuzzy-match silently.'),
        @('Totals', 'Published and recomputed totals are reconciled within stated rounding tolerance.', 'Keep recomputed total only when components and definition are verified; otherwise re-extract source.'),
        @('Ranges', 'Non-negative MW/MU/count fields, valid percentages, min <= max water ranges and India coordinate bounds.', 'Flag or remove source/footer records with a reason code.'),
        @('Temporal availability', 'Every feature has an as-of date earlier than the target observation.', 'Remove or lag the leaking feature.'),
        @('Coverage', 'Feature coverage and missingness are reported by state/region and split.', 'Use a missingness flag, limit the model scope or acquire data; do not hide sparse coverage.'),
        @('Evaluation', 'Target, unit of prediction, metric and split strategy are written before encoding/model fitting.', 'Do not select a model or perform target encoding until these choices exist.')
    ) @(110, 196, 162)

    Add-Heading '10. Practical first sprint', 1
    Add-Text '1. Build dim_state_alias and bridge_market_state, including documented manual decisions. 2. Produce fact_re_state_2025 from the three MNRE capacity/potential files and a fact_state_resources table. 3. Run key, coverage, component-total and unit tests. 4. Create a descriptive state_snapshot_2025 feature table without a target. 5. In parallel, clean file_02 into a regional daily time-series table. 6. Re-extract every quarantined CEA/MNRE source before it can enter an ML training pipeline.'
    Add-Note 'Model decision still needed: choose whether the eventual target is (a) market/site suitability or data-centre concentration, (b) regional generation/forecast error, (c) substation capacity or commissioning, or another outcome. Each requires a different grain, date alignment and validation plan; selecting it after the clean layer prevents preventable leakage.'

    Add-Text 'Assessment basis: 33 source files in the supplied directory, including CSV, XLSX, GeoJSON and two source PDFs. Counts and quality findings in this guide are from direct structural inspection of the supplied files on 22 September 2026.' 'Roadmap Small'

    $doc.BuiltInDocumentProperties.Item('Title').Value = 'Data Preprocessing and Feature Engineering Roadmap'
    $doc.BuiltInDocumentProperties.Item('Subject').Value = 'India energy and data-centre dataset assessment'
    $doc.BuiltInDocumentProperties.Item('Author').Value = 'Codex'
    $doc.SaveAs2($outputPath, 16)
    $doc.Close($false)
    $doc = $null
    $word.Quit()
    $word = $null
    Write-Output $outputPath
}
finally {
    if ($doc -ne $null) { $doc.Close($false) }
    if ($word -ne $null) { $word.Quit() }
}
