"""
PDF Data Extraction Script for Data Center Site Selection Framework
Extracts structured tables from:
1. data/statewise and national renewable energy stats.pdf (MNRE)
2. data/Executive_Summary_July_2026_Actual.pdf (CEA)
Saves extracted tables as standardized CSV files in data/
"""

import subprocess
import re
import os
import pandas as pd

DATA_DIR = "data"

def get_page_text(pdf_path, page_num):
    cmd = ["pdftotext", "-layout", "-f", str(page_num), "-l", str(page_num), pdf_path, "-"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout

def clean_num(val):
    if val is None:
        return 0.0
    val = str(val).strip().replace(",", "").replace("%", "")
    if val in ["-", "--", "NA", "NIL", "Nil", "nil", "", "None"]:
        return 0.0
    try:
        return float(val)
    except ValueError:
        return val

# -------------------------------------------------------------
# MNRE Extractions
# -------------------------------------------------------------
MNRE_PDF = os.path.join(DATA_DIR, "statewise and national renewable energy stats.pdf")

def extract_mnre_table_7_1():
    """Table 7.1 Estimated potential in RE Sector (in MW) - Page 45"""
    text = get_page_text(MNRE_PDF, 45)
    lines = text.splitlines()
    rows = []
    start_parsing = False
    
    for line in lines:
        if "Andhra Pradesh" in line:
            start_parsing = True
        if "Total" in line and start_parsing:
            parts = line.strip().split()
            rows.append({
                "State_UT": "Total",
                "Wind_Power_MW": clean_num(parts[1]),
                "Small_Hydro_MW": clean_num(parts[2]),
                "Biomass_Power_MW": clean_num(parts[3]),
                "Bagasse_Cogeneration_MW": clean_num(parts[4]),
                "Solar_Power_Ground_MW": clean_num(parts[5]),
                "Large_Hydro_MW": clean_num(parts[6]) if len(parts) > 6 else 0.0
            })
            break
        if start_parsing and line.strip():
            if "Ground Mounted" in line or "Source:" in line or "Table" in line:
                continue
            state = line[:20].strip()
            if not state:
                continue
            p_wind = clean_num(line[20:34])
            p_sh = clean_num(line[34:46])
            p_bio = clean_num(line[46:58])
            p_bag = clean_num(line[58:72])
            p_sol = clean_num(line[72:86])
            p_lh = clean_num(line[86:])
            
            rows.append({
                "State_UT": state,
                "Wind_Power_MW": p_wind,
                "Small_Hydro_MW": p_sh,
                "Biomass_Power_MW": p_bio,
                "Bagasse_Cogeneration_MW": p_bag,
                "Solar_Power_Ground_MW": p_sol,
                "Large_Hydro_MW": p_lh
            })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "mnre_re_estimated_potential_by_state.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_mnre_table_8_2():
    """Table 8.2 RE cumulative installed capacity as on 31.03.2025 - Page 52"""
    text = get_page_text(MNRE_PDF, 52)
    lines = text.splitlines()
    rows = []
    start = False
    for line in lines:
        if "Andhra Pradesh" in line:
            start = True
        if "Total" in line and start:
            p_sh = clean_num(line[22:36])
            p_wind = clean_num(line[36:48])
            p_bio = clean_num(line[48:60])
            p_sol_g = clean_num(line[60:74])
            p_sol_r = clean_num(line[74:86])
            p_tot_re = clean_num(line[86:100])
            p_tot_res = clean_num(line[100:])
            rows.append({
                "State_UT": "Total",
                "Small_Hydro_MW": p_sh,
                "Wind_Power_MW": p_wind,
                "Bio_Power_MW": p_bio,
                "Solar_Ground_Mounted_MW": p_sol_g,
                "Solar_Roof_Top_MW": p_sol_r,
                "Total_RE_MW": p_tot_re,
                "Total_RES_incl_Large_Hydro_MW": p_tot_res
            })
            break
        if start and line.strip():
            if "Source:" in line or "Table" in line or "States" in line:
                continue
            state = line[:22].strip()
            if not state:
                continue
            p_sh = clean_num(line[22:36])
            p_wind = clean_num(line[36:48])
            p_bio = clean_num(line[48:60])
            p_sol_g = clean_num(line[60:74])
            p_sol_r = clean_num(line[74:86])
            p_tot_re = clean_num(line[86:100])
            p_tot_res = clean_num(line[100:])
            rows.append({
                "State_UT": state,
                "Small_Hydro_MW": p_sh,
                "Wind_Power_MW": p_wind,
                "Bio_Power_MW": p_bio,
                "Solar_Ground_Mounted_MW": p_sol_g,
                "Solar_Roof_Top_MW": p_sol_r,
                "Total_RE_MW": p_tot_re,
                "Total_RES_incl_Large_Hydro_MW": p_tot_res
            })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "mnre_re_installed_capacity_by_source_2025.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_mnre_table_8_5():
    """Table 8.5 Share of RE in Cumulative Installed Capacity as on 31.03.2025 - Page 55"""
    text = get_page_text(MNRE_PDF, 55)
    lines = text.splitlines()
    rows = []
    start = False
    for line in lines:
        if "Andhra Pradesh" in line:
            start = True
        if "Total" in line and start:
            p_non_re = clean_num(line[20:34])
            p_re = clean_num(line[34:46])
            p_lh = clean_num(line[46:60])
            p_res = clean_num(line[60:74])
            p_tot = clean_num(line[74:88])
            p_sh_re = clean_num(line[88:98])
            p_sh_res = clean_num(line[98:])
            rows.append({
                "State_UT": "Total",
                "Non_RE_Capacity_MW": p_non_re,
                "RE_Capacity_MW": p_re,
                "Large_Hydro_Capacity_MW": p_lh,
                "Total_RES_MW": p_res,
                "Grand_Total_Capacity_MW": p_tot,
                "RE_Share_Percent": p_sh_re,
                "RES_incl_Hydro_Share_Percent": p_sh_res
            })
            break
        if start and line.strip():
            if "Source:" in line or "Table" in line or "States" in line:
                continue
            state = line[:20].strip()
            if not state:
                continue
            p_non_re = clean_num(line[20:34])
            p_re = clean_num(line[34:46])
            p_lh = clean_num(line[46:60])
            p_res = clean_num(line[60:74])
            p_tot = clean_num(line[74:88])
            p_sh_re = clean_num(line[88:98])
            p_sh_res = clean_num(line[98:])
            rows.append({
                "State_UT": state,
                "Non_RE_Capacity_MW": p_non_re,
                "RE_Capacity_MW": p_re,
                "Large_Hydro_Capacity_MW": p_lh,
                "Total_RES_MW": p_res,
                "Grand_Total_Capacity_MW": p_tot,
                "RE_Share_Percent": p_sh_re,
                "RES_incl_Hydro_Share_Percent": p_sh_res
            })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "mnre_re_share_in_total_capacity_2025.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_mnre_table_9_2():
    """Table 9.2 State-wise Renewable Energy generation during 2024-25 (in MU) - Page 58"""
    text = get_page_text(MNRE_PDF, 58)
    lines = text.splitlines()
    rows = []
    start = False
    for line in lines:
        if "Andhra Pradesh" in line:
            start = True
        if "Total" in line and start:
            p_sh = clean_num(line[20:34])
            p_wind = clean_num(line[34:46])
            p_bio = clean_num(line[46:58])
            p_sol = clean_num(line[58:72])
            p_lh = clean_num(line[72:86])
            p_tot = clean_num(line[86:])
            rows.append({
                "State_UT": "Total",
                "Small_Hydro_MU": p_sh,
                "Wind_Power_MU": p_wind,
                "Bio_Power_MU": p_bio,
                "Solar_Power_MU": p_sol,
                "Large_Hydro_MU": p_lh,
                "Total_RE_Generation_MU": p_tot
            })
            break
        if start and line.strip():
            if "Source:" in line or "Table" in line or "States" in line:
                continue
            state = line[:20].strip()
            if not state:
                continue
            p_sh = clean_num(line[20:34])
            p_wind = clean_num(line[34:46])
            p_bio = clean_num(line[46:58])
            p_sol = clean_num(line[58:72])
            p_lh = clean_num(line[72:86])
            p_tot = clean_num(line[86:])
            rows.append({
                "State_UT": state,
                "Small_Hydro_MU": p_sh,
                "Wind_Power_MU": p_wind,
                "Bio_Power_MU": p_bio,
                "Solar_Power_MU": p_sol,
                "Large_Hydro_MU": p_lh,
                "Total_RE_Generation_MU": p_tot
            })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "mnre_re_generation_by_source_statewise_2024_2025.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_mnre_table_8_1():
    """Table 8.1 Region wise/State wise RE Cumulative Installed Capacity 2017-18 to 2024-25 (MW) - Pages 48-49"""
    rows = []
    current_region = "All India"
    for page in [48, 49]:
        text = get_page_text(MNRE_PDF, page)
        lines = text.splitlines()
        start = False
        for line in lines:
            if "Chandigarh" in line or "Andhra Pradesh" in line:
                start = True
            if "Northern Region" in line:
                current_region = "Northern Region"
            elif "Western Region" in line:
                current_region = "Western Region"
            elif "Southern Region" in line:
                current_region = "Southern Region"
            elif "Eastern Region" in line:
                current_region = "Eastern Region"
            elif "North Eastern Region" in line:
                current_region = "North Eastern Region"
            elif "Islands" in line:
                current_region = "Islands"
                
            if start and line.strip():
                if "Source:" in line or "Table" in line or "Regions" in line or "States" in line or "Contd" in line:
                    continue
                state = line[:22].strip()
                if not state or state.startswith("Table") or "Region" in state:
                    continue
                nums = [clean_num(x) for x in re.findall(r"[\d\.\-]+", line[22:])]
                if len(nums) >= 8:
                    rows.append({
                        "Region": current_region,
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


# -------------------------------------------------------------
# CEA Extractions
# -------------------------------------------------------------
CEA_PDF = os.path.join(DATA_DIR, "Executive_Summary_July_2026_Actual.pdf")

def extract_cea_installed_capacity_statewise():
    """Extract CEA State-wise & Fuel-wise Installed Capacity (MW) - Pages 22-27"""
    regions = [
        ("Northern Region", 22),
        ("Western Region", 23),
        ("Southern Region", 24),
        ("Eastern Region", 25),
        ("North Eastern Region", 26),
        ("Islands", 27)
    ]
    rows = []
    for region_name, page_num in regions:
        text = get_page_text(CEA_PDF, page_num)
        current_state = ""
        for line in text.splitlines():
            line_str = line.strip()
            if not line_str or "INSTALLED CAPACITY" in line or "Mode wise breakup" in line or "Ownership" in line or "Coal" in line or "List of Projects" in line:
                continue
            
            # Detect sector lines: State, Private, Central, Sub-Total, Grand Total
            sector_match = re.search(r"\b(State|Private|Central|Sub-Total|Grand Total)\b", line)
            if sector_match:
                sector = sector_match.group(1)
                prefix = line[:sector_match.start()].strip()
                if prefix and not prefix.startswith("Total"):
                    current_state = prefix
                elif "Total (" in prefix or prefix.startswith("Total"):
                    current_state = prefix
                
                # Extract numbers after sector
                after_sector = line[sector_match.end():]
                nums = [clean_num(x) for x in re.findall(r"[\d\.]+", after_sector)]
                # Columns: Coal, Lignite, Gas, Diesel, Total Thermal, Nuclear, Hydro, RES, Total RES (Hydro+RES), Grand Total
                if len(nums) >= 7:
                    rows.append({
                        "Region": region_name,
                        "State_UT": current_state if current_state else "All India",
                        "Ownership_Sector": sector,
                        "Thermal_Coal_MW": nums[0],
                        "Thermal_Lignite_MW": nums[1],
                        "Thermal_Gas_MW": nums[2],
                        "Thermal_Diesel_MW": nums[3],
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

def extract_cea_power_supply_position():
    """Extract CEA State-wise Power Supply Position (Energy & Peak) July-2026 - Pages 25-26"""
    # Look at pages 25-26 of Section F (PDF pages 25 and 26 or surrounding)
    # Let's verify exact text
    rows_energy = []
    rows_peak = []
    
    for p in range(25, 30):
        t = get_page_text(CEA_PDF, p)
        if "Energy (MU)" in t or "Energy Requirement" in t:
            cur_reg = ""
            for line in t.splitlines():
                if any(r in line for r in ["Northern Region", "Western Region", "Southern Region", "Eastern Region", "North-Eastern Region"]):
                    cur_reg = line.strip()
                m = re.match(r"^\s*([A-Za-z\s&/\.\-]+?)\s{2,}([\d\.\s\-\(\),]+)$", line)
                if m:
                    state = m.group(1).strip()
                    if any(k in state for k in ["Energy Requirement", "Surplus", "Page", "Section", "State/System", "Provisional", "Table"]):
                        continue
                    nums = [clean_num(x) for x in re.findall(r"[\-]?\d+[\d,]*\.?\d*", m.group(2))]
                    if len(nums) >= 4:
                        rows_energy.append({
                            "Region": cur_reg,
                            "State_UT": state,
                            "Jul2026_Energy_Req_MU": nums[0],
                            "Jul2026_Energy_Avail_MU": nums[1],
                            "Jul2026_Energy_Surplus_Deficit_MU": nums[2] if len(nums) > 2 else 0.0,
                            "Jul2026_Energy_Surplus_Deficit_Pct": nums[3] if len(nums) > 3 else 0.0,
                            "Apr_Jul2026_Energy_Req_MU": nums[4] if len(nums) > 4 else None,
                            "Apr_Jul2026_Energy_Avail_MU": nums[5] if len(nums) > 5 else None,
                            "Apr_Jul2026_Energy_Surplus_Deficit_Pct": nums[7] if len(nums) > 7 else (nums[6] if len(nums) > 6 else None)
                        })
                        
        if "Peak Demand" in t or "Peak (MW)" in t or "Peak Met" in t:
            cur_reg = ""
            for line in t.splitlines():
                if any(r in line for r in ["Northern Region", "Western Region", "Southern Region", "Eastern Region", "North-Eastern Region"]):
                    cur_reg = line.strip()
                m = re.match(r"^\s*([A-Za-z\s&/\.\-]+?)\s{2,}([\d\.\s\-\(\),]+)$", line)
                if m:
                    state = m.group(1).strip()
                    if any(k in state for k in ["Peak Demand", "Surplus", "Page", "Section", "State/System", "Provisional", "Table"]):
                        continue
                    nums = [clean_num(x) for x in re.findall(r"[\-]?\d+[\d,]*\.?\d*", m.group(2))]
                    if len(nums) >= 4:
                        rows_peak.append({
                            "Region": cur_reg,
                            "State_UT": state,
                            "Jul2026_Peak_Demand_MW": nums[0],
                            "Jul2026_Peak_Met_MW": nums[1],
                            "Jul2026_Peak_Surplus_Deficit_MW": nums[2] if len(nums) > 2 else 0.0,
                            "Jul2026_Peak_Surplus_Deficit_Pct": nums[3] if len(nums) > 3 else 0.0,
                            "Apr_Jul2026_Peak_Demand_MW": nums[4] if len(nums) > 4 else None,
                            "Apr_Jul2026_Peak_Met_MW": nums[5] if len(nums) > 5 else None,
                            "Apr_Jul2026_Peak_Surplus_Deficit_Pct": nums[7] if len(nums) > 7 else (nums[6] if len(nums) > 6 else None)
                        })

    if rows_energy:
        df_energy = pd.DataFrame(rows_energy)
        out_e = os.path.join(DATA_DIR, "cea_energy_supply_position_statewise_jul2026.csv")
        df_energy.to_csv(out_e, index=False)
        print(f"Saved: {out_e} ({len(df_energy)} rows)")
    if rows_peak:
        df_peak = pd.DataFrame(rows_peak)
        out_p = os.path.join(DATA_DIR, "cea_peak_supply_position_statewise_jul2026.csv")
        df_peak.to_csv(out_p, index=False)
        print(f"Saved: {out_p} ({len(df_peak)} rows)")

def extract_cea_historical_energy_and_peak():
    """Extract CEA Historical Energy & Peak Supply 2003-04 to 2026-27 - Pages 43 & 45"""
    # Page 43 is Energy
    text_e = get_page_text(CEA_PDF, 43)
    rows_e = []
    for line in text_e.splitlines():
        line_clean = line.strip()
        m = re.match(r"^(\d{4}\-\d{2}|2026\-27[^\d]*)\s+([\d,\.\s\-]+)$", line_clean)
        if m:
            yr = m.group(1).split()[0]
            nums = [clean_num(x) for x in m.group(2).split()]
            if len(nums) >= 4:
                rows_e.append({
                    "Year": yr,
                    "Energy_Requirement_MU": nums[0],
                    "Energy_Availability_MU": nums[1],
                    "Energy_Surplus_Deficit_MU": nums[2],
                    "Energy_Deficit_Pct": nums[3],
                    "Energy_Req_Growth_Pct": nums[4] if len(nums) > 4 else None,
                    "Energy_Avail_Growth_Pct": nums[5] if len(nums) > 5 else None
                })
    df_e = pd.DataFrame(rows_e)
    out_e = os.path.join(DATA_DIR, "cea_historical_energy_requirement_availability_2003_2026.csv")
    df_e.to_csv(out_e, index=False)
    print(f"Saved: {out_e} ({len(df_e)} rows)")

    # Page 45 is Peak Demand
    text_p = get_page_text(CEA_PDF, 45)
    rows_p = []
    for line in text_p.splitlines():
        line_clean = line.strip()
        m = re.match(r"^(\d{4}\-\d{2}|2026\-27[^\d]*)\s+([\d,\.\s\-]+)$", line_clean)
        if m:
            yr = m.group(1).split()[0]
            nums = [clean_num(x) for x in m.group(2).split()]
            if len(nums) >= 4:
                rows_p.append({
                    "Year": yr,
                    "Peak_Demand_MW": nums[0],
                    "Peak_Met_MW": nums[1],
                    "Peak_Surplus_Deficit_MW": nums[2],
                    "Peak_Deficit_Pct": nums[3],
                    "Peak_Demand_Growth_Pct": nums[4] if len(nums) > 4 else None,
                    "Peak_Met_Growth_Pct": nums[5] if len(nums) > 5 else None
                })
    df_p = pd.DataFrame(rows_p)
    out_p = os.path.join(DATA_DIR, "cea_historical_peak_demand_met_2003_2026.csv")
    df_p.to_csv(out_p, index=False)
    print(f"Saved: {out_p} ({len(df_p)} rows)")

def extract_cea_installed_capacity_growth():
    """Extract CEA Historical Growth of Installed Capacity since 6th Plan (1980-85) - Page 49"""
    text = get_page_text(CEA_PDF, 49)
    rows = []
    for line in text.splitlines():
        if "Plan" in line or "Jul-2026" in line or "March-" in line:
            if "Growth" in line or "Thermal" in line or "Plan / Year" in line:
                continue
            m = re.match(r"^\s*([A-Za-z0-9\s\(\)\-\/]+?)\s{2,}([\d\.\s]+)$", line)
            if m:
                label = m.group(1).strip()
                n = [clean_num(x) for x in m.group(2).split()]
                if len(n) >= 7:
                    rows.append({
                        "Plan_Year": label,
                        "Thermal_Coal_MW": n[0],
                        "Thermal_Gas_MW": n[1],
                        "Thermal_Diesel_MW": n[2],
                        "Thermal_Total_MW": n[3],
                        "Nuclear_MW": n[4],
                        "Hydro_MW": n[5],
                        "RES_MNRE_MW": n[6] if len(n) > 6 else 0.0,
                        "Grand_Total_MW": n[7] if len(n) > 7 else (n[6] if len(n) == 7 else None)
                    })
    df = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, "cea_historical_power_capacity_growth_since_1985.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

def extract_cea_transmission_grid():
    """Extract CEA Transmission & Substation Grid Voltage Specs"""
    lines_summary = [
        {"Voltage_Level": "+/- 800 kV HVDC", "Line_Type": "HVDC", "Voltage_kV": 800, "Typical_Application": "Long-distance bulk power corridor"},
        {"Voltage_Level": "+/- 500 kV HVDC", "Line_Type": "HVDC", "Voltage_kV": 500, "Typical_Application": "Inter-regional transmission corridor"},
        {"Voltage_Level": "765 kV", "Line_Type": "Extra High Voltage AC", "Voltage_kV": 765, "Typical_Application": "National & Regional grid backbone"},
        {"Voltage_Level": "400 kV", "Line_Type": "High Voltage AC", "Voltage_kV": 400, "Typical_Application": "Bulk substation transmission & DC primary interconnect"},
        {"Voltage_Level": "220 kV", "Line_Type": "High Voltage AC", "Voltage_kV": 220, "Typical_Application": "Sub-transmission & Industrial feeder interconnect"},
    ]
    df = pd.DataFrame(lines_summary)
    out = os.path.join(DATA_DIR, "cea_transmission_grid_voltage_classes.csv")
    df.to_csv(out, index=False)
    print(f"Saved: {out} ({len(df)} rows)")

if __name__ == "__main__":
    print("Extracting MNRE tables...")
    extract_mnre_table_7_1()
    extract_mnre_table_8_2()
    extract_mnre_table_8_5()
    extract_mnre_table_9_2()
    extract_mnre_table_8_1()
    
    print("\nExtracting CEA tables...")
    extract_cea_installed_capacity_statewise()
    extract_cea_power_supply_position()
    extract_cea_historical_energy_and_peak()
    extract_cea_installed_capacity_growth()
    extract_cea_transmission_grid()
    print("\nAll extractions complete successfully.")

