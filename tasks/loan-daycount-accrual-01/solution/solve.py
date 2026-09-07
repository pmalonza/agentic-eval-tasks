#!/usr/bin/env python3
"""Deterministic oracle for loan-daycount-accrual-01.

Same amortization/covenant/sweep mechanics as debt-covenant-runoff-01,
but interest accrues on an Actual/360 basis over a real 24-month calendar
(January 2027 - December 2028) instead of a flat annual-rate/12 monthly
fraction. This spans two different Februaries -- 2027 (28 days) and 2028
(29 days, a leap year) -- so a correct implementation must derive the
actual day count for each calendar month, not assume a fixed 30 days or
reuse a flat monthly fraction.

Usage: solve.py <output_dir>
Writes <output_dir>/answer.json and prints it to stdout.
"""

from __future__ import annotations

import calendar
import csv
import json
import sys
from pathlib import Path

STARTING_PRINCIPAL = 1_500_000.00
N_MONTHS = 24
SCHEDULED_PRINCIPAL = 62_500.00
BASE_ANNUAL_RATE = 0.072
ELEVATED_ANNUAL_RATE = 0.087
DAY_COUNT_DENOMINATOR = 360
MIN_CASH_THRESHOLD = 100_000.00
STARTING_CASH = 250_000.00
SWEEP_PCT = 0.50
CHECKPOINT_MONTHS = (6, 12, 18, 24)

START_YEAR, START_MONTH = 2027, 1


def calendar_month_for(month_index: int) -> tuple[int, int]:
    """1-indexed month_index -> (year, month) starting Jan 2027."""
    zero_based = (START_MONTH - 1) + (month_index - 1)
    year = START_YEAR + zero_based // 12
    month = zero_based % 12 + 1
    return year, month


def days_in_month(month_index: int) -> int:
    year, month = calendar_month_for(month_index)
    return calendar.monthrange(year, month)[1]


def load_fcf(data_dir: Path) -> dict[int, float]:
    fcf = {}
    with open(data_dir / "monthly_cash_flow.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            fcf[int(row["Month"])] = float(row["Free_Cash_Flow_Before_Debt_Service_USD"])
    return fcf


def simulate(fcf: dict[int, float]) -> dict:
    balance = STARTING_PRINCIPAL
    cash = STARTING_CASH
    current_annual_rate = BASE_ANNUAL_RATE

    total_interest = 0.0
    covenant_trigger_month = None
    payoff_month = None
    min_cash_balance = STARTING_CASH
    min_cash_month = 0
    checkpoint_balances: dict[int, float] = {}

    for month in range(1, N_MONTHS + 1):
        month_fcf = fcf[month]

        if balance > 0:
            days = days_in_month(month)
            daily_rate = current_annual_rate / DAY_COUNT_DENOMINATOR
            interest = balance * daily_rate * days
            scheduled_principal = min(SCHEDULED_PRINCIPAL, balance)
            debt_service = interest + scheduled_principal

            cash_available = cash + month_fcf - debt_service
            balance_after_scheduled = balance - scheduled_principal

            sweep = 0.0
            if cash_available > MIN_CASH_THRESHOLD:
                sweep = min(0.5 * (cash_available - MIN_CASH_THRESHOLD), balance_after_scheduled)

            balance = balance_after_scheduled - sweep
            cash = cash_available - sweep
            total_interest += interest

            if payoff_month is None and balance <= 1e-9:
                balance = 0.0
                payoff_month = month
        else:
            cash = cash + month_fcf

        if month_fcf < 0 and covenant_trigger_month is None:
            covenant_trigger_month = month
            current_annual_rate = ELEVATED_ANNUAL_RATE

        if cash < min_cash_balance:
            min_cash_balance = cash
            min_cash_month = month

        if month in CHECKPOINT_MONTHS:
            checkpoint_balances[month] = balance

    return {
        "covenant_trigger_month": covenant_trigger_month,
        "payoff_month": payoff_month,
        "total_interest_paid_usd": round(total_interest, 2),
        "month_6_balance_usd": round(checkpoint_balances[6], 2),
        "month_12_balance_usd": round(checkpoint_balances[12], 2),
        "month_18_balance_usd": round(checkpoint_balances[18], 2),
        "month_24_balance_usd": round(checkpoint_balances[24], 2),
        "month_24_cash_balance_usd": round(cash, 2),
        "min_cash_balance_usd": round(min_cash_balance, 2),
        "min_cash_month": min_cash_month,
    }


def main() -> int:
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    data_dir = Path(__file__).resolve().parent.parent / "environment" / "data"

    fcf = load_fcf(data_dir)
    result = simulate(fcf)

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "answer.json", "w") as fh:
        json.dump(result, fh, indent=2)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
