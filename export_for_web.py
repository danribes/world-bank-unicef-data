#!/usr/bin/env python3
"""
Export World Bank + UNICEF data to JSON format for the GitHub Pages website.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path


def load_data():
    """Load the main dataset."""
    return pd.read_excel('world_bank_gdp_data_with_poverty.xlsx')


def prepare_mortality_data(df):
    """Prepare mortality trend data for visualization."""
    mortality_cols = ['under5_mortality_rate', 'infant_mortality_rate', 'neonatal_mortality_rate']

    # Get global averages by year
    yearly_avg = df.groupby('year')[mortality_cols].mean().reset_index()

    # Filter to years with sufficient data (1990 onwards has better coverage)
    yearly_avg = yearly_avg[yearly_avg['year'] >= 1990]

    return {
        'labels': yearly_avg['year'].astype(str).tolist(),
        'datasets': [
            {
                'label': 'Under-5 Mortality Rate',
                'data': yearly_avg['under5_mortality_rate'].round(1).tolist(),
                'borderColor': '#ea4335',
                'backgroundColor': '#ea433520',
                'fill': True,
                'tension': 0.4
            },
            {
                'label': 'Infant Mortality Rate',
                'data': yearly_avg['infant_mortality_rate'].round(1).tolist(),
                'borderColor': '#1a73e8',
                'backgroundColor': '#1a73e820',
                'fill': True,
                'tension': 0.4
            },
            {
                'label': 'Neonatal Mortality Rate',
                'data': yearly_avg['neonatal_mortality_rate'].round(1).tolist(),
                'borderColor': '#34a853',
                'backgroundColor': '#34a85320',
                'fill': True,
                'tension': 0.4
            }
        ]
    }


def prepare_nutrition_data(df):
    """Prepare nutrition data by region for visualization."""
    # Define regions based on common World Bank classifications
    regions = {
        'Sub-Saharan Africa': ['Nigeria', 'Ethiopia', 'Kenya', 'Tanzania', 'South Africa', 'Ghana', 'Senegal'],
        'South Asia': ['India', 'Bangladesh', 'Pakistan', 'Nepal', 'Sri Lanka'],
        'East Asia & Pacific': ['China', 'Indonesia', 'Vietnam', 'Philippines', 'Thailand'],
        'Latin America': ['Brazil', 'Mexico', 'Colombia', 'Peru', 'Argentina'],
        'Middle East & North Africa': ['Egypt, Arab Rep.', 'Morocco', 'Tunisia', 'Jordan'],
        'Europe & Central Asia': ['Turkey', 'Poland', 'Romania', 'Ukraine']
    }

    nutrition_cols = ['stunting_pct', 'wasting_pct', 'underweight_pct']

    # Get latest data for each country
    latest = df.sort_values('year').groupby('country_name').last().reset_index()

    regional_data = {}
    for region, countries in regions.items():
        region_df = latest[latest['country_name'].isin(countries)]
        regional_data[region] = {
            'stunting': region_df['stunting_pct'].mean() if 'stunting_pct' in region_df else np.nan,
            'wasting': region_df['wasting_pct'].mean() if 'wasting_pct' in region_df else np.nan,
            'underweight': region_df['underweight_pct'].mean() if 'underweight_pct' in region_df else np.nan
        }

    labels = list(regional_data.keys())

    return {
        'labels': labels,
        'datasets': [
            {
                'label': 'Stunting (%)',
                'data': [round(regional_data[r]['stunting'], 1) if not np.isnan(regional_data[r]['stunting']) else None for r in labels],
                'backgroundColor': '#ea4335cc'
            },
            {
                'label': 'Wasting (%)',
                'data': [round(regional_data[r]['wasting'], 1) if not np.isnan(regional_data[r]['wasting']) else None for r in labels],
                'backgroundColor': '#fbbc04cc'
            },
            {
                'label': 'Underweight (%)',
                'data': [round(regional_data[r]['underweight'], 1) if not np.isnan(regional_data[r]['underweight']) else None for r in labels],
                'backgroundColor': '#9334e6cc'
            }
        ]
    }


def prepare_poverty_scatter_data(df):
    """Prepare scatter plot data showing GDP vs child mortality."""
    # Get latest data for each country with both GDP and mortality data
    cols = ['country_name', 'year', 'gdp_per_capita_current_usd', 'under5_mortality_rate']

    # Filter to rows with both values
    valid = df[cols].dropna()

    # Get latest year for each country
    latest = valid.sort_values('year').groupby('country_name').last().reset_index()

    # Sample countries for visualization (too many points makes chart unreadable)
    if len(latest) > 100:
        latest = latest.sample(100, random_state=42)

    scatter_data = []
    for _, row in latest.iterrows():
        scatter_data.append({
            'x': round(row['gdp_per_capita_current_usd'], 0),
            'y': round(row['under5_mortality_rate'], 1),
            'country': row['country_name']
        })

    return {
        'datasets': [{
            'label': 'GDP per Capita vs Under-5 Mortality',
            'data': scatter_data,
            'backgroundColor': '#1cabe280',
            'borderColor': '#1cabe2',
            'pointRadius': 6
        }]
    }


def prepare_summary_stats(df):
    """Calculate summary statistics."""
    return {
        'total_countries': df['country_name'].nunique(),
        'year_range': {
            'start': int(df['year'].min()),
            'end': int(df['year'].max())
        },
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'data_coverage': {
            'under5_mortality': int(df['under5_mortality_rate'].notna().sum()),
            'infant_mortality': int(df['infant_mortality_rate'].notna().sum()),
            'stunting': int(df['stunting_pct'].notna().sum()) if 'stunting_pct' in df else 0,
            'gdp_per_capita': int(df['gdp_per_capita_current_usd'].notna().sum())
        }
    }


def main():
    print("Loading data...")
    df = load_data()

    print("Preparing visualizations...")

    output = {
        'summary': prepare_summary_stats(df),
        'mortality': prepare_mortality_data(df),
        'nutrition': prepare_nutrition_data(df),
        'poverty': prepare_poverty_scatter_data(df)
    }

    # Ensure output directory exists
    output_dir = Path('docs/data')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write summary JSON
    output_file = output_dir / 'summary.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"Exported data to {output_file}")

    # Also export a simplified country list for dropdowns
    countries = df['country_name'].unique().tolist()
    countries.sort()

    with open(output_dir / 'countries.json', 'w') as f:
        json.dump(countries, f, indent=2)

    print(f"Exported country list to {output_dir / 'countries.json'}")
    print("Done!")


if __name__ == '__main__':
    main()
