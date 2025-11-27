# World Bank + UNICEF Data

This repository contains economic and child welfare data from the World Bank and UNICEF, merged into a single dataset covering 217 countries from 1960-2023.

## Data Sources

- **World Bank**: GDP, public debt, tax revenue, government expenses, inflation, poverty indicators, and Gini index
- **UNICEF**: Child mortality, nutrition indicators, and child poverty measures

## Dataset

The main dataset is `world_bank_gdp_data_with_poverty.xlsx` containing 54 columns:

### World Bank Economic Indicators
- `gdp_billions_usd` - GDP in billions USD
- `gdp_per_capita_current_usd` - GDP per capita
- `gdp_ppp_billions_intl_dollar` - GDP PPP
- `public_debt_pct_gdp` - Public debt as % of GDP
- `tax_revenue_pct_gdp` - Tax revenue as % of GDP
- `govt_expense_pct_gdp` - Government expenses as % of GDP
- `inflation_consumer_prices_annual_pct` - Annual inflation rate
- `poverty_headcount_3_dollars_pct` - Poverty at $3.65/day
- `poverty_headcount_4_dollars_pct` - Poverty at $4/day
- `poverty_headcount_8_dollars_pct` - Poverty at $8/day
- `gini_index` - Income inequality index

### UNICEF Child Mortality Indicators
- `under5_mortality_rate` - Deaths per 1,000 live births (under 5)
- `infant_mortality_rate` - Deaths per 1,000 live births (under 1)
- `neonatal_mortality_rate` - Deaths per 1,000 live births (first 28 days)
- `mortality_rate_5to14` - Deaths per 1,000 children aged 5-14

### UNICEF Nutrition Indicators
- `stunting_pct` - Height-for-age < -2 SD (%)
- `wasting_pct` - Weight-for-height < -2 SD (%)
- `underweight_pct` - Weight-for-age < -2 SD (%)
- `low_birth_weight_pct` - Birth weight < 2500g (%)

### UNICEF Child Poverty Indicators
- 27 child deprivation and poverty indicators

## Scripts

- `extract_unicef_data.py` - Script to fetch UNICEF data and merge with World Bank data
- `add_poverty_data.py` - Script to add poverty indicators to the dataset

## Coverage

- **Countries**: 217
- **Years**: 1960-2023
- **Rows**: 14,105
- **Columns**: 54

## Data Availability

| Category | Indicator | Data Points |
|----------|-----------|-------------|
| Mortality | Under-5 mortality rate | 11,619 |
| Mortality | Infant mortality rate | 11,588 |
| Mortality | Neonatal mortality rate | 9,872 |
| Nutrition | Stunting | 1,123 |
| Nutrition | Wasting | 1,122 |
| Nutrition | Low birth weight | 3,276 |
