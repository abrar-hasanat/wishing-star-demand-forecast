# Wishing Star Demand Forecasting

## Purpose

This repository demonstrates a demand-forecasting workflow modeled on the inventory-planning needs of Wishing Star by Shantu. The model uses 42 months of synthetic order history to identify stockout risk before procurement lead times are exhausted.

## Project scope

The workflow:

- Aggregates order and inventory data for product-level demand analysis.
- Builds a weekday-baseline demand forecast.
- Calculates expected demand across the supplier lead-time window.
- Flags stockout risk when expected demand exceeds the reorder threshold.

The model flagged stockout risk three weeks before the simulated peak Q4 demand period.

## Synthetic data notice

All customer, order, product, transaction, and inventory data in this repository is synthetic and was created solely to demonstrate the forecasting workflow. No production data from Wishing Star by Shantu or any other business is included. Any resemblance to real people, customers, transactions, products, organizations, or events is purely coincidental.

## Run the forecast

Run the script from the repository root:

```bash
python scripts/demand_forecast.py
```

The script reads `Orders.csv`, `Order_Items.csv`, and `Products.csv`. It writes `q4_demand_forecast_with_alerts.csv` with daily actual demand, a weekday baseline forecast, a forward supplier lead-time total, and a stockout alert flag. It uses only the Python standard library.

## Data

The synthetic dataset covers August 2020 through January 2024, representing 42 inclusive calendar months. Product one uses a 21-day supplier lead time. An alert is raised when predicted demand over that period exceeds the 600-unit reorder limit.

## Repository layout

- `scripts/demand_forecast.py`: Forecast entry point and CSV export.
- `scripts/data_pipeline.sql`: PostgreSQL aggregation query for daily product demand and inventory status.
- `Customers.csv`, `Orders.csv`, `Order_Items.csv`, `Products.csv`, and `Inventory_Log.csv`: Synthetic demonstration inputs.
- `dashboards/`: Dashboard screenshots.
