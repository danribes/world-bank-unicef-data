#!/usr/bin/env python3
"""
Add fiscal indicators to the World Bank dataset:
1. Tax revenue (% of GDP)
2. Total government expenses (% of GDP)
3. Fiscal deficit/surplus (% of GDP)
4. Total government revenue (% of GDP)
5. Education spending (% of GDP)
"""

import pandas as pd
import requests
import time

# Load existing dataset
print("Loading existing dataset...")
df = pd.read_csv('world_bank_gdp_data_billions.csv')
print(f"Current dataset: {len(df)} records")

# Load country list
countries_df = pd.read_csv('world_bank_countries.csv')
country_ids = countries_df['ID'].tolist()
print(f"Countries to process: {len(country_ids)}")

# Fiscal indicators to fetch
indicators = {
    'GC.TAX.TOTL.GD.ZS': 'tax_revenue_pct_gdp',
    'GC.XPN.TOTL.GD.ZS': 'govt_expense_pct_gdp',
    'GC.NLD.TOTL.GD.ZS': 'fiscal_balance_pct_gdp',
    'GC.REV.XGRT.GD.ZS': 'govt_revenue_pct_gdp',
    'SE.XPD.TOTL.GD.ZS': 'education_spending_pct_gdp'
}

# Collect data for each indicator
all_fiscal_data = {}

for indicator_code, column_name in indicators.items():
    print(f"\n{'='*60}")
    print(f"Collecting: {column_name}")
    print(f"Indicator: {indicator_code}")
    print('='*60)
    
    fiscal_data = {}
    
    for i, country_id in enumerate(country_ids, 1):
        if i % 10 == 0:
            print(f"Progress: {i}/{len(country_ids)} countries processed...")
            time.sleep(1)  # Rate limiting
        
        url = f"https://api.worldbank.org/v2/country/{country_id}/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'date': '1960:2024',
            'per_page': 1000
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if len(data) > 1 and data[1]:
                for entry in data[1]:
                    year = entry['date']
                    value = entry['value']
                    key = (country_id, int(year))
                    fiscal_data[key] = value
        
        except Exception as e:
            print(f"Error fetching {country_id}: {e}")
            continue
    
    all_fiscal_data[column_name] = fiscal_data
    print(f"✅ Collected {len(fiscal_data)} data points for {column_name}")

# Merge fiscal data with existing dataset
print("\n" + "="*60)
print("Merging fiscal data with existing dataset...")
print("="*60)

for column_name, fiscal_data in all_fiscal_data.items():
    df[column_name] = df.apply(
        lambda row: fiscal_data.get((row['country_id'], row['year']), None),
        axis=1
    )
    non_null = df[column_name].notna().sum()
    coverage = (non_null / len(df)) * 100
    print(f"✅ {column_name}: {non_null} records ({coverage:.1f}% coverage)")

# Save updated dataset
csv_output = 'world_bank_gdp_data_billions.csv'
df.to_csv(csv_output, index=False)
print(f"\n✅ Saved to {csv_output}")

# Save to JSON
json_output = 'world_bank_gdp_data_billions.json'
df.to_json(json_output, orient='records', indent=2)
print(f"✅ Saved to {json_output}")

# Show file sizes
import os
csv_size = os.path.getsize(csv_output) / 1024
json_size = os.path.getsize(json_output) / 1024 / 1024
print(f"\nFile sizes:")
print(f"  CSV: {csv_size:.1f} KB")
print(f"  JSON: {json_size:.1f} MB")

# Show sample data (Spain 2020-2024)
print("\n" + "="*60)
print("Sample data (Spain 2020-2024):")
print("="*60)
sample = df[
    (df['country_id'] == 'ESP') & 
    (df['year'] >= 2020)
][['country_name', 'year', 'tax_revenue_pct_gdp', 'govt_expense_pct_gdp', 
   'fiscal_balance_pct_gdp', 'govt_revenue_pct_gdp', 'education_spending_pct_gdp']]
print(sample.to_string(index=False))

print(f"\n✅ Dataset now has {len(df.columns)} columns")
print(f"New columns added:")
for col in indicators.values():
    print(f"  - {col}")
