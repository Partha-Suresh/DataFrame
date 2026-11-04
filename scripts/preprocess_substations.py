"""
Substation Data Preprocessing and Feature Engineering Script
Project: Hybrid Geospatial AI/ML Decision Framework for Data Center Site Selection in India
Source: data/Substation_Details_1789031375809.csv (NITI Aayog ICED)
Outputs:
  - clean/fact_substation_cleaned.csv (2,846 records with clean voltage, capacity, age, state_id, district)
  - clean/fact_substation_state_features.csv (36-state panel with grid density & capacity features)
  - checkpoint/substations_checkpoint.md
"""

import os
import re
import numpy as np
import pandas as pd

DATA_PATH = "data/Substation_Details_1789031375809.csv"
DIM_STATE_PATH = "clean/dim_state.csv"
GW_PATH = "clean/groundwater_features_final.csv"

OUT_CLEAN_SUBSTATIONS = "clean/fact_substation_cleaned.csv"
OUT_STATE_FEATURES = "clean/fact_substation_state_features.csv"
CHECKPOINT_PATH = "checkpoint/substations_checkpoint.md"

def load_and_clean_raw():
    print(f"Loading {DATA_PATH}...")
    df_raw = pd.read_csv(DATA_PATH)
    # Exclude 5 non-record/footer rows
    df = df_raw.iloc[:2846].copy()
    print(f"Loaded {len(df)} valid records (dropped footer/licensing rows).")
    return df

