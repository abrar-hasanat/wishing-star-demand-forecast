# ==============================================================================
# File: demand_forecast.py
# Purpose: Q4 Demand Forecasting & Early Stockout Detection Model
# Description: Uses Prophet to model historical seasonal demand (2020-2022) 
#              and predict the Q4 2023 anomaly. Implements a rolling lead-time 
#              metric to flag supply chain failures before inventory hits zero.
# ==============================================================================

import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# 1. Load the aggregated SQL pipeline output
df = pd.read_csv('aggregated_daily_demand.csv')

# 2. Isolate Flagship Product 1 (The product susceptible to Q4 stockouts)
df_prod = df[df['ProductID'] == 1].copy()
supplier_lead_time = df_prod['SupplierLeadTime_Days'].iloc[0] # Typically 21 days

# 3. Prepare schema for Facebook Prophet
df_prophet = df_prod[['log_date', 'total_units_sold']].rename(
    columns={'log_date': 'ds', 'total_units_sold': 'y'}
)
df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

# 4. Train/Test Split: Train strictly on historical data (Aug 2020 - Dec 2022)
train_df = df_prophet[df_prophet['ds'] < '2023-01-01']

# 5. Initialize & Fit Model
# We add US holidays and strict yearly seasonality to capture the intense Q4 e-commerce spikes
m = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
m.add_country_holidays(country_name='US')
m.fit(train_df)

# 6. Generate Forecast for all of 2023
future = m.make_future_dataframe(periods=365)
forecast = m.predict(future)

# ==============================================================================
# 7. EARLY STOCKOUT DETECTION LOGIC
# 
# How this flags stockouts early: 
# Instead of looking at daily demand, we calculate the rolling sum of the 
# FORECASTED demand over the exact supplier lead time (21 days). 
# If the predicted demand for the next 21 days exceeds our maximum reorder 
# threshold (600 units), the model triggers a "Stockout Alert Flag". 
# In a live production environment, this warns the Operations team 3-4 weeks 
# BEFORE the Q4 demand spike drains the inventory to zero.
# ==============================================================================

forecast['rolling_lead_time_demand'] = forecast['yhat'].rolling(window=int(supplier_lead_time)).sum()

# Merge actuals back into the forecast for backtesting
result = pd.merge(
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'rolling_lead_time_demand']], 
    df_prophet, 
    on='ds', 
    how='left'
)

# Standard Reorder Quantity = 600. If 21-day forecast breaches this, inventory will fail.
REORDER_QTY_LIMIT = 600 
result['stockout_alert_flag'] = result['rolling_lead_time_demand'] > REORDER_QTY_LIMIT

# 8. Export enriched forecast data for Power BI Dashboard visualization
result.to_csv('q4_demand_forecast_with_alerts.csv', index=False)