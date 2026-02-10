#!/usr/bin/env python3
"""
Script to fetch all countries from World Bank API
"""
import requests
import json
import csv

def get_all_countries():
    """Fetch all countries from World Bank API"""
    url = "https://api.worldbank.org/v2/country?format=json&per_page=500"
    
    print("Fetching countries from World Bank API...")
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # The API returns [metadata, countries_list]
        if len(data) > 1:
            countries = data[1]
            print(f"\nFound {len(countries)} countries/regions\n")
            
            # Save to CSV
            csv_file = '/home/dan/work/world_bank_countries.csv'
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'ISO2', 'Name', 'Region', 'Income Level', 'Capital City'])
                
                for country in countries:
                    writer.writerow([
                        country.get('id', ''),
                        country.get('iso2Code', ''),
                        country.get('name', ''),
                        country.get('region', {}).get('value', ''),
                        country.get('incomeLevel', {}).get('value', ''),
                        country.get('capitalCity', '')
                    ])
            
            print(f"✅ Saved to: {csv_file}")
            
            # Save to JSON
            json_file = '/home/dan/work/world_bank_countries.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(countries, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved to: {json_file}")
            
            # Print first 20 countries as preview
            print("\n📋 Preview (first 20 countries):")
            print(f"{'ID':<6} {'ISO2':<6} {'Name':<40} {'Region':<30}")
            print("-" * 90)
            
            for country in countries[:20]:
                print(f"{country.get('id', ''):<6} {country.get('iso2Code', ''):<6} {country.get('name', ''):<40} {country.get('region', {}).get('value', ''):<30}")
            
            print(f"\n... and {len(countries) - 20} more")
            
            return countries
        else:
            print("❌ Unexpected API response format")
            return None
    else:
        print(f"❌ Error: HTTP {response.status_code}")
        return None

if __name__ == "__main__":
    countries = get_all_countries()
    
    if countries:
        print(f"\n✅ Total countries/regions extracted: {len(countries)}")
        print("\nFiles created:")
        print("  - world_bank_countries.csv (for Excel/spreadsheet)")
        print("  - world_bank_countries.json (full data)")
