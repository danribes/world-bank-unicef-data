#!/usr/bin/env python3
"""
Add ICER-like column to World Bank dataset:
Ratio of incremental annual debt to incremental annual GDP PPP

ICER formula: (Debt_year - Debt_year-1) / (PPP_year - PPP_year-1)
"""

import pandas as pd
import json

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('world_bank_gdp_data_70years.csv')

print(f"Original dataset: {len(df)} records")
print(f"Columns: {list(df.columns)}")

# Sort by country and year to ensure proper ordering
df = df.sort_values(['country_id', 'year']).reset_index(drop=True)

# Convert debt percentage to numeric (it's percentage of GDP)
df['public_debt_pct_gdp'] = pd.to_numeric(df['public_debt_pct_gdp'], errors='coerce')
df['gdp_ppp_current_intl_dollar'] = pd.to_numeric(df['gdp_ppp_current_intl_dollar'], errors='coerce')

# Calculate absolute debt value (debt % * GDP)
# We need GDP to calculate absolute debt amount
df['gdp_current_usd'] = pd.to_numeric(df['gdp_current_usd'], errors='coerce')
df['absolute_debt_usd'] = (df['public_debt_pct_gdp'] / 100) * df['gdp_current_usd']

print("\nCalculating year-over-year changes...")

# Calculate incremental changes using shift within each country
df['prev_year'] = df.groupby('country_id')['year'].shift(1)
df['prev_debt'] = df.groupby('country_id')['absolute_debt_usd'].shift(1)
df['prev_ppp'] = df.groupby('country_id')['gdp_ppp_current_intl_dollar'].shift(1)

# Calculate incremental changes
df['delta_debt'] = df['absolute_debt_usd'] - df['prev_debt']
df['delta_ppp'] = df['gdp_ppp_current_intl_dollar'] - df['prev_ppp']

# Calculate ICER-like ratio
# Only calculate when both delta_debt and delta_ppp are non-zero
df['debt_ppp_icer'] = None
mask = (df['delta_ppp'].notna()) & (df['delta_ppp'] != 0) & (df['delta_debt'].notna())
df.loc[mask, 'debt_ppp_icer'] = df.loc[mask, 'delta_debt'] / df.loc[mask, 'delta_ppp']

# Keep only the main columns plus the new ICER column
output_df = df[[
    'country_id', 'country_name', 'iso2_code', 'year',
    'gdp_current_usd', 'gdp_per_capita_current_usd',
    'gdp_ppp_current_intl_dollar', 'public_debt_pct_gdp',
    'debt_ppp_icer'
]].copy()

print(f"\nICER Statistics:")
print(f"Total records: {len(output_df)}")
print(f"Records with ICER value: {output_df['debt_ppp_icer'].notna().sum()}")
print(f"Coverage: {output_df['debt_ppp_icer'].notna().sum() / len(output_df) * 100:.1f}%")

# Show some sample calculations
print("\nSample ICER calculations (first 10 non-null values):")
sample = output_df[output_df['debt_ppp_icer'].notna()].head(10)[
    ['country_name', 'year', 'gdp_ppp_current_intl_dollar', 'public_debt_pct_gdp', 'debt_ppp_icer']
]
print(sample.to_string(index=False))

# Save to CSV
csv_output = 'world_bank_gdp_data_with_icer.csv'
output_df.to_csv(csv_output, index=False)
print(f"\n✅ Saved to {csv_output}")

# Save to JSON
json_output = 'world_bank_gdp_data_with_icer.json'
output_df.to_json(json_output, orient='records', indent=2)
print(f"✅ Saved to {json_output}")

# Show file sizes
import os
csv_size = os.path.getsize(csv_output) / 1024
json_size = os.path.getsize(json_output) / 1024 / 1024
print(f"\nFile sizes:")
print(f"  CSV: {csv_size:.1f} KB")
print(f"  JSON: {json_size:.1f} MB")
