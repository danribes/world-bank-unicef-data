#!/usr/bin/env python3
"""
Script to extract OECD Income Distribution Database (IDD) data
and merge with existing World Bank + UNICEF data.
"""

import requests
import pandas as pd
from io import StringIO
import time

# OECD SDMX API endpoint
OECD_API_BASE = "https://sdmx.oecd.org/public/rest/data"
DATAFLOW = "OECD.WISE.INE,DSD_WISE_IDD@DF_IDD,1.0"

# Measures to extract
MEASURES = [
    "INC_DISP_GINI",   # Gini coefficient (disposable income)
    "PR_INC_DISP",     # Poverty rate (disposable income)
    "PG_INC_DISP",     # Poverty gap (disposable income)
    "QR_INC_DISP",     # Quintile share ratio (S80/S20)
    "PAL_INC_DISP",    # Palma ratio
    "D9_1_INC_DISP",   # P90/P10 decile ratio
    "D9_5_INC_DISP",   # P90/P50 decile ratio
    "D5_1_INC_DISP",   # P50/P10 decile ratio
    "INC_MRKT_GINI",   # Gini (market income)
    "PR_INC_MRKT",     # Poverty rate (market income)
]

# Column names for the output
COLUMN_NAMES = {
    "INC_DISP_GINI": "oecd_gini_disposable_income",
    "PR_INC_DISP": "oecd_poverty_rate_disposable_income",
    "PG_INC_DISP": "oecd_poverty_gap_disposable_income",
    "QR_INC_DISP": "oecd_quintile_share_ratio_s80_s20",
    "PAL_INC_DISP": "oecd_palma_ratio",
    "D9_1_INC_DISP": "oecd_p90_p10_decile_ratio",
    "D9_5_INC_DISP": "oecd_p90_p50_decile_ratio",
    "D5_1_INC_DISP": "oecd_p50_p10_decile_ratio",
    "INC_MRKT_GINI": "oecd_gini_market_income",
    "PR_INC_MRKT": "oecd_poverty_rate_market_income",
}


def fetch_oecd_data(measures):
    """Fetch OECD IDD data for specified measures."""
    measures_str = "+".join(measures)

    # Query for all countries, annual frequency, total age group, latest methodology
    # Using wildcards for dimensions we don't care about filtering
    url = f"{OECD_API_BASE}/{DATAFLOW}/.A.{measures_str}..._T.METH2012.D_CUR.PL_50"

    print(f"Fetching OECD IDD data...")
    print(f"URL: {url}")

    headers = {"Accept": "text/csv"}

    try:
        response = requests.get(url, headers=headers, timeout=120)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            print(f"Retrieved {len(df)} records")
            return df
        else:
            print(f"Error: {response.status_code}")
            print(response.text[:500])
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def fetch_oecd_data_by_measure(measure):
    """Fetch OECD IDD data for a single measure."""
    # Query for all countries, annual, total age, latest methodology
    url = f"{OECD_API_BASE}/{DATAFLOW}/.A.{measure}..._T.METH2012.D_CUR."

    print(f"  Fetching {measure}...")

    headers = {"Accept": "text/csv"}

    try:
        response = requests.get(url, headers=headers, timeout=120)
        if response.status_code == 200 and response.text.strip():
            df = pd.read_csv(StringIO(response.text))
            print(f"    Retrieved {len(df)} records")
            return df
        else:
            print(f"    No data or error: {response.status_code}")
            return None
    except Exception as e:
        print(f"    Error: {e}")
        return None


def process_oecd_data(df):
    """Process OECD data to country-year format."""
    if df is None or df.empty:
        return pd.DataFrame()

    # Keep only relevant columns
    cols_to_keep = ['REF_AREA', 'MEASURE', 'TIME_PERIOD', 'OBS_VALUE']
    df = df[cols_to_keep].copy()

    # Rename columns
    df = df.rename(columns={
        'REF_AREA': 'country_id',
        'TIME_PERIOD': 'year',
        'OBS_VALUE': 'value'
    })

    # Convert year to integer (handle cases like "2015-02")
    df['year'] = df['year'].astype(str).str[:4].astype(int)

    # Pivot to get measures as columns
    pivot_df = df.pivot_table(
        index=['country_id', 'year'],
        columns='MEASURE',
        values='value',
        aggfunc='first'
    ).reset_index()

    # Rename measure columns
    pivot_df = pivot_df.rename(columns=COLUMN_NAMES)

    return pivot_df


def main():
    # Read existing Excel file
    print("Reading existing Excel file...")
    excel_path = "world_bank_gdp_data_with_poverty.xlsx"
    wb_df = pd.read_excel(excel_path)
    print(f"Loaded {len(wb_df)} rows with {len(wb_df.columns)} columns")

    # Fetch OECD data for each measure separately (more reliable)
    all_data = []
    for measure in MEASURES:
        df = fetch_oecd_data_by_measure(measure)
        if df is not None and len(df) > 0:
            all_data.append(df)
        time.sleep(0.5)  # Rate limiting

    if not all_data:
        print("No OECD data retrieved!")
        return

    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal OECD records: {len(combined_df)}")

    # Process and pivot the data
    print("\nProcessing OECD data...")
    oecd_df = process_oecd_data(combined_df)
    print(f"Processed data: {len(oecd_df)} country-year combinations")
    print(f"Columns: {list(oecd_df.columns)}")

    # Ensure year columns are integers
    wb_df['year'] = wb_df['year'].astype(int)
    oecd_df['year'] = oecd_df['year'].astype(int)

    # Merge with existing data
    print("\nMerging with existing data...")
    merged_df = wb_df.merge(
        oecd_df,
        on=['country_id', 'year'],
        how='left'
    )
    print(f"Merged data: {len(merged_df)} rows with {len(merged_df.columns)} columns")

    # Check data availability
    new_cols = [c for c in merged_df.columns if c.startswith('oecd_')]
    print("\nData availability for new columns:")
    for col in new_cols:
        non_null = merged_df[col].notna().sum()
        print(f"  {col}: {non_null} non-null values")

    # Save to Excel
    print(f"\nSaving to {excel_path}...")
    merged_df.to_excel(excel_path, index=False, sheet_name='world_bank_gdp_data_billions')

    print("\nDone!")
    print(f"New columns added: {new_cols}")


if __name__ == "__main__":
    main()