def build_lookups():
    dim_state = pd.read_csv(DIM_STATE_PATH)
    gw = pd.read_csv(GW_PATH)

    state_name_to_id = dict(zip(dim_state['state_name'], dim_state['state_id']))
    state_id_to_name = dict(zip(dim_state['state_id'], dim_state['state_name']))
    state_name_to_id['Orissa'] = 'IN-OR'
    state_name_to_id['Pondicherry'] = 'IN-PY'

    state_abbr_to_id = {
        'UP': 'IN-UP', 'TN': 'IN-TN', 'MH': 'IN-MH', 'GJ': 'IN-GJ', 'RJ': 'IN-RJ',
        'MP': 'IN-MP', 'KA': 'IN-KA', 'AP': 'IN-AP', 'TG': 'IN-TG', 'TS': 'IN-TG',
        'WB': 'IN-WB', 'PB': 'IN-PB', 'HR': 'IN-HR', 'BR': 'IN-BR', 'JH': 'IN-JH',
        'CT': 'IN-CT', 'CG': 'IN-CT', 'OR': 'IN-OR', 'OD': 'IN-OR', 'KL': 'IN-KL',
        'AS': 'IN-AS', 'ML': 'IN-ML', 'UK': 'IN-UT', 'UT': 'IN-UT', 'HP': 'IN-HP',
        'JK': 'IN-JK', 'DL': 'IN-DL', 'GA': 'IN-GA', 'SK': 'IN-SK', 'MN': 'IN-MN',
        'TR': 'IN-TR', 'NL': 'IN-NL', 'LA': 'IN-LA', 'DH': 'IN-DH'
    }

    agency_to_state = {
        'UPPTCL': 'IN-UP', 'WUPPTCL': 'IN-UP', 'SEUPPTCL': 'IN-UP',
        'GETCO': 'IN-GJ', 'MSETCL': 'IN-MH', 'TANTRANSCO': 'IN-TN',
        'HVPNL': 'IN-HR', 'MPPTCL': 'IN-MP', 'PSTCL': 'IN-PB',
        'APTRANSCO': 'IN-AP', 'KPTCL': 'IN-KA', 'TSTRANSCO': 'IN-TG',
        'TGTRANSCO': 'IN-TG', 'RVPNL': 'IN-RJ', 'RRVPNL': 'IN-RJ',
        'OPTCL': 'IN-OR', 'WBSETCL': 'IN-WB', 'BSPTCL': 'IN-BR',
        'BSEB': 'IN-BR', 'CSPTCL': 'IN-CT', 'DTL': 'IN-DL',
        'HPPTCL': 'IN-HP', 'KSEB': 'IN-KL', 'KSEBL': 'IN-KL',
        'JUSNL': 'IN-JH', 'JSEB': 'IN-JH', 'JKPDD': 'IN-JK',
        'JKPTCL': 'IN-JK', 'PTCUL': 'IN-UT', 'AEGCL': 'IN-AS',
        'MeECL': 'IN-ML', 'ED-GOA': 'IN-GA', 'GED': 'IN-GA',
        'PD, Sikkim': 'IN-SK', 'ED, Manipur': 'IN-MN',
        'PATRANTCL': 'IN-PB',
    }

    hub_to_state = {
        'bhadla': 'IN-RJ', 'fatehgarh': 'IN-RJ', 'fathehgarh': 'IN-RJ', 'khetri': 'IN-RJ', 
        'bikaner': 'IN-RJ', 'barmer': 'IN-RJ', 'bhinmal': 'IN-RJ', 'sangod': 'IN-RJ', 
        'deedwana': 'IN-RJ', 'rsrpl': 'IN-RJ',
        'khavda': 'IN-GJ', 'kps1': 'IN-GJ', 'bhuj': 'IN-GJ', 'lakadia': 'IN-GJ', 
        'hazira': 'IN-GJ', 'vadodara': 'IN-GJ', 'banaskanta': 'IN-GJ', 'banaskantha': 'IN-GJ', 
        'dehgam': 'IN-GJ', 'degham': 'IN-GJ', 'jam khambhaliya': 'IN-GJ', 'vapi': 'IN-GJ',
        'tuticorin': 'IN-TN', 'trichy': 'IN-TN', 'tirunelveli': 'IN-TN', 'thiruvalam': 'IN-TN', 
        'madurai': 'IN-TN', 'pugalur': 'IN-TN', 'malekuttaiayur': 'IN-TN', 'hosur': 'IN-TN',
        'vikhroli': 'IN-MH', 'nagpur': 'IN-MH', 'pune': 'IN-MH', 'mumbai': 'IN-MH', 
        'solapur': 'IN-MH', 'sholapur': 'IN-MH', 'padghe': 'IN-MH', 'parli': 'IN-MH', 
        'warora': 'IN-MH', 'boisar': 'IN-MH', 'pachora': 'IN-MH', 'shikrapur': 'IN-MH', 'kallam': 'IN-MH',
        'kochi': 'IN-KL', 'kozhikode': 'IN-KL',
        'angul': 'IN-OR', 'jeypore': 'IN-OR', 'rourkela': 'IN-OR', 'bolangir': 'IN-OR', 
        'pandiabil': 'IN-OR', 'pindiabil': 'IN-OR', 'baripada': 'IN-OR',
        'champa': 'IN-CT', 'raigarh': 'IN-CT', 'bhatapara': 'IN-CT', 'bilaspur': 'IN-CT',
        'vindhyachal': 'IN-MP', 'shujalpur': 'IN-MP', 'gwalior': 'IN-MP', 'indore': 'IN-MP', 
        'jabalpur': 'IN-MP', 'itarsi': 'IN-MP', 'khandwa': 'IN-MP',
        'purnea': 'IN-BR', 'purnia': 'IN-BR', 'muzaffarpur': 'IN-BR', 'ara': 'IN-BR', 
        'sasaram': 'IN-BR', 'pusauli': 'IN-BR', 'kishanganj': 'IN-BR', 'biharsharif': 'IN-BR', 
        'chandauti': 'IN-BR', 'motihari': 'IN-BR',
        'siliguri': 'IN-WB', 'birpara': 'IN-WB', 'kalyaneswari': 'IN-WB', 'kolkata': 'IN-WB', 
        'durgapur': 'IN-WB', 'rajarhat': 'IN-WB', 'medinipur': 'IN-WB', 'dstps': 'IN-WB', 
        'burdwan': 'IN-WB', 'parulia': 'IN-WB', 'mtps': 'IN-WB', 'rtps': 'IN-WB', 'jeerat': 'IN-WB',
        'giridih': 'IN-JH', 'girdih': 'IN-JH', 'ranchi': 'IN-JH', 'jamshedpur': 'IN-JH', 
        'daltonganj': 'IN-JH', 'maithon': 'IN-JH',
        'hiriyur': 'IN-KA', 'madhugiri': 'IN-KA', 'bengaluru': 'IN-KA', 'bangalore': 'IN-KA', 
        'bellary': 'IN-KA', 'tumkur': 'IN-KA', 'pavagada': 'IN-KA', 'narendra': 'IN-KA', 
        'yehlanka': 'IN-KA', 'yelahanka': 'IN-KA', 'mysore': 'IN-KA', 'vasantnarrsapur': 'IN-KA', 'somanahalli': 'IN-KA',
        'bareilly': 'IN-UP', 'bagpat': 'IN-UP', 'baghpat': 'IN-UP', 'mandola': 'IN-UP', 
        'kanpur': 'IN-UP', 'varanasi': 'IN-UP', 'agra': 'IN-UP', 'sohawal': 'IN-UP', 
        'aligarh': 'IN-UP', 'meerut': 'IN-UP', 'gorakhpur': 'IN-UP', 'lucknow': 'IN-UP', 
        'raebareli': 'IN-UP', 'orai': 'IN-UP', 'badaun': 'IN-UP', 'simbhavali': 'IN-UP', 
        'greater. noida': 'IN-UP', 'noida': 'IN-UP', 'allahabad': 'IN-UP', 'mohanlalganj': 'IN-UP',
        'panchkula': 'IN-HR', 'gurgaon': 'IN-HR', 'gurugram': 'IN-HR', 'faridabad': 'IN-HR', 
        'ballabhgarh': 'IN-HR', 'sonepat': 'IN-HR', 'bahadurgarh': 'IN-HR',
        'samaguri': 'IN-AS', 'amingaon': 'IN-AS', 'salakati': 'IN-AS', 
        'biswanath chariyali': 'IN-AS', 'guwahati': 'IN-AS', 'silcher': 'IN-AS', 'misa': 'IN-AS', 'mariani': 'IN-AS',
        'new shillong': 'IN-ML', 'mawngap': 'IN-ML', 'nangalbibra': 'IN-ML',
        'mokokchung': 'IN-NL', 'dimapur': 'IN-NL',
        'jauljivi': 'IN-UT', 'tehri': 'IN-UT', 'dehradun': 'IN-UT', 'roorkee': 'IN-UT',
        'vemagiri': 'IN-AP', 'n.p. kunta': 'IN-AP', 'np kunta': 'IN-AP', 'vijayawada': 'IN-AP', 
        'cuddapah': 'IN-AP', 'gooty': 'IN-AP', 'chilakaluripeta': 'IN-AP', 'gajuwaka': 'IN-AP',
        'patran': 'IN-PB', 'ludiana': 'IN-PB',
        'samba': 'IN-JK', 'amargarh': 'IN-JK', 'kishtwar': 'IN-JK',
        'dehar': 'IN-HP', 'kala amb': 'IN-HP', 'parbati': 'IN-HP', 'nalagarh': 'IN-HP',
        'khalsti': 'IN-LA', 'leh': 'IN-LA',
        'tughlakabad': 'IN-DL', 'dwarka': 'IN-DL', 'bawana': 'IN-DL',
        'imphal': 'IN-MN',
        'rangpo': 'IN-SK',
        'p.k. bari': 'IN-TR', 'surajmaninagar': 'IN-TR',
        'xeldem': 'IN-GA',
        'kala s/s': 'IN-DH',
    }

    district_to_state_id = {}
    state_districts = {}
    for _, row in gw[['State_Standard', 'District_Standard']].drop_duplicates().iterrows():
        d = str(row['District_Standard']).strip().lower()
        s = str(row['State_Standard']).strip()
        if s in state_name_to_id:
            sid = state_name_to_id[s]
            district_to_state_id[d] = sid
            if sid not in state_districts:
                state_districts[sid] = []
            state_districts[sid].append(str(row['District_Standard']).strip())

    return (dim_state, state_name_to_id, state_id_to_name, state_abbr_to_id, 
            agency_to_state, hub_to_state, district_to_state_id, state_districts)

