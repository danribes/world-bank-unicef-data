#!/usr/bin/env python3
"""
Script to add public debt data to the existing GDP dataset
Public Debt Indicator: GC.DOD.TOTL.GD.ZS (Central government debt, total (% of GDP))
Alternative: DT.DOD.DECT.CD (External debt stocks, total (DOD, current US$))
"""
import requests
import json
import csv
import time
from collections import defaultdict

# Public debt indicator
PUBLIC_DEBT_INDICATOR = 'GC.DOD.TOTL.GD.ZS'  # Central government debt, total (% of GDP)

def load_existing_data():
    """Load the existing GDP data"""
    print("📂 Loading existing GDP data...")
    with open('/home/dan/work/world_bank_gdp_data_70years.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    countries = sorted(set(d['country_id'] for d in data))
    print(f"   Found {len(data)} records for {len(countries)} countries")
    return data, countries

def fetch_public_debt_data(country_id, start_year=1960, end_year=2024):
    """Fetch public debt data for a specific country"""
    url = f"https://api.worldbank.org/v2/country/{country_id}/indicator/{PUBLIC_DEBT_INDICATOR}"
    params = {
        'format': 'json',
        'date': f'{start_year}:{end_year}',
        'per_page': 500
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and data[1]:
                # Return as dict: {year: value}
                return {item['date']: item['value'] for item in data[1]}
        return {}
    except Exception as e:
        print(f"  ⚠️  Error fetching debt data for {country_id}: {str(e)}")
        return {}

def collect_public_debt_data(countries):
    """Collect public debt data for all countries"""
    print("\n💰 Collecting public debt data...")
    print("   Indicator: Central government debt, total (% of GDP)")
    print("=" * 80)
    
    debt_data = {}
    
    for i, country_id in enumerate(countries, 1):
        print(f"[{i}/{len(countries)}] {country_id}...", end=' ', flush=True)
        
        country_debt = fetch_public_debt_data(country_id)
        debt_data[country_id] = country_debt
        
        print(f"✓ ({len(country_debt)} years)")
        
        # Rate limiting
        if i % 10 == 0:
            time.sleep(1)
    
    print("\n" + "=" * 80)
    
    # Count total records
    total_debt_records = sum(len(v) for v in debt_data.values())
    print(f"✅ Collected {total_debt_records:,} public debt records")
    
    return debt_data

def merge_data(gdp_data, debt_data):
    """Merge public debt data into GDP data"""
    print("\n🔗 Merging public debt data with GDP data...")
    
    merged_count = 0
    
    for record in gdp_data:
        country_id = record['country_id']
        year = record['year']
        
        # Add public debt value if available
        if country_id in debt_data and year in debt_data[country_id]:
            record['public_debt_pct_gdp'] = debt_data[country_id][year]
            if debt_data[country_id][year] is not None:
                merged_count += 1
        else:
            record['public_debt_pct_gdp'] = None
    
    print(f"   Merged {merged_count:,} public debt values")
    return gdp_data

def save_updated_data(data):
    """Save the updated data with public debt column"""
    
    # Sort by country and year
    data.sort(key=lambda x: (x['country_name'], x['year']))
    
    # Save to CSV
    csv_file = '/home/dan/work/world_bank_gdp_data_70years.csv'
    print(f"\n💾 Saving updated CSV: {csv_file}")
    
    fieldnames = [
        'country_id', 'country_name', 'iso2_code', 'year',
        'gdp_current_usd', 'gdp_per_capita_current_usd', 'gdp_ppp_current_intl_dollar',
        'public_debt_pct_gdp'
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ CSV updated!")
    
    # Save to JSON
    json_file = '/home/dan/work/world_bank_gdp_data_70years.json'
    print(f"💾 Saving updated JSON: {json_file}")
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON updated!")
    
    # Generate summary
    print("\n📈 Updated Data Summary:")
    print("=" * 80)
    
    total_records = len(data)
    debt_records = sum(1 for d in data if d['public_debt_pct_gdp'] is not None)
    
    print(f"Total records: {total_records:,}")
    print(f"Records with public debt data: {debt_records:,} ({debt_records/total_records*100:.1f}%)")
    
    # Show sample with debt data
    print(f"\n📋 Sample records with debt data:")
    samples = [d for d in data if d['public_debt_pct_gdp'] is not None][:5]
    
    for record in samples:
        debt_val = f"{float(record['public_debt_pct_gdp']):.1f}%" if record['public_debt_pct_gdp'] else 'N/A'
        print(f"  {record['country_name']} ({record['year']}): Debt = {debt_val} of GDP")

if __name__ == "__main__":
    print("=" * 80)
    print("Adding Public Debt Data to World Bank GDP Dataset")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    # Load existing data
    gdp_data, countries = load_existing_data()
    
    # Collect public debt data
    debt_data = collect_public_debt_data(countries)
    
    # Merge data
    merged_data = merge_data(gdp_data, debt_data)
    
    # Save updated data
    save_updated_data(merged_data)
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
    print("\n✅ Done! Public debt column added to dataset.")
    print("   Column name: public_debt_pct_gdp")
    print("   Description: Central government debt as % of GDP")
