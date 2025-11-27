#!/usr/bin/env python3
"""
Script to extract UNICEF child welfare data and merge with World Bank data.
Fetches child poverty, child mortality, and nutrition data for all countries.
"""

import requests
import pandas as pd
import time
from collections import defaultdict

# UNICEF SDMX API base URL
BASE_URL = "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data"

# Countries from the Excel file
COUNTRIES = [
    "ABW", "AFG", "AGO", "ALB", "AND", "ARE", "ARG", "ARM", "ASM", "ATG",
    "AUS", "AUT", "AZE", "BDI", "BEL", "BEN", "BFA", "BGD", "BGR", "BHR",
    "BHS", "BIH", "BLR", "BLZ", "BMU", "BOL", "BRA", "BRB", "BRN", "BTN",
    "BWA", "CAF", "CAN", "CHE", "CHI", "CHL", "CHN", "CIV", "CMR", "COD",
    "COG", "COL", "COM", "CPV", "CRI", "CUB", "CUW", "CYM", "CYP", "CZE",
    "DEU", "DJI", "DMA", "DNK", "DOM", "DZA", "ECU", "EGY", "ERI", "ESP",
    "EST", "ETH", "FIN", "FJI", "FRA", "FRO", "FSM", "GAB", "GBR", "GEO",
    "GHA", "GIB", "GIN", "GMB", "GNB", "GNQ", "GRC", "GRD", "GRL", "GTM",
    "GUM", "GUY", "HKG", "HND", "HRV", "HTI", "HUN", "IDN", "IMN", "IND",
    "IRL", "IRN", "IRQ", "ISL", "ISR", "ITA", "JAM", "JOR", "JPN", "KAZ",
    "KEN", "KGZ", "KHM", "KIR", "KNA", "KOR", "KWT", "LAO", "LBN", "LBR",
    "LBY", "LCA", "LIE", "LKA", "LSO", "LTU", "LUX", "LVA", "MAC", "MAF",
    "MAR", "MCO", "MDA", "MDG", "MDV", "MEX", "MHL", "MKD", "MLI", "MLT",
    "MMR", "MNE", "MNG", "MNP", "MOZ", "MRT", "MUS", "MWI", "MYS", "NAM",
    "NCL", "NER", "NGA", "NIC", "NLD", "NOR", "NPL", "NRU", "NZL", "OMN",
    "PAK", "PAN", "PER", "PHL", "PLW", "PNG", "POL", "PRI", "PRK", "PRT",
    "PRY", "PSE", "PYF", "QAT", "ROU", "RUS", "RWA", "SAU", "SDN", "SEN",
    "SGP", "SLB", "SLE", "SLV", "SMR", "SOM", "SRB", "SSD", "STP", "SUR",
    "SVK", "SVN", "SWE", "SWZ", "SXM", "SYC", "SYR", "TCA", "TCD", "TGO",
    "THA", "TJK", "TKM", "TLS", "TON", "TTO", "TUN", "TUR", "TUV", "TZA",
    "UGA", "UKR", "URY", "USA", "UZB", "VCT", "VEN", "VGB", "VIR", "VNM",
    "VUT", "WSM", "XKX", "YEM", "ZAF", "ZMB", "ZWE"
]

def fetch_unicef_data(dataflow, countries_batch, indicators=None):
    """Fetch data from UNICEF API for a batch of countries."""
    countries_str = "+".join(countries_batch)

    # Build the URL
    if indicators:
        indicators_str = "+".join(indicators)
        url = f"{BASE_URL}/{dataflow}/{countries_str}.{indicators_str}._T._T?format=csv"
    else:
        url = f"{BASE_URL}/{dataflow}/{countries_str}?format=csv"

    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200 and response.text.strip():
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            return df
        else:
            return None
    except Exception as e:
        print(f"Error fetching {dataflow}: {e}")
        return None

def fetch_child_mortality_data():
    """Fetch child mortality data for all countries."""
    print("Fetching child mortality data...")

    # Key mortality indicators
    indicators = [
        "CME_MRY0T4",   # Under-five mortality rate
        "CME_MRY0",     # Infant mortality rate
        "CME_MRM0",     # Neonatal mortality rate
        "CME_MRY5T14",  # Mortality rate 5-14 years
    ]

    all_data = []
    batch_size = 50

    for i in range(0, len(COUNTRIES), batch_size):
        batch = COUNTRIES[i:i+batch_size]
        print(f"  Processing countries {i+1}-{min(i+batch_size, len(COUNTRIES))}...")

        df = fetch_unicef_data("CME", batch, indicators)
        if df is not None and len(df) > 0:
            all_data.append(df)
        time.sleep(0.5)  # Rate limiting

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        print(f"  Retrieved {len(combined)} mortality records")
        return combined
    return pd.DataFrame()