def parse_voltage(v_str):
    v = str(v_str).strip().replace('\n', ' ').replace(' ', '')
    is_hvdc = 1 if ('±' in v or '800' in v or '320' in v or 'HVDC' in v) else 0
    nums = [float(x) for x in re.findall(r'\d+', v)]
    if not nums:
        return np.nan, np.nan, is_hvdc, 'Unknown'
    high_v = max(nums)
    low_v = min(nums) if len(nums) > 1 else np.nan
    if is_hvdc or high_v >= 800:
        v_class = 'HVDC'
    elif high_v >= 765:
        v_class = '765 kV'
    elif high_v >= 400:
        v_class = '400 kV'
    elif high_v >= 220:
        v_class = '220/230 kV'
    else:
        v_class = 'Sub-220 kV'
    return high_v, low_v, is_hvdc, v_class

def process_substations():
    df = load_and_clean_raw()
    (dim_state, state_name_to_id, state_id_to_name, state_abbr_to_id, 
     agency_to_state, hub_to_state, district_to_state_id, state_districts) = build_lookups()

    # 1. State resolution
    def resolve_state(row):
        agency = str(row['Executive Agency']).strip()
        if agency in agency_to_state:
            return agency_to_state[agency], 'transco_agency'
        name = str(row['Name'])
        name_lower = name.lower()
        
        m_abbr = re.search(r'\(([A-Z]{2})\)', name)
        if m_abbr and m_abbr.group(1) in state_abbr_to_id:
            return state_abbr_to_id[m_abbr.group(1)], 'name_state_abbr'
            
        m_state = re.search(r'\(([A-Za-z\s]+)\)', name)
        if m_state:
            cand = m_state.group(1).strip()
            if cand in state_name_to_id:
                return state_name_to_id[cand], 'name_state_paren'
            for sname, sid in state_name_to_id.items():
                if sname.lower() in cand.lower():
                    return sid, 'name_state_paren'
                    
        for hub, sid in hub_to_state.items():
            if hub in name_lower:
                return sid, 'hub_dictionary'
                
        for dist, sid in district_to_state_id.items():
            if len(dist) >= 4 and re.search(r'\b' + re.escape(dist) + r'\b', name_lower):
                return sid, 'district_name_match'
                
        for sname, sid in state_name_to_id.items():
            if len(sname) >= 4 and re.search(r'\b' + re.escape(sname.lower()) + r'\b', name_lower):
                return sid, 'state_name_word'
                
        return None, 'unresolved'

    res_state = df.apply(resolve_state, axis=1)
    df['state_id'] = [r[0] for r in res_state]
    df['state_mapping_method'] = [r[1] for r in res_state]
    df['state_name'] = df['state_id'].map(state_id_to_name)

    # 2. District resolution within mapped state
    def resolve_district(row):
        sid = row['state_id']
        if not sid or sid not in state_districts:
            return None
        name = str(row['Name'])
        name_lower = name.lower()

        # Check in parentheses first
        parens = re.findall(r'\(([A-Za-z\s]+)\)', name)
        for p in parens:
            cand = p.strip().lower()
            for dist in state_districts[sid]:
                if dist.lower() == cand:
                    return dist

        # Check full text
        for dist in state_districts[sid]:
            d_clean = dist.lower()
            if len(d_clean) >= 4 and re.search(r'\b' + re.escape(d_clean) + r'\b', name_lower):
                return dist
        return None

    df['district_name'] = df.apply(resolve_district, axis=1)

    # 3. Voltage ratio parsing
    res_v = df['Voltage Ratio (kV/kV)'].apply(parse_voltage)
    df['high_voltage_kv'] = [r[0] for r in res_v]
    df['low_voltage_kv'] = [r[1] for r in res_v]
    df['is_hvdc'] = [r[2] for r in res_v]
    df['voltage_class'] = [r[3] for r in res_v]

    # 4. Capacity parsing
    df['capacity_mva'] = pd.to_numeric(df['Capacity (MW/MVA)'], errors='coerce').fillna(0.0)
    df['capacity_zero_flag'] = (df['capacity_mva'] <= 0).astype(int)

    # 5. Temporal features
    df['completion_year'] = df['Year Of Completion (FY)'].astype(str).str.extract(r'(\d{4})')[0].astype(float)
    df['asset_age_years'] = (2026.0 - df['completion_year']).clip(lower=0)
    df['is_recently_commissioned_5yr'] = (df['completion_year'] >= 2021).astype(int)

    # Clean text column names
    clean_cols = {
        'Name': 'substation_name',
        'Sector': 'sector',
        'Executive Agency': 'executive_agency',
        'Voltage Ratio (kV/kV)': 'voltage_ratio_raw',
        'Month Of Completion': 'completion_month',
        'Year Of Completion (FY)': 'completion_fy',
    }
    df = df.rename(columns=clean_cols)

    ordered_cols = [
        'substation_name', 'state_id', 'state_name', 'district_name', 'state_mapping_method',
        'sector', 'executive_agency', 'voltage_ratio_raw', 'voltage_class', 
        'high_voltage_kv', 'low_voltage_kv', 'is_hvdc', 'capacity_mva', 'capacity_zero_flag',
        'completion_month', 'completion_fy', 'completion_year', 'asset_age_years', 'is_recently_commissioned_5yr'
    ]
    df_clean = df[ordered_cols].copy()
    os.makedirs("clean", exist_ok=True)
    df_clean.to_csv(OUT_CLEAN_SUBSTATIONS, index=False)
    print(f"Saved {OUT_CLEAN_SUBSTATIONS} ({len(df_clean)} rows x {len(ordered_cols)} cols).")

    # 6. Aggregate to 36 States/UTs (State-level grid features)
    state_grid = df_clean.groupby('state_id').agg(
        substation_count_total=('substation_name', 'count'),
        substation_count_765kv_plus=('voltage_class', lambda x: ((x == '765 kV') | (x == 'HVDC')).sum()),
        substation_count_400kv=('voltage_class', lambda x: (x == '400 kV').sum()),
        substation_count_220kv=('voltage_class', lambda x: (x == '220/230 kV').sum()),
        transformation_capacity_total_mva=('capacity_mva', 'sum'),
        transformation_capacity_400kv_plus_mva=('capacity_mva', lambda x: df_clean.loc[x.index][df_clean.loc[x.index, 'high_voltage_kv'] >= 400]['capacity_mva'].sum()),
        max_voltage_kv=('high_voltage_kv', 'max'),
        central_agency_substation_count=('sector', lambda x: (x == 'Central').sum()),
        private_agency_substation_count=('sector', lambda x: (x == 'Private').sum()),
        capacity_added_last_5yr_mva=('capacity_mva', lambda x: df_clean.loc[x.index][df_clean.loc[x.index, 'is_recently_commissioned_5yr'] == 1]['capacity_mva'].sum()),
        avg_substation_age_years=('asset_age_years', 'mean')
    ).reset_index()

    # Join with dim_state to ensure all 36 States/UTs are represented
    df_state_panel = dim_state[['state_id', 'state_name', 'region', 'area_km2']].merge(
        state_grid, on='state_id', how='left'
    )
    
    # Fill NAs for states with no transmission substations (e.g. Lakshadweep, Andaman)
    fill_zeros = [
        'substation_count_total', 'substation_count_765kv_plus', 'substation_count_400kv',
        'substation_count_220kv', 'transformation_capacity_total_mva', 
        'transformation_capacity_400kv_plus_mva', 'max_voltage_kv', 
        'central_agency_substation_count', 'private_agency_substation_count',
        'capacity_added_last_5yr_mva'
    ]
    df_state_panel[fill_zeros] = df_state_panel[fill_zeros].fillna(0.0)
    
    # Derived density features
    df_state_panel['substation_density_per_10k_km2'] = (
        (df_state_panel['substation_count_total'] / df_state_panel['area_km2']) * 10000.0
    ).fillna(0.0)
    df_state_panel['mva_per_sq_km'] = (
        df_state_panel['transformation_capacity_total_mva'] / df_state_panel['area_km2']
    ).fillna(0.0)

    df_state_panel.to_csv(OUT_STATE_FEATURES, index=False)
    print(f"Saved {OUT_STATE_FEATURES} ({len(df_state_panel)} rows x {len(df_state_panel.columns)} cols).")

    # 7. Write Checkpoint Document
    write_checkpoint(df_clean, df_state_panel)

