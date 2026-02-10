#!/usr/bin/env python3
"""
Convert GDP and GDP PPP values from raw dollars to billions of dollars
for easier readability
"""

import pandas as pd

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('world_bank_gdp_data_with_icer.csv')

print(f"Original dataset: {len(df)} records")

# Convert to numeric first
df['gdp_current_usd'] = pd.to_numeric(df['gdp_current_usd'], errors='coerce')
df['gdp_per_capita_current_usd'] = pd.to_numeric(df['gdp_per_capita_current_usd'], errors='coerce')
df['gdp_ppp_current_intl_dollar'] = pd.to_numeric(df['gdp_ppp_current_intl_dollar'], errors='coerce')

# Convert to billions (divide by 1,000,000,000)
print("\nConverting to billions...")
df['gdp_billions_usd'] = df['gdp_current_usd'] / 1_000_000_000
df['gdp_ppp_billions_intl_dollar'] = df['gdp_ppp_current_intl_dollar'] / 1_000_000_000

# Keep per capita in regular dollars (already readable scale)
# Reorder columns with new billion-scale columns
output_df = df[[
    'country_id', 'country_name', 'iso2_code', 'year',
    'gdp_billions_usd', 'gdp_per_capita_current_usd',
    'gdp_ppp_billions_intl_dollar', 'public_debt_pct_gdp',
    'debt_ppp_icer'
]].copy()

# Show sample before/after
print("\nSample conversions (Brazil 2010-2011):")
brazil_sample = output_df[
    (output_df['country_id'] == 'BRA') & 
    (output_df['year'].isin([2010, 2011]))
][['country_name', 'year', 'gdp_billions_usd', 'gdp_ppp_billions_intl_dollar', 'debt_ppp_icer']]
print(brazil_sample.to_string(index=False))

# Save to CSV
csv_output = 'world_bank_gdp_data_billions.csv'
output_df.to_csv(csv_output, index=False)
print(f"\n✅ Saved to {csv_output}")

# Save to JSON
json_output = 'world_bank_gdp_data_billions.json'
output_df.to_json(json_output, orient='records', indent=2)
print(f"✅ Saved to {json_output}")

# Show file sizes
import os
csv_size = os.path.getsize(csv_output) / 1024
json_size = os.path.getsize(json_output) / 1024 / 1024
print(f"\nFile sizes:")
print(f"  CSV: {csv_size:.1f} KB")
print(f"  JSON: {json_size:.1f} MB")

print(f"\nColumn names:")
for col in output_df.columns:
    print(f"  - {col}")