def fetch_child_poverty_data():
    """Fetch child poverty data for all countries."""
    print("Fetching child poverty data...")

    all_data = []
    batch_size = 50

    for i in range(0, len(COUNTRIES), batch_size):
        batch = COUNTRIES[i:i+batch_size]
        print(f"  Processing countries {i+1}-{min(i+batch_size, len(COUNTRIES))}...")

        df = fetch_unicef_data("CHLD_PVTY", batch)
        if df is not None and len(df) > 0:
            all_data.append(df)
        time.sleep(0.5)

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        print(f"  Retrieved {len(combined)} poverty records")
        return combined
    return pd.DataFrame()

def fetch_nutrition_data():
    """Fetch nutrition data for all countries."""
    print("Fetching nutrition data...")

    # Key nutrition indicators (for children under 5)
    indicators = [
        "NT_ANT_HAZ_NE2",   # Stunting (height-for-age < -2 SD)
        "NT_ANT_WHZ_NE2",   # Wasting (weight-for-height < -2 SD)
        "NT_ANT_WAZ_NE2",   # Underweight (weight-for-age < -2 SD)
        "NT_BF_EXBF",       # Exclusive breastfeeding
        "NT_BW_LBW",        # Low birth weight
    ]

    all_data = []
    batch_size = 50

    for i in range(0, len(COUNTRIES), batch_size):
        batch = COUNTRIES[i:i+batch_size]
        print(f"  Processing countries {i+1}-{min(i+batch_size, len(COUNTRIES))}...")

        df = fetch_unicef_data("NUTRITION", batch, indicators)
        if df is not None and len(df) > 0:
            all_data.append(df)
        time.sleep(0.5)

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        print(f"  Retrieved {len(combined)} nutrition records")
        return combined
    return pd.DataFrame()

def process_mortality_data(df):
    """Process mortality data to get country-year level aggregates."""
    if df.empty:
        return pd.DataFrame()

    # Filter for total sex and total wealth quintile
    df_filtered = df[
        (df['SEX'] == '_T') &
        (df['WEALTH_QUINTILE'] == '_T')
    ].copy()

    # Pivot to get indicators as columns
    pivot_df = df_filtered.pivot_table(
        index=['REF_AREA', 'TIME_PERIOD'],
        columns='INDICATOR',
        values='OBS_VALUE',
        aggfunc='first'
    ).reset_index()

    # Rename columns
    rename_map = {
        'REF_AREA': 'country_id',
        'TIME_PERIOD': 'year',
        'CME_MRY0T4': 'under5_mortality_rate',
        'CME_MRY0': 'infant_mortality_rate',
        'CME_MRM0': 'neonatal_mortality_rate',
        'CME_MRY5T14': 'mortality_rate_5to14',
    }
    pivot_df = pivot_df.rename(columns=rename_map)

    # Select only columns we need
    cols = ['country_id', 'year'] + [c for c in rename_map.values() if c in pivot_df.columns and c not in ['country_id', 'year']]
    pivot_df = pivot_df[[c for c in cols if c in pivot_df.columns]]

    return pivot_df

def process_poverty_data(df):
    """Process child poverty data to get country-year level aggregates."""
    if df.empty:
        return pd.DataFrame()

    # Filter for total
    df_filtered = df[
        (df['SEX'] == '_T') &
        (df['RESIDENCE'] == '_T')
    ].copy()

    # Pivot to get indicators as columns
    pivot_df = df_filtered.pivot_table(
        index=['REF_AREA', 'TIME_PERIOD'],
        columns='INDICATOR',
        values='OBS_VALUE',
        aggfunc='first'
    ).reset_index()

    # Rename columns
    pivot_df = pivot_df.rename(columns={
        'REF_AREA': 'country_id',
        'TIME_PERIOD': 'year'
    })

    # Rename indicators to more readable names
    indicator_renames = {}
    for col in pivot_df.columns:
        if col.startswith('PV_'):
            indicator_renames[col] = f'child_poverty_{col.lower()}'

    pivot_df = pivot_df.rename(columns=indicator_renames)

    return pivot_df

