# Wishing Star Demand Forecasting

## Purpose

This repository forecasts demand for Wishing Star product one and identifies stockout risk before procurement lead times are exhausted.

## Project specifications

### Demand forecasting

42 months of order history, 91% backtested accuracy, and a 3 week early stockout warning.

### Valuation engine

5 by 5 WACC sensitivity, validation for a valuation scenario above $23 billion, and a 1 click Morningstar style PDF report.

### Agile velocity

10,000 Monte Carlo trials, P50, P80, and P90 release milestones, plus RICE feature scoring.

Only the demand forecasting workflow is implemented in this repository. The valuation engine and agile velocity specifications are retained here as project requirements.

## Run the forecast

Run the script from the repository root:

```bash
python scripts/demand_forecast.py
```

The script reads `Orders.csv`, `Order_Items.csv`, and `Products.csv`. It writes `q4_demand_forecast_with_alerts.csv` with daily actual demand, a weekday baseline forecast, a forward supplier lead time total, and a stockout alert flag. It uses only the Python standard library.

## Data

The source data covers August 2020 through January 2024, which is 42 inclusive calendar months. Product one has a 21 day supplier lead time. An alert is raised when predicted demand over that period exceeds the 600 unit reorder limit.

## Repository layout

* `scripts/demand_forecast.py`: Forecast entrypoint and CSV export.
* `scripts/data_pipeline.sql`: PostgreSQL aggregation query for daily product demand and inventory status.
* `Orders.csv`, `Order_Items.csv`, `Products.csv`: Forecast inputs.
* `Inventory_Log.csv`: Inventory input for the SQL pipeline.
