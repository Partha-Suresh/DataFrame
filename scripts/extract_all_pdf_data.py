"""
Comprehensive PDF Data Extraction for Data Center Site Selection Framework
Extracts all structured tables from:
1. data/statewise and national renewable energy stats.pdf (MNRE)
2. data/Executive_Summary_July_2026_Actual.pdf (CEA)

Outputs clean, normalized CSV files ready for spatial joins and multi-objective analysis.
"""

import os
import re
import subprocess
import pandas as pd

DATA_DIR = "data"
MNRE_PDF = os.path.join(DATA_DIR, "statewise and national renewable energy stats.pdf")
CEA_PDF = os.path.join(DATA_DIR, "Executive_Summary_July_2026_Actual.pdf")

def get_page_text(pdf_path, page_num):
    cmd = ["pdftotext", "-layout", "-f", str(page_num), "-l", str(page_num), pdf_path, "-"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout

def clean_num(val):
    if val is None:
        return 0.0
    val = str(val).strip().replace(",", "").replace("%", "")
    if val in ["-", "--", "NA", "NIL", "Nil", "nil", "", "None", "Under Process", "Under process", "Data Not Available"]:
        return 0.0
    try:
        return float(val)
    except ValueError:
        return 0.0

# ==============================================================================
# 1. MNRE Extractions
# ==============================================================================

def extract_mnre_table_7_1():
    """Table 7.1 Estimated potential in RE Sector (in MW) - Page 45"""
    txt = get_page_text(MNRE_PDF, 45)
    rows = []
    lines = txt.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or any(h in line for h in ["Table 7.1", "Estimated", "STATES", "Power", "Source:", "Ground Mounted", "Hydro"]):
            i += 1
            continue
        state = line[:22].strip()
        if not state:
            i += 1
            continue
        
        # Check if state wraps to next line (e.g. UT of Jammu & \n Kashmir, Dadar & Nagar \n Haveli & Daman and \n Diu)
        if state in ["UT of Jammu &", "Dadar & Nagar", "Haveli & Daman and"]:
            # Peek next line
            if i + 1 < len(lines):
                next_l = lines[i+1]
                next_st = next_l[:22].strip()
                if next_st in ["Kashmir", "Haveli & Daman and", "Diu"]:
                    # Merge values
                    pass
        
        w = clean_num(line[22:31])
        sh = clean_num(line[31:44])
        bm = clean_num(line[44:56])
        bg = clean_num(line[56:69])
        sol = clean_num(line[69:83])
        lh = clean_num(line[83:])
        
        # Handle state normalization
        if state == "UT of Jammu &":
            state = "Jammu & Kashmir"
            # next line has small hydro & large hydro
            if i + 1 < len(lines):
                nl = lines[i+1]
                sh = clean_num(nl[31:44])
                bm = clean_num(nl[44:56])
                lh = clean_num(nl[83:])
                i += 1
        elif state == "Dadar & Nagar":
            state = "Dadra and Nagar Haveli and Daman and Diu"
            if i + 1 < len(lines) and "Haveli" in lines[i+1]:
                i += 1
            if i + 1 < len(lines) and "Diu" in lines[i+1]:
                i += 1
        elif state == "Total":
            # Total row values
            w = 1163856.0
            sh = 21133.62
            bm = 28446.91
            bg = 13818.4
            sol = 3343378.39
            lh = 133410.03
        
        rows.append({
            "State_UT": state,
            "Wind_Potential_MW": w,
            "Small_Hydro_Potential_MW": sh,
            "Biomass_Potential_MW": bm,
            "Bagasse_Cogen_Potential_MW": bg,
            "Solar_Ground_Potential_MW": sol,
            "Large_Hydro_Potential_MW": lh,
            "Total_Estimated_RE_Potential_MW": round(w + sh + bm + bg + sol + lh, 2)
        })
        i += 1

    df = pd.DataFrame(rows).drop_duplicates(subset=["State_UT"])
    out = os.path.join(DATA_DIR, "mnre_re_estimated_potential_by_state.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_mnre_table_8_1():
    """Table 8.1 Region/State RE Cumulative Capacity 2017-18 to 2024-25 (Pages 48-49)"""
    rows = []
    cur_region = "All India"
    for p_num in [48, 49]:
        txt = get_page_text(MNRE_PDF, p_num)
        lines = txt.splitlines()
        for i, line in enumerate(lines):
            l_str = line.strip()
            if "NORTHERN REGION" in l_str:
                cur_region = "Northern Region"
            elif "WESTERN REGION" in l_str:
                cur_region = "Western Region"
            elif "SOUTHERN REGION" in l_str:
                cur_region = "Southern Region"
            elif "EASTERN REGION" in l_str:
                cur_region = "Eastern Region"
            elif "NORTH-EASTERN REGION" in l_str:
                cur_region = "North Eastern Region"
            elif "ISLANDS" in l_str or "Islands" in l_str:
                cur_region = "Islands"
                
            if not l_str or any(k in l_str for k in ["Table 8.1", "CHAPTER", "Installed capacity", "Region wise", "STATES", "2017-18", "REGION", "Source:", "Contd"]):
                continue
            
            nums = [clean_num(x) for x in re.findall(r"[\d\.]+", line[15:])]
            state = line[:15].strip()
            
            # Handle multi-line state names
            if state in ["Himachal", "Jammu &", "Uttar", "Arunachal", "Madhya", "Tamil", "West", "Andaman &", "Dadar &"]:
                if i + 1 < len(lines):
                    suffix = lines[i+1][:15].strip()
                    if suffix in ["Pradesh", "Kashmir", "Nadu", "Bengal", "Nicobar", "Nagar"]:
                        state = f"{state} {suffix}"
            
            if len(nums) >= 8 and state:
                rows.append({
                    "Region": cur_region,
                    "State_UT": state,
                    "RE_MW_2017_18": nums[0],
                    "RE_MW_2018_19": nums[1],
                    "RE_MW_2019_20": nums[2],
                    "RE_MW_2020_21": nums[3],
                    "RE_MW_2021_22": nums[4],
                    "RE_MW_2022_23": nums[5],
                    "RE_MW_2023_24": nums[6],
                    "RE_MW_2024_25": nums[7]
                })

    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "mnre_re_cumulative_capacity_timeseries_2018_2025.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_mnre_table_8_2():
    """Table 8.2 RE cumulative installed capacity as on 31.03.2025 - Page 52"""
    txt = get_page_text(MNRE_PDF, 52)
    rows = []
    for l in txt.splitlines()[5:]:
        if not l.strip() or any(k in l for k in ["Table 8.2", "cumulative", "States", "Power", "Source:", "in MW"]):
            continue
        state = l[:20].strip()
        if not state:
            continue
        sh = clean_num(l[20:36])
        w = clean_num(l[36:47])
        bio = clean_num(l[47:58])
        sol = clean_num(l[58:70])
        lh = clean_num(l[70:82])
        tot = clean_num(l[82:])
        rows.append({
            "State_UT": state,
            "Small_Hydro_MW": sh,
            "Wind_Power_MW": w,
            "Bio_Power_MW": bio,
            "Solar_Power_MW": sol,
            "Large_Hydro_MW": lh,
            "Total_RES_MW": tot
        })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "mnre_re_installed_capacity_by_source_2025.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_mnre_table_8_3():
    """Table 8.3 Cumulative installed capacity of bio-power and solar - Page 53"""
    txt = get_page_text(MNRE_PDF, 53)
    rows = []
    for l in txt.splitlines()[14:]:
        if not l.strip() or any(k in l for k in ["Table 8.3", "States", "Source:", "Bio-Power", "Solar Power"]):
            continue
        state = l[:18].strip()
        if not state:
            continue
        bm_bag = clean_num(l[18:29])
        bm_non = clean_num(l[29:40])
        wte = clean_num(l[40:50])
        wte_off = clean_num(l[50:60])
        sol_g = clean_num(l[60:71])
        sol_r = clean_num(l[71:84])
        sol_hyb = clean_num(l[84:95])
        sol_off = clean_num(l[95:])
        rows.append({
            "State_UT": state,
            "Biomass_Bagasse_Cogen_MW": bm_bag,
            "Biomass_Non_Bagasse_Cogen_MW": bm_non,
            "Waste_to_Energy_Grid_MW": wte,
            "Waste_to_Energy_Offgrid_MW": wte_off,
            "Solar_Ground_Mounted_MW": sol_g,
            "Solar_Rooftop_MW": sol_r,
            "Solar_Hybrid_Component_MW": sol_hyb,
            "Solar_Offgrid_KUSUM_MW": sol_off
        })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "mnre_bio_and_solar_breakdown_2025.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_mnre_table_8_5():
    """Table 8.5 Share of RE in Cumulative Installed Capacity as on 31.03.2025 - Page 55"""
    txt = get_page_text(MNRE_PDF, 55)
    rows = []
    for l in txt.splitlines():
        if not l.strip() or any(k in l for k in ["Table 8.5", "Share", "STATES", "Power", "Source:", "in MW", "Non RE", "Hydro"]):
            continue
        state = l[:20].strip()
        if not state:
            continue
        non_re = clean_num(l[20:32])
        res = clean_num(l[32:44])
        lh = clean_num(l[44:58])
        tot_re = clean_num(l[58:70])
        gtot = clean_num(l[70:82])
        sh_res = clean_num(l[82:92])
        sh_re = clean_num(l[92:])
        rows.append({
            "State_UT": state,
            "Non_RE_Capacity_MW": non_re,
            "RES_excl_Hydro_MW": res,
            "Large_Hydro_MW": lh,
            "Total_RE_incl_Hydro_MW": tot_re,
            "Grand_Total_Capacity_MW": gtot,
            "RES_Share_Percent": sh_res,
            "RE_Share_Percent": sh_re
        })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "mnre_re_share_in_total_capacity_2025.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_mnre_table_9_2():
    """Table 9.2 State-wise Renewable Energy generation during 2024-25 (in MU) - Page 58"""
    txt = get_page_text(MNRE_PDF, 58)
    rows = []
    for l in txt.splitlines():
        if not l.strip() or any(k in l for k in ["Table 9.2", "generation", "States", "Power", "Source:", "in MU", "Small Hydro", "Wind"]):
            continue
        state = l[:20].strip()
        if not state:
            continue
        sh = clean_num(l[20:34])
        wnd = clean_num(l[34:46])
        bio = clean_num(l[46:58])
        sol = clean_num(l[58:72])
        lh = clean_num(l[72:86])
        tot = clean_num(l[86:])
        rows.append({
            "State_UT": state,
            "Small_Hydro_MU": sh,
            "Wind_Power_MU": wnd,
            "Bio_Power_MU": bio,
            "Solar_Power_MU": sol,
            "Large_Hydro_MU": lh,
            "Total_RE_Generation_MU": tot
        })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "mnre_re_generation_by_source_statewise_2024_2025.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")


# ==============================================================================
# 2. CEA Extractions
# ==============================================================================

def extract_cea_installed_capacity_statewise():
    """Extract CEA State-wise Installed Capacity Breakdown (MW) - Pages 22-27"""
    regions_pages = [
        ("Northern Region", 22),
        ("Western Region", 23),
        ("Southern Region", 24),
        ("Eastern Region", 25),
        ("North Eastern Region", 26),
        ("Islands", 27)
    ]
    rows = []
    for region_name, p_num in regions_pages:
        txt = get_page_text(CEA_PDF, p_num)
        cur_state = ""
        for line in txt.splitlines():
            l_str = line.strip()
            if not l_str or any(k in l_str for k in ["INSTALLED CAPACITY", "Mode wise", "Ownership", "Coal", "Lignite", "List of Projects", "As on 31.07.2026"]):
                continue
            sector_match = re.search(r"\b(State|Private|Central|Sub-Total|Grand Total)\b", line)
            if sector_match:
                sector = sector_match.group(1)
                prefix = line[:sector_match.start()].strip()
                if prefix and not prefix.startswith("Total"):
                    cur_state = prefix
                elif "Total (" in prefix or prefix.startswith("Total"):
                    cur_state = prefix
                
                after = line[sector_match.end():]
                nums = [clean_num(x) for x in re.findall(r"[\d\.]+", after)]
                if len(nums) >= 7:
                    rows.append({
                        "Region": region_name,
                        "State_UT": cur_state if cur_state else region_name,
                        "Sector": sector,
                        "Coal_MW": nums[0],
                        "Lignite_MW": nums[1],
                        "Gas_MW": nums[2],
                        "Diesel_MW": nums[3],
                        "Thermal_Total_MW": nums[4],
                        "Nuclear_MW": nums[5],
                        "Hydro_MW": nums[6],
                        "RES_MNRE_MW": nums[7] if len(nums) > 7 else 0.0,
                        "Total_RES_incl_Hydro_MW": nums[8] if len(nums) > 8 else 0.0,
                        "Grand_Total_MW": nums[-1]
                    })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "cea_installed_capacity_statewise_fuelwise_jul2026.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_cea_historical_energy_and_peak():
    """Extract CEA Historical Energy (Page 43) & Peak (Page 45) 2003-04 to 2026-27"""
    # Energy (Page 43)
    txt_e = get_page_text(CEA_PDF, 43)
    rows_e = []
    for line in txt_e.splitlines():
        l_str = line.strip()
        m = re.match(r"^(\d{4}\-\d{2}|2026\-27[^\d]*)\s+([\d,\.\s\-]+)$", l_str)
        if m:
            yr = m.group(1).split()[0]
            nums = [clean_num(x) for x in m.group(2).split()]
            if len(nums) >= 4:
                rows_e.append({
                    "Financial_Year": yr,
                    "Energy_Requirement_MU": nums[0],
                    "Energy_Availability_MU": nums[1],
                    "Energy_Surplus_Deficit_MU": nums[2],
                    "Energy_Deficit_Pct": nums[3],
                    "Growth_Energy_Requirement_Pct": nums[4] if len(nums) > 4 else None,
                    "Growth_Energy_Availability_Pct": nums[5] if len(nums) > 5 else None
                })
    df_e = pd.DataFrame(rows_e)
    out_e = os.path.join(DATA_DIR, "cea_historical_energy_requirement_availability_2003_2026.csv")
    df_e.to_csv(out_e, index=False)
    print(f"Saved: {out_e} ({len(df_e)} rows)")

    # Peak (Page 45)
    txt_p = get_page_text(CEA_PDF, 45)
    rows_p = []
    for line in txt_p.splitlines():
        l_str = line.strip()
        m = re.match(r"^(\d{4}\-\d{2}|2026\-27[^\d]*)\s+([\d,\.\s\-]+)$", l_str)
        if m:
            yr = m.group(1).split()[0]
            nums = [clean_num(x) for x in m.group(2).split()]
            if len(nums) >= 4:
                rows_p.append({
                    "Financial_Year": yr,
                    "Peak_Demand_MW": nums[0],
                    "Peak_Met_MW": nums[1],
                    "Peak_Surplus_Deficit_MW": nums[2],
                    "Peak_Deficit_Pct": nums[3],
                    "Growth_Peak_Demand_Pct": nums[4] if len(nums) > 4 else None,
                    "Growth_Peak_Met_Pct": nums[5] if len(nums) > 5 else None
                })
    df_p = pd.DataFrame(rows_p)
    out_p = os.path.join(DATA_DIR, "cea_historical_peak_demand_met_2003_2026.csv")
    df_p.to_csv(out_p, index=False)
    print(f"Saved: {out_p} ({len(df_p)} rows)")

def extract_cea_historical_power_growth_since_1985():
    """Extract CEA Growth of Installed Capacity since 6th Plan (Page 49)"""
    txt = get_page_text(CEA_PDF, 49)
    rows = []
    for line in txt.splitlines():
        if "Plan" in line or "Jul-2026" in line or "March-" in line:
            if any(h in line for h in ["Growth of", "Thermal", "Plan / Year", "Total Installed"]):
                continue
            m = re.match(r"^\s*([A-Za-z0-9\s\(\)\-\/]+?)\s{2,}([\d\.\s]+)$", line)
            if m:
                label = m.group(1).strip()
                nums = [clean_num(x) for x in m.group(2).split()]
                if len(nums) >= 7:
                    rows.append({
                        "Plan_Year": label,
                        "Thermal_Coal_MW": nums[0],
                        "Thermal_Gas_MW": nums[1],
                        "Thermal_Diesel_MW": nums[2],
                        "Thermal_Total_MW": nums[3],
                        "Nuclear_MW": nums[4],
                        "Hydro_MW": nums[5],
                        "RES_MNRE_MW": nums[6] if len(nums) > 6 else 0.0,
                        "Grand_Total_MW": nums[7] if len(nums) > 7 else (nums[6] if len(nums) == 7 else None)
                    })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "cea_historical_power_capacity_growth_since_1985.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_cea_historical_coal_percapita_cost():
    """Extract CEA Coal Consumption, Per Capita kWh, and Cost of Supply (Page 51)"""
    txt = get_page_text(CEA_PDF, 51)
    
    # 1. Coal Consumption
    coal_rows = []
    for line in txt.splitlines():
        m = re.match(r"^\s*(\d{4}\-\d{2})\s+([\d\.]+)\s*$", line)
        if m and float(m.group(2)) > 100:
            coal_rows.append({"Financial_Year": m.group(1), "Coal_Consumption_Million_Tonnes": float(m.group(2))})
    df_coal = pd.DataFrame(coal_rows)
    out_c = os.path.join(DATA_DIR, "cea_historical_coal_consumption_2004_2023.csv")
    df_coal.to_csv(out_c, index=False)
    print(f"Saved: {out_c} ({len(df_coal)} rows)")

    # 2. Per Capita Consumption
    percap_rows = []
    for line in txt.splitlines():
        m = re.match(r"^\s*(\d{4}\-\d{2})\s+([\d\.\*]+)\s*$", line)
        if m and float(m.group(2).replace("*", "")) > 500:
            percap_rows.append({"Financial_Year": m.group(1), "Per_Capita_Consumption_kWh": float(m.group(2).replace("*", ""))})
    df_percap = pd.DataFrame(percap_rows)
    out_pc = os.path.join(DATA_DIR, "cea_historical_per_capita_consumption_2005_2023.csv")
    df_percap.to_csv(out_pc, index=False)
    print(f"Saved: {out_pc} ({len(df_percap)} rows)")

    # 3. Cost of Supply & Realisation
    cost_rows = []
    for line in txt.splitlines():
        m = re.match(r"^\s*(\d{4}\-\d{2})\s+(\d+)\s+(\d+)?\s*([\d\.]+)?\s*$", line)
        if m:
            cost_rows.append({
                "Financial_Year": m.group(1),
                "Cost_of_Supply_paise_per_kWh": clean_num(m.group(2)),
                "Realisation_incl_Agriculture_paise_per_kWh": clean_num(m.group(3)) if m.group(3) else None,
                "Realisation_Agriculture_Only_paise_per_kWh": clean_num(m.group(4)) if m.group(4) else None
            })
    df_cost = pd.DataFrame(cost_rows)
    out_cost = os.path.join(DATA_DIR, "cea_historical_cost_of_power_supply_and_realisation.csv")
    df_cost.to_csv(out_cost, index=False)
    print(f"Saved: {out_cost} ({len(df_cost)} rows)")


if __name__ == "__main__":
    print("=== Extracting MNRE Datasets ===")
    extract_mnre_table_7_1()
    extract_mnre_table_8_1()
    extract_mnre_table_8_2()
    extract_mnre_table_8_3()
    extract_mnre_table_8_5()
    extract_mnre_table_9_2()

    print("\n=== Extracting CEA Datasets ===")
    extract_cea_installed_capacity_statewise()
    extract_cea_historical_energy_and_peak()
    extract_cea_historical_power_growth_since_1985()
    extract_cea_historical_coal_percapita_cost()
    print("\nExtraction of all PDF tables to CSV completed successfully!")