def process_nutrition_data(df):
    """Process nutrition data to get country-year level aggregates."""
    if df.empty:
        return pd.DataFrame()

    # Filter for total sex, under 5 age group, total residence
    df_filtered = df[
        (df['SEX'] == '_T') &
        (df['AGE'] == 'Y0T4') &  # Under 5 years
        (df['RESIDENCE'] == '_T') &
        (df['WEALTH_QUINTILE'] == '_T')
    ].copy()

    if df_filtered.empty:
        # Try without age filter
        df_filtered = df[
            (df['SEX'] == '_T') &
            (df['RESIDENCE'] == '_T')
        ].copy()

    if df_filtered.empty:
        return pd.DataFrame()

    # Pivot to get indicators as columns
    pivot_df = df_filtered.pivot_table(
        index=['REF_AREA', 'TIME_PERIOD'],
        columns='INDICATOR',
        values='OBS_VALUE',
        aggfunc='first'
    ).reset_index()

    # Rename columns
    rename_map = {
        'REF_AREA': 'country_id',
        'TIME_PERIOD': 'year',
        'NT_ANT_HAZ_NE2': 'stunting_pct',
        'NT_ANT_WHZ_NE2': 'wasting_pct',
        'NT_ANT_WAZ_NE2': 'underweight_pct',
        'NT_BF_EXBF': 'exclusive_breastfeeding_pct',
        'NT_BW_LBW': 'low_birth_weight_pct',
    }
    pivot_df = pivot_df.rename(columns=rename_map)

    # Select only columns we need
    cols = ['country_id', 'year'] + [c for c in rename_map.values() if c in pivot_df.columns and c not in ['country_id', 'year']]
    pivot_df = pivot_df[[c for c in cols if c in pivot_df.columns]]

    return pivot_df

def main():
    # Read the existing Excel file
    print("Reading existing Excel file...")
    excel_path = "/home/dan/world_bank_mcp/world_bank_gdp_data_with_poverty.xlsx"
    wb_df = pd.read_excel(excel_path)
    print(f"  Loaded {len(wb_df)} rows from World Bank data")

    # Fetch UNICEF data
    mortality_raw = fetch_child_mortality_data()
    poverty_raw = fetch_child_poverty_data()
    nutrition_raw = fetch_nutrition_data()

    # Process the data
    print("\nProcessing data...")
    mortality_df = process_mortality_data(mortality_raw)
    poverty_df = process_poverty_data(poverty_raw)
    nutrition_df = process_nutrition_data(nutrition_raw)

    print(f"  Mortality data: {len(mortality_df)} rows")
    print(f"  Poverty data: {len(poverty_df)} rows")
    print(f"  Nutrition data: {len(nutrition_df)} rows")

    # Ensure year columns are integers
    wb_df['year'] = wb_df['year'].astype(int)

    if not mortality_df.empty:
        mortality_df['year'] = mortality_df['year'].astype(int)
    if not poverty_df.empty:
        poverty_df['year'] = poverty_df['year'].astype(int)
    if not nutrition_df.empty:
        nutrition_df['year'] = nutrition_df['year'].astype(int)

    # Merge all dataframes
    print("\nMerging data...")
    merged_df = wb_df.copy()

    if not mortality_df.empty:
        merged_df = merged_df.merge(
            mortality_df,
            on=['country_id', 'year'],
            how='left'
        )
        print(f"  After mortality merge: {len(merged_df)} rows")

    if not poverty_df.empty:
        merged_df = merged_df.merge(
            poverty_df,
            on=['country_id', 'year'],
            how='left'
        )
        print(f"  After poverty merge: {len(merged_df)} rows")

    if not nutrition_df.empty:
        merged_df = merged_df.merge(
            nutrition_df,
            on=['country_id', 'year'],
            how='left'
        )
        print(f"  After nutrition merge: {len(merged_df)} rows")

    # Save to Excel
    output_path = "/home/dan/world_bank_mcp/world_bank_gdp_data_with_poverty.xlsx"
    print(f"\nSaving to {output_path}...")
    merged_df.to_excel(output_path, index=False, sheet_name='world_bank_gdp_data_billions')

    # Print summary of new columns
    new_cols = [c for c in merged_df.columns if c not in wb_df.columns]
    print(f"\nNew columns added: {new_cols}")

    # Print data availability summary
    print("\nData availability summary:")
    for col in new_cols:
        non_null = merged_df[col].notna().sum()
        print(f"  {col}: {non_null} non-null values")

    print("\nDone!")

if __name__ == "__main__":
    main()
