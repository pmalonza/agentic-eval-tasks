#!/usr/bin/env python3
"""Deterministic oracle for fpa-variance-analysis-01.

Reads the same three files the agent is given and computes the variance
bridge and the corrected product-line attribution from scratch -- no
value here is hand-typed; every number is derived from the source CSVs.
No network calls, no randomness, no wall-clock dependence: rerunning this
script reproduces answer.json byte-for-byte.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = TASK_ROOT / "environment" / "data"


def _f(row: dict, key: str) -> float:
    return float(row[key])


def load_pnl(data_dir: Path) -> dict:
    with open(data_dir / "q2_budget_vs_actual.csv") as fh:
        rows = list(csv.DictReader(fh))
    return {(r["Product"], r["Period"]): r for r in rows}


def load_allocation(data_dir: Path) -> list[dict]:
    with open(data_dir / "cost_allocation_schedule.csv") as fh:
        return list(csv.DictReader(fh))


def gross_margin_pct(row: dict) -> float:
    return _f(row, "Gross_Profit") / _f(row, "Revenue") * 100.0


def volume_effect(budget_row: dict, actual_row: dict) -> float:
    """Net GP impact of the volume change alone (revenue effect minus the
    proportional direct-cost effect), holding price and per-unit cost at
    budget."""
    vol_b, price_b = _f(budget_row, "Volume_Units"), _f(budget_row, "Price_Per_Unit")
    vol_a = _f(actual_row, "Volume_Units")
    dcost_per_unit_b = _f(budget_row, "Direct_Cost") / vol_b
    revenue_effect = (vol_a - vol_b) * price_b
    cost_effect = (vol_a - vol_b) * dcost_per_unit_b
    return revenue_effect - cost_effect


def price_effect(budget_row: dict, actual_row: dict) -> float:
    """Net GP impact of the price change alone, at actual volume."""
    price_b, price_a = _f(budget_row, "Price_Per_Unit"), _f(actual_row, "Price_Per_Unit")
    vol_a = _f(actual_row, "Volume_Units")
    return (price_a - price_b) * vol_a


def find_anomalous_allocation_row(alloc_rows: list[dict], a_share: float) -> dict:
    """Identify the cost-pool row whose allocation is NOT pro-rata by
    revenue share, i.e. was booked to one product line only. Detected by
    comparison to what a pro-rata allocation would look like, not by
    matching a hardcoded row name.
    """
    candidates = [r for r in alloc_rows if r["Allocation_Basis"].strip()]
    anomalous = []
    for r in candidates:
        amount = _f(r, "Total_Amount")
        if amount <= 0:
            continue
        actual_a_share_of_row = _f(r, "Product_A_Allocated") / amount
        if abs(actual_a_share_of_row - a_share) > 0.01:
            anomalous.append(r)
    if len(anomalous) != 1:
        raise ValueError(f"expected exactly one non-pro-rata allocation row, found {len(anomalous)}")
    return anomalous[0]


def main(output_dir: str) -> None:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    pnl = load_pnl(DATA_DIR)
    alloc = load_allocation(DATA_DIR)

    budget_a, actual_a = pnl[("Product A", "Budget")], pnl[("Product A", "Actual")]
    budget_b, actual_b = pnl[("Product B", "Budget")], pnl[("Product B", "Actual")]
    budget_t, actual_t = pnl[("Total", "Budget")], pnl[("Total", "Actual")]

    total_gm_miss_points = gross_margin_pct(budget_t) - gross_margin_pct(actual_t)
    total_gp_variance_usd = _f(actual_t, "Gross_Profit") - _f(budget_t, "Gross_Profit")

    a_miss_booked = gross_margin_pct(budget_a) - gross_margin_pct(actual_a)
    b_miss_booked = gross_margin_pct(budget_b) - gross_margin_pct(actual_b)

    a_rev_actual, b_rev_actual = _f(actual_a, "Revenue"), _f(actual_b, "Revenue")
    total_rev_actual = a_rev_actual + b_rev_actual
    a_share, b_share = a_rev_actual / total_rev_actual, b_rev_actual / total_rev_actual

    onetime_row = find_anomalous_allocation_row(alloc, a_share)
    one_time_cost_usd = _f(onetime_row, "Total_Amount")
    one_time_booked_a = _f(onetime_row, "Product_A_Allocated")
    one_time_booked_b = _f(onetime_row, "Product_B_Allocated")
    one_time_corrected_a = one_time_cost_usd * a_share
    one_time_corrected_b = one_time_cost_usd * b_share

    a_oh_corrected = _f(actual_a, "Allocated_Overhead") - one_time_booked_a + one_time_corrected_a
    b_oh_corrected = _f(actual_b, "Allocated_Overhead") - one_time_booked_b + one_time_corrected_b

    a_gp_corrected = a_rev_actual - _f(actual_a, "Direct_Cost") - a_oh_corrected
    b_gp_corrected = b_rev_actual - _f(actual_b, "Direct_Cost") - b_oh_corrected
    a_gm_corrected = a_gp_corrected / a_rev_actual * 100.0
    b_gm_corrected = b_gp_corrected / b_rev_actual * 100.0

    a_miss_corrected = gross_margin_pct(budget_a) - a_gm_corrected
    b_miss_corrected = gross_margin_pct(budget_b) - b_gm_corrected

    volume_total = volume_effect(budget_a, actual_a) + volume_effect(budget_b, actual_b)
    price_total = price_effect(budget_a, actual_a) + price_effect(budget_b, actual_b)
    overhead_total = -(_f(actual_t, "Allocated_Overhead") - _f(budget_t, "Allocated_Overhead"))

    drivers = {"volume": volume_total, "price": price_total, "overhead": overhead_total}
    largest_single_driver = max(drivers, key=lambda k: abs(drivers[k]))

    recommended_focus_product = "Product A" if a_miss_corrected > b_miss_corrected else "Product B"

    answer = {
        "total_gm_miss_points": round(total_gm_miss_points, 2),
        "total_gp_variance_usd": round(total_gp_variance_usd, 2),
        "product_a_miss_points_as_booked": round(a_miss_booked, 2),
        "product_b_miss_points_as_booked": round(b_miss_booked, 2),
        "product_a_miss_points_corrected": round(a_miss_corrected, 2),
        "product_b_miss_points_corrected": round(b_miss_corrected, 2),
        "largest_single_driver": largest_single_driver,
        "one_time_cost_usd": round(one_time_cost_usd, 2),
        "one_time_cost_corrected_product_a_usd": round(one_time_corrected_a, 2),
        "one_time_cost_corrected_product_b_usd": round(one_time_corrected_b, 2),
        "recommended_focus_product": recommended_focus_product,
    }

    with open(out_path / "answer.json", "w") as fh:
        json.dump(answer, fh, indent=2)
        fh.write("\n")

    print(json.dumps(answer, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: solve.py <output_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