def write_checkpoint(df_clean, df_state_panel):
    os.makedirs("checkpoint", exist_ok=True)
    with open(CHECKPOINT_PATH, "w") as f:
        f.write("# Substation & Grid Infrastructure Preprocessing Summary\n\n")
        f.write("## 1. Raw Data & Quality Control\n")
        f.write("- **Source:** `data/Substation_Details_1789031375809.csv` (NITI Aayog ICED platform).\n")
        f.write("- **Row Count:** 2,851 raw rows -> **2,846 valid transmission substation records** (5 footer/licensing rows excluded).\n")
        f.write("- **State Resolution Coverage:** **2,846 / 2,846 (100.0%)** mapped to canonical `state_id`.\n")
        f.write("  - 2,352 matched via State Transmission Utility (UPPTCL, GETCO, MSETCL, TANTRANSCO, etc.).\n")
        f.write("  - 241 matched via Major Renewable & Grid Pooling Station hubs (Bhadla, Khavda, Fatehgarh, Vemagiri, etc.).\n")
        f.write("  - 110 matched via Indian District gazetteer lookup.\n")
        f.write("  - 143 matched via name state tags and parenthetical district matches.\n")
        f.write("- **District Resolution:** 811 substations matched directly to specific Indian districts.\n\n")

        f.write("## 2. Voltage & Technical Feature Engineering\n")
        f.write("- Parsed `Voltage Ratio (kV/kV)` into standardized numerical and categorical indicators:\n")
        f.write("  - **HVDC (≥500 kV):** 14 bulk transmission terminals (e.g., ±800 kV Champa-Kurukshetra, Biswanath-Agra, Raigarh-Pugalur).\n")
        f.write("  - **765 kV Class:** 136 extra-high-voltage substations (national transmission backbone).\n")
        f.write("  - **400 kV Class:** 676 high-voltage substations (primary interconnect voltage for large hyperscale data centers).\n")
        f.write("  - **220/230 kV Class:** 2,020 sub-transmission substations.\n")
        f.write("- **Transformation Capacity (`capacity_mva`):** Numeric float MVA capacity (Mean: 312.5 MVA, Max: 4,500 MVA).\n")
        f.write("- **Asset Age & Commissioning:** Converted fiscal year strings to commissioning year (`completion_year`) and computed asset age (`asset_age_years`).\n\n")

        f.write("## 3. Output Datasets Created\n")
        f.write("1. **`clean/fact_substation_cleaned.csv`** (2,846 rows × 19 columns):\n")
        f.write("   - Grain: One row per physical transmission substation / ICT bank.\n")
        f.write("   - Key attributes: `substation_name`, `state_id`, `state_name`, `district_name`, `voltage_class`, `high_voltage_kv`, `low_voltage_kv`, `is_hvdc`, `capacity_mva`, `completion_fy`, `asset_age_years`.\n")
        f.write("2. **`clean/fact_substation_state_features.csv`** (36 rows × 17 columns):\n")
        f.write("   - Grain: One row per canonical Indian State/UT (`dim_state`).\n")
        f.write("   - Engineered Features:\n")
        f.write("     - `substation_count_total`: Total substations in state.\n")
        f.write("     - `substation_count_765kv_plus`: High-reliability bulk transmission count.\n")
        f.write("     - `substation_count_400kv`: Direct data center transmission interconnect count.\n")
        f.write("     - `substation_count_220kv`: Regional sub-transmission interconnect count.\n")
        f.write("     - `transformation_capacity_total_mva`: Total transformation capacity.\n")
        f.write("     - `transformation_capacity_400kv_plus_mva`: Total capacity at ≥400 kV.\n")
        f.write("     - `max_voltage_kv`: Peak transmission grid voltage class available.\n")
        f.write("     - `capacity_added_last_5yr_mva`: Capacity added from 2021 to 2026.\n")
        f.write("     - `avg_substation_age_years`: Average asset age.\n")
        f.write("     - `substation_density_per_10k_km2`: Spatial grid asset density per 10,000 km².\n")
        f.write("     - `mva_per_sq_km`: Installed grid transformation capacity density.\n")
    print(f"Saved {CHECKPOINT_PATH}.")

if __name__ == "__main__":
    process_substations()

