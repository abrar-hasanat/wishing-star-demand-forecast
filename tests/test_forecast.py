"""Check time separation and complete lead-time calculations."""
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from demand_forecast import build_forecast_rows, weekday_averages, forecast_errors


class ForecastTests(unittest.TestCase):
    def test_future_demand_does_not_change_earlier_predictions(self):
        start = date(2024, 1, 1)
        history = {start + timedelta(days=i): 10 for i in range(60)}
        changed = dict(history)
        changed[start + timedelta(days=40)] = 10000
        a = build_forecast_rows(history, 21)
        b = build_forecast_rows(changed, 21)
        for left, right in zip(a, b):
            if left['ds'] <= (start + timedelta(days=40)).isoformat():
                self.assertEqual(left['yhat'], right['yhat'])
                self.assertEqual(left['rolling_lead_time_demand'], right['rolling_lead_time_demand'])

    def test_last_row_keeps_the_full_horizon(self):
        start = date(2024, 1, 1)
        rows = build_forecast_rows({start + timedelta(days=i): 10 for i in range(40)}, 21)
        self.assertEqual(rows[-1]['rolling_lead_time_demand'], 210)
        self.assertEqual(forecast_errors(rows), (0.0, 0.0))

    def test_zero_order_dates_enter_the_average(self):
        self.assertEqual(weekday_averages({date(2024, 1, 1): 14, date(2024, 1, 15): 7})[0], 7)

    def test_error_is_calculated_from_observations(self):
        self.assertEqual(forecast_errors([{'y': 10, 'yhat': 8}, {'y': 20, 'yhat': 24}]), (3, 0.2))


if __name__ == '__main__':
    unittest.main()
