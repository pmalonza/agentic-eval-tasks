#!/usr/bin/env python3
"""Deterministic oracle for debt-covenant-runoff-01.

Reads the monthly free-cash-flow series from environment/data/ and
simulates the loan month by month per the rules in loan_terms.md. The
fixed loan terms (principal, rates, thresholds) are scenario constants
that mirror loan_terms.md exactly -- only the free-cash-flow series is
read as data, since the terms document is prose meant for a human/agent
to read, not machine-parsed.

No network calls, no randomness, no wall-clock dependence: rerunning
this script reproduces answer.json byte-for-byte.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = TASK_ROOT / "environment" / "data"

# --- Loan terms (must match environment/data/loan_terms.md exactly) ---
STARTING_PRINCIPAL = 1_500_000.00
N_MONTHS = 24
SCHEDULED_PRINCIPAL = STARTING_PRINCIPAL / N_MONTHS  # 62,500.00
BASE_ANNUAL_RATE = 0.072
ELEVATED_ANNUAL_RATE = 0.087
MIN_CASH_THRESHOLD = 100_000.00
STARTING_CASH = 250_000.00
SWEEP_PCT = 0.50
CHECKPOINT_MONTHS = (6, 12, 18, 24)


def load_monthly_fcf(data_dir: Path) -> list[float]:
    with open(data_dir / "monthly_cash_flow.csv") as fh:
        rows = list(csv.DictReader(fh))
    rows.sort(key=lambda r: int(r["Month"]))
    fcf = [float(r["Free_Cash_Flow_Before_Debt_Service_USD"]) for r in rows]
    if len(fcf) != N_MONTHS:
        raise ValueError(f"expected {N_MONTHS} months of cash flow, found {len(fcf)}")
    return fcf


def simulate(fcf: list[float]) -> dict:
    balance = STARTING_PRINCIPAL
    cash = STARTING_CASH
    current_annual_rate = BASE_ANNUAL_RATE

    covenant_trigger_month: int | None = None
    payoff_month: int | None = None
    total_interest = 0.0
    checkpoints: dict[int, dict[str, float]] = {}
    min_cash_balance = STARTING_CASH
    min_cash_month = 0

    for month in range(1, N_MONTHS + 1):
        month_fcf = fcf[month - 1]

        if balance <= 0.0:
            # Loan already fully repaid: no further debt service, FCF
            # simply accumulates into cash.
            cash += month_fcf
        else:
            monthly_rate = current_annual_rate / 12.0
            interest = balance * monthly_rate
            scheduled_principal = min(SCHEDULED_PRINCIPAL, balance)
            balance_after_scheduled = balance - scheduled_principal
            debt_service = interest + scheduled_principal

            cash_available = cash + month_fcf - debt_service
            sweep = 0.0
            if cash_available > MIN_CASH_THRESHOLD:
                excess = cash_available - MIN_CASH_THRESHOLD
                sweep = min(SWEEP_PCT * excess, balance_after_scheduled)
            balance = balance_after_scheduled - sweep
            cash = cash_available - sweep

            total_interest += interest

            if balance <= 0.0 and payoff_month is None:
                payoff_month = month

            # Covenant check: a negative-FCF month steps the rate up
            # starting NEXT month, one-time and permanent.
            if month_fcf < 0 and covenant_trigger_month is None:
                covenant_trigger_month = month
                current_annual_rate = ELEVATED_ANNUAL_RATE

        if cash < min_cash_balance:
            min_cash_balance = cash
            min_cash_month = month

        if month in CHECKPOINT_MONTHS:
            checkpoints[month] = {"balance": balance, "cash": cash}

    return {
        "covenant_trigger_month": covenant_trigger_month,
        "payoff_month": payoff_month,
        "total_interest_paid_usd": round(total_interest, 2),
        "month_6_balance_usd": round(checkpoints[6]["balance"], 2),
        "month_12_balance_usd": round(checkpoints[12]["balance"], 2),
        "month_18_balance_usd": round(checkpoints[18]["balance"], 2),
        "month_24_balance_usd": round(checkpoints[24]["balance"], 2),
        "month_24_cash_balance_usd": round(checkpoints[24]["cash"], 2),
        "min_cash_balance_usd": round(min_cash_balance, 2),
        "min_cash_month": min_cash_month,
    }


def main(output_dir: str) -> None:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    fcf = load_monthly_fcf(DATA_DIR)
    answer = simulate(fcf)

    with open(out_path / "answer.json", "w") as fh:
        json.dump(answer, fh, indent=2)
        fh.write("\n")

    print(json.dumps(answer, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: solve.py <output_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
