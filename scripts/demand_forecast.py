"""Backtest a weekday demand baseline on synthetic order history."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ORDER_HISTORY_MONTHS = 42
MIN_TRAINING_DAYS = 28
REORDER_QTY_LIMIT = 600


def parse_args() -> argparse.Namespace:
    """Return command line options for the forecast export."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-r", dest="orders", type=Path, default=PROJECT_ROOT / "Orders.csv"
    )
    parser.add_argument(
        "-i", dest="order_items", type=Path, default=PROJECT_ROOT / "Order_Items.csv"
    )
    parser.add_argument(
        "-p", dest="products", type=Path, default=PROJECT_ROOT / "Products.csv"
    )
    parser.add_argument(
        "-o", dest="output",
        type=Path,
        default=PROJECT_ROOT / "q4_demand_forecast_with_alerts.csv",
    )
    return parser.parse_args()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file or raise a clear error when it is unavailable."""
    if not path.is_file():
        raise FileNotFoundError(f"Required input file was not found: {path}")
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def month_count(dates: Iterable[date]) -> int:
    """Return the number of inclusive calendar months represented by dates."""
    first, last = min(dates), max(dates)
    return (last.year - first.year) * 12 + last.month - first.month + 1


def load_daily_demand(
    orders_path: Path, order_items_path: Path, products_path: Path
) -> tuple[dict[date, int], int]:
    """Aggregate product one order quantities by calendar date."""
    order_dates = {
        row["OrderID"]: datetime.fromisoformat(row["OrderDate"]).date()
        for row in read_csv_rows(orders_path)
    }
    lead_times = {
        int(row["ProductID"]): int(row["SupplierLeadTime_Days"])
        for row in read_csv_rows(products_path)
    }
    demand: dict[date, int] = defaultdict(int)
    for row in read_csv_rows(order_items_path):
        if int(row["ProductID"]) == 1:
            demand[order_dates[row["OrderID"]]] += int(row["Quantity"])
    if not demand:
        raise ValueError("No product one demand records were found.")
    return dict(demand), lead_times[1]


def weekday_averages(demand: dict[date, int]) -> dict[int, float]:
    """Calculate weekday means, including dates with no orders."""
    totals: dict[int, int] = defaultdict(int)
    counts: dict[int, int] = defaultdict(int)
    sale_date = min(demand)
    while sale_date <= max(demand):
        totals[sale_date.weekday()] += demand.get(sale_date, 0)
        counts[sale_date.weekday()] += 1
        sale_date += timedelta(days=1)
    return {weekday: totals[weekday] / counts[weekday] for weekday in totals}


def build_forecast_rows(demand: dict[date, int], lead_time: int) -> list[dict[str, object]]:
    """Predict each day using earlier dates, after a 28-day warm-up.

    The lead-time check compares expected demand with a fixed reorder threshold.
    It is not a stockout prediction: on-hand stock and incoming orders are absent.
    Its full horizon is calculated even at the sample end.
    """
    if lead_time <= 0:
        raise ValueError("Supplier lead time must be positive.")
    first_date, last_date = min(demand), max(demand)
    dates = []
    current_date = first_date
    while current_date <= last_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    totals: dict[int, int] = defaultdict(int)
    counts: dict[int, int] = defaultdict(int)
    rows: list[dict[str, object]] = []
    for index, sale_date in enumerate(dates):
        if index >= MIN_TRAINING_DAYS:
            averages = {day: totals[day] / counts[day] for day in range(7)}
            lead_time_demand = sum(
                averages[(sale_date + timedelta(days=offset)).weekday()]
                for offset in range(lead_time)
            )
            rows.append({
                "ds": sale_date.isoformat(),
                "y": demand.get(sale_date, 0),
                "yhat": round(averages[sale_date.weekday()], 2),
                "rolling_lead_time_demand": round(lead_time_demand, 2),
                "reorder_threshold_exceeded": lead_time_demand > REORDER_QTY_LIMIT,
            })
        totals[sale_date.weekday()] += demand.get(sale_date, 0)
        counts[sale_date.weekday()] += 1
    if not rows:
        raise ValueError("More than 28 calendar days are required for evaluation.")
    return rows


def forecast_errors(rows: list[dict[str, object]]) -> tuple[float, float | None]:
    """Return measured MAE and WAPE across rolling-origin predictions."""
    absolute_error = sum(abs(float(row["y"]) - float(row["yhat"])) for row in rows)
    actual_total = sum(float(row["y"]) for row in rows)
    return absolute_error / len(rows), absolute_error / actual_total if actual_total else None


def write_forecast(rows: list[dict[str, object]], output_path: Path) -> None:
    """Write forecast rows to a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Run the forecast export."""
    args = parse_args()
    demand, lead_time = load_daily_demand(args.orders, args.order_items, args.products)
    history_months = month_count(demand)
    if history_months != ORDER_HISTORY_MONTHS:
        raise ValueError(
            f"Expected {ORDER_HISTORY_MONTHS} months of order history, found {history_months}."
        )
    rows = build_forecast_rows(demand, lead_time)
    write_forecast(rows, args.output)
    mae, wape = forecast_errors(rows)
    wape_text = f"{wape:.1%}" if wape is not None else "undefined (zero observed demand)"
    print(
        f"Wrote {args.output} from {history_months} months of history. "
        f"Rolling-origin MAE: {mae:.2f} units; WAPE: {wape_text}. "
        f"Supplier lead-time assumption: {lead_time} days. "
        "Synthetic demonstration; no verified stockout-warning lead time."
    )


if __name__ == "__main__":
    main()
