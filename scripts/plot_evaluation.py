"""Plot the rolling evaluation on the included synthetic order records."""
from collections import defaultdict
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from demand_forecast import PROJECT_ROOT, build_forecast_rows, forecast_errors, load_daily_demand


def main():
    demand, lead_time = load_daily_demand(PROJECT_ROOT / "Orders.csv", PROJECT_ROOT / "Order_Items.csv", PROJECT_ROOT / "Products.csv")
    rows = build_forecast_rows(demand, lead_time)
    mae, wape = forecast_errors(rows)
    monthly = defaultdict(lambda: [0, 0.0])
    for row in rows:
        month = str(row["ds"])[:7] + "-01"
        monthly[month][0] += int(row["y"])
        monthly[month][1] += float(row["yhat"])
    # August has only three evaluated days after warm-up; use complete months.
    months = sorted(monthly)[1:]
    dates = [date.fromisoformat(month) for month in months]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none"})
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.5), gridspec_kw={"height_ratios": [2, 1]}, sharex=True)
    fig.subplots_adjust(top=.80, bottom=.18, left=.09, right=.97, hspace=.20)
    fig.text(.09, .945, "How well does a weekday baseline forecast demand?", fontsize=18, weight="bold")
    fig.text(.09, .895, f"Synthetic product 1 orders | Daily MAE: {mae:.2f} units | Daily WAPE: {wape:.1%}", fontsize=11)
    actual = [monthly[m][0] for m in months]
    predicted = [monthly[m][1] for m in months]
    axes[0].plot(dates, actual, color="#173e59", linewidth=2, label="Observed units")
    axes[0].plot(dates, predicted, color="#bb641f", linewidth=2, linestyle="--", label="Predicted units")
    axes[0].set_ylabel("Monthly total units")
    axes[0].set_ylim(bottom=0)
    axes[0].legend(frameon=False, ncol=2, loc="upper left")
    errors = [p-a for p,a in zip(predicted, actual)]
    axes[1].bar(dates, errors, width=22, color=["#bb641f" if e >= 0 else "#173e59" for e in errors])
    axes[1].axhline(0, color="#55616b", linewidth=.7)
    axes[1].set_ylabel("Predicted minus\nobserved units")
    axes[1].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#dae1e5", linewidth=.6)
        ax.set_axisbelow(True)
    fig.text(.09, .075, "Chart: complete evaluation months, Sep 2020 to Jan 2024. Error metrics: all evaluated days, including Aug 29-31.", fontsize=9, color="#44515c")
    fig.text(.09, .04, "Each daily prediction uses earlier observations only. Monthly aggregation smooths daily errors. No actual business data.", fontsize=9, color="#44515c")
    output = PROJECT_ROOT / "dashboards/demand_backtest.svg"
    output.parent.mkdir(exist_ok=True)
    fig.savefig(output)
    print(output)


if __name__ == "__main__":
    main()
