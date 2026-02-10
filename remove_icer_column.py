#!/usr/bin/env python3
"""
Remove the debt_ppp_icer column from the dataset
"""

import pandas as pd

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('world_bank_gdp_data_billions.csv')

print(f"Original dataset: {len(df)} records")
print(f"Original columns: {list(df.columns)}")

# Drop the ICER column
df_clean = df.drop(columns=['debt_ppp_icer'])

print(f"\nNew columns: {list(df_clean.columns)}")

# Save to CSV
csv_output = 'world_bank_gdp_data_billions.csv'
df_clean.to_csv(csv_output, index=False)
print(f"\n✅ Updated {csv_output}")

# Save to JSON
json_output = 'world_bank_gdp_data_billions.json'
df_clean.to_json(json_output, orient='records', indent=2)
print(f"✅ Updated {json_output}")

# Show file sizes
import os
csv_size = os.path.getsize(csv_output) / 1024
json_size = os.path.getsize(json_output) / 1024 / 1024
print(f"\nFile sizes:")
print(f"  CSV: {csv_size:.1f} KB")
print(f"  JSON: {json_size:.1f} MB")

# Show sample
print("\nSample data (Spain 2023-2024):")
sample = df_clean[(df_clean['country_id'] == 'ESP') & (df_clean['year'].isin([2023, 2024]))]
print(sample.to_string(index=False))
