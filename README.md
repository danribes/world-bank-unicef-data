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

## Data Pipeline

The data is collected and enriched through the following pipeline:

1. **`get_world_bank_countries.py`** - Fetch 260+ countries from World Bank API
2. **`collect_gdp_data.py`** - Collect 70 years of GDP data (1955-2025)
3. **`add_public_debt_data.py`** - Add public debt metrics
4. **`add_fiscal_indicators.py`** - Add tax revenue, government expenses, fiscal balance, education spending
5. **`add_debt_ppp_icer.py`** - Calculate incremental cost-effectiveness ratio
6. **`convert_to_billions.py`** - Scale GDP values to billions for readability
7. **`add_poverty_data.py`** - Add poverty headcount ratios and Gini index
8. **`extract_unicef_data.py`** - Fetch and merge UNICEF mortality, nutrition, and child poverty data

### Intermediate Data Files

| File | Description |
|------|-------------|
| `world_bank_countries.csv` | Country directory (260+ countries) |
| `world_bank_gdp_data_70years.csv` | Base GDP data |
| `world_bank_gdp_data_with_icer.csv` | With ICER calculations |
| `world_bank_gdp_data_billions.csv` | Enriched, scaled to billions |
| `world_bank_gdp_data_billions.xlsx` | Excel version of above |
| `world_bank_gdp_data_with_poverty.xlsx` | Final dataset with all indicators |

## MCP Server

The `unicef-mcp-server/` directory contains a Node.js MCP (Model Context Protocol) server for querying UNICEF data in real-time via the SDMX API.

### Available Tools
- `list_dataflows` - List available UNICEF dataflows
- `get_indicators` - Get indicators for a dataflow
- `get_child_poverty_data` - Query child poverty by country/years
- `get_child_mortality_data` - Query mortality by country/years
- `get_nutrition_data` - Query nutrition by country/years
- `get_indicator_for_country` - Query specific indicator from any dataflow
- `search_indicators` - Keyword search across indicators

See [WORLD_BANK_MCP_SETUP.md](WORLD_BANK_MCP_SETUP.md) for setup instructions.

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
