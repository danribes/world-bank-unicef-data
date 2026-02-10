#!/usr/bin/env python3
"""
Script to collect GDP data from World Bank for all countries
Last 70 years (1955-2025)
Indicators:
- NY.GDP.MKTP.CD: GDP (current US$)
- NY.GDP.PCAP.CD: GDP per capita (current US$)
- NY.GDP.MKTP.PP.CD: GDP, PPP (current international $)
"""
import requests
import json
import csv
import time
from datetime import datetime

# World Bank indicators
INDICATORS = {
    'gdp': 'NY.GDP.MKTP.CD',           # GDP (current US$)
    'gdp_per_capita': 'NY.GDP.PCAP.CD', # GDP per capita (current US$)
    'gdp_ppp': 'NY.GDP.MKTP.PP.CD'     # GDP, PPP (current international $)
}

def load_countries():
    """Load countries from the JSON file"""
    with open('/home/dan/work/world_bank_countries.json', 'r') as f:
        countries = json.load(f)
    # Filter out aggregates - keep only actual countries
    return [c for c in countries if c.get('region', {}).get('value') != 'Aggregates']

def fetch_indicator_data(country_id, indicator_code, start_year=1955, end_year=2025):
    """Fetch indicator data for a specific country"""
    url = f"https://api.worldbank.org/v2/country/{country_id}/indicator/{indicator_code}"
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
                return data[1]  # Returns list of year-value pairs
        return []
    except Exception as e:
        print(f"  ⚠️  Error fetching {indicator_code} for {country_id}: {str(e)}")
        return []

def collect_all_gdp_data():
    """Collect GDP data for all countries"""
    print("🌍 Loading countries...")
    countries = load_countries()
    print(f"📊 Found {len(countries)} countries (excluding aggregates)\n")
    
    # Prepare data structure
    all_data = []
    
    print("⏳ Collecting GDP data (this will take a while)...")
    print("=" * 80)
    
    for i, country in enumerate(countries, 1):
        country_id = country.get('id')
        country_name = country.get('name')
        iso2 = country.get('iso2Code')
        
        print(f"[{i}/{len(countries)}] {country_name} ({country_id})...", end=' ')
        
        # Fetch all three indicators
        gdp_data = fetch_indicator_data(country_id, INDICATORS['gdp'])
        gdp_pc_data = fetch_indicator_data(country_id, INDICATORS['gdp_per_capita'])
        gdp_ppp_data = fetch_indicator_data(country_id, INDICATORS['gdp_ppp'])
        
        # Organize by year
        years_data = {}
        
        for item in gdp_data:
            year = item.get('date')
            if year:
                if year not in years_data:
                    years_data[year] = {}
                years_data[year]['gdp'] = item.get('value')
        
        for item in gdp_pc_data:
            year = item.get('date')
            if year:
                if year not in years_data:
                    years_data[year] = {}
                years_data[year]['gdp_per_capita'] = item.get('value')
        
        for item in gdp_ppp_data:
            year = item.get('date')
            if year:
                if year not in years_data:
                    years_data[year] = {}
                years_data[year]['gdp_ppp'] = item.get('value')
        
        # Add to main data
        for year, values in years_data.items():
            all_data.append({
                'country_id': country_id,
                'country_name': country_name,
                'iso2_code': iso2,
                'year': year,
                'gdp_current_usd': values.get('gdp'),
                'gdp_per_capita_current_usd': values.get('gdp_per_capita'),
                'gdp_ppp_current_intl_dollar': values.get('gdp_ppp')
            })
        
        data_points = len(years_data)
        print(f"✓ ({data_points} years)")
        
        # Rate limiting - be nice to the API
        if i % 10 == 0:
            time.sleep(1)
    
    print("\n" + "=" * 80)
    print(f"✅ Data collection complete! Total records: {len(all_data)}")
    
    return all_data

def save_data(data):
    """Save data to CSV and JSON files"""
    
    # Sort by country and year
    data.sort(key=lambda x: (x['country_name'], x['year']))
    
    # Save to CSV
    csv_file = '/home/dan/work/world_bank_gdp_data_70years.csv'
    print(f"\n💾 Saving to CSV: {csv_file}")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'country_id', 'country_name', 'iso2_code', 'year',
            'gdp_current_usd', 'gdp_per_capita_current_usd', 'gdp_ppp_current_intl_dollar'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ CSV saved!")
    
    # Save to JSON
    json_file = '/home/dan/work/world_bank_gdp_data_70years.json'
    print(f"💾 Saving to JSON: {json_file}")
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON saved!")
    
    # Generate summary statistics
    print("\n📈 Summary Statistics:")
    print("=" * 80)
    
    countries_with_data = set(d['country_name'] for d in data)
    years_covered = set(d['year'] for d in data)
    
    print(f"Countries with data: {len(countries_with_data)}")
    print(f"Years covered: {min(years_covered)} - {max(years_covered)}")
    print(f"Total data points: {len(data)}")
    
    # Count records by indicator
    gdp_count = sum(1 for d in data if d['gdp_current_usd'] is not None)
    gdp_pc_count = sum(1 for d in data if d['gdp_per_capita_current_usd'] is not None)
    gdp_ppp_count = sum(1 for d in data if d['gdp_ppp_current_intl_dollar'] is not None)
    
    print(f"\nRecords by indicator:")
    print(f"  - GDP (current US$): {gdp_count:,}")
    print(f"  - GDP per capita (current US$): {gdp_pc_count:,}")
    print(f"  - GDP PPP (current intl $): {gdp_ppp_count:,}")
    
    # Sample data
    print(f"\n📋 Sample records (first 5):")
    for record in data[:5]:
        gdp_val = f"${record['gdp_current_usd']:,.0f}" if record['gdp_current_usd'] else 'N/A'
        print(f"  {record['country_name']} ({record['year']}): GDP={gdp_val}")

if __name__ == "__main__":
    print("=" * 80)
    print("World Bank GDP Data Collection Tool")
    print("Collecting: GDP, GDP per capita, GDP PPP (1955-2025)")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    # Collect data
    data = collect_all_gdp_data()
    
    # Save data
    save_data(data)
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
    print("\n✅ Done! Files created:")
    print("  📄 world_bank_gdp_data_70years.csv")
    print("  📄 world_bank_gdp_data_70years.json")
