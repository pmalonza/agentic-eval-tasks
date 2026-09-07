#!/usr/bin/env python3
"""Deterministic oracle for tranche-waterfall-runoff-01.

Simulates a three-tranche (Senior / Mezzanine / Subordinated) 24-month
credit facility with a strict payment waterfall, a PIK-vs-cash toggle on
the Mezzanine tranche, and a Subordinated tranche that only converts from
PIK to cash-pay once both senior tranches are fully retired. See
environment/data/loan_terms.md for the full rule set this implements.

Usage: solve.py <output_dir>
Writes <output_dir>/answer.json and prints it to stdout.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

A_PRINCIPAL = 2_000_000.00
A_SCHEDULED_PRINCIPAL = A_PRINCIPAL / 24  # 83,333.33...
A_BASE_ANNUAL_RATE = 0.08
A_ELEVATED_ANNUAL_RATE = 0.09

B_PRINCIPAL = 800_000.00
B_ANNUAL_RATE = 0.11

C_PRINCIPAL = 500_000.00
C_ANNUAL_RATE = 0.14

MIN_CASH_THRESHOLD = 150_000.00
STARTING_CASH = 400_000.00
SWEEP_PCT = 0.50
N_MONTHS = 24
CHECKPOINT_MONTH = 12


def load_fcf(data_dir: Path) -> dict[int, float]:
    fcf = {}
    with open(data_dir / "monthly_cash_flow.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            fcf[int(row["Month"])] = float(row["Free_Cash_Flow_Before_Debt_Service_USD"])
    return fcf


def simulate(fcf: dict[int, float]) -> dict:
    a_bal = A_PRINCIPAL
    b_bal = B_PRINCIPAL
    c_bal = C_PRINCIPAL
    cash = STARTING_CASH
    a_rate = A_BASE_ANNUAL_RATE

    covenant_trigger_month = None
    forced_pik_month = None  # the single month Mezz is forced into PIK
    a_payoff_month = None
    b_payoff_month = None
    c_conversion_month = None
    c_payoff_month = None

    total_a_cash_interest = 0.0
    total_b_cash_interest = 0.0
    total_b_pik_interest = 0.0
    total_c_pik_interest = 0.0
    total_c_cash_interest = 0.0

    min_cash_balance = STARTING_CASH
    min_cash_month = 0
    checkpoint_balances: dict[int, tuple[float, float, float]] = {}

    for month in range(1, N_MONTHS + 1):
        cash += fcf[month]

        # --- Tranche A (Senior): cash-pay interest + scheduled principal, first priority ---
        a_interest = a_bal * (a_rate / 12) if a_bal > 0 else 0.0
        a_sched = min(A_SCHEDULED_PRINCIPAL, a_bal) if a_bal > 0 else 0.0
        cash -= (a_interest + a_sched)
        a_bal -= a_sched
        total_a_cash_interest += a_interest

        # --- Tranche B (Mezzanine): interest-only, PIK-vs-cash toggle, second priority ---
        b_interest = b_bal * (B_ANNUAL_RATE / 12) if b_bal > 0 else 0.0
        if b_bal > 0:
            if month == forced_pik_month:
                b_bal += b_interest
                total_b_pik_interest += b_interest
            elif cash >= b_interest:
                cash -= b_interest
                total_b_cash_interest += b_interest
            else:
                b_bal += b_interest
                total_b_pik_interest += b_interest

        # --- Tranche C (Subordinated): PIK until A and B are both fully retired (as of
        # the start of this month), then permanently cash-pay interest-only ---
        c_converted = a_bal <= 1e-9 and b_bal <= 1e-9
        if c_converted and c_conversion_month is None and c_bal > 0:
            c_conversion_month = month
        c_interest = c_bal * (C_ANNUAL_RATE / 12) if c_bal > 0 else 0.0
        if c_bal > 0:
            if c_converted:
                cash -= c_interest
                total_c_cash_interest += c_interest
            else:
                c_bal += c_interest
                total_c_pik_interest += c_interest

        # --- Cash sweep: waterfall priority A -> B -> C (C only once converted) ---
        if cash > MIN_CASH_THRESHOLD:
            sweep = 0.5 * (cash - MIN_CASH_THRESHOLD)
            if a_bal > 0:
                applied = min(sweep, a_bal)
                a_bal -= applied
                cash -= applied
            elif b_bal > 0:
                applied = min(sweep, b_bal)
                b_bal -= applied
                cash -= applied
            elif c_bal > 0 and c_converted:
                applied = min(sweep, c_bal)
                c_bal -= applied
                cash -= applied

        if a_bal <= 1e-9:
            a_bal = 0.0
            if a_payoff_month is None:
                a_payoff_month = month
        if b_bal <= 1e-9:
            b_bal = 0.0
            if b_payoff_month is None:
                b_payoff_month = month
        if c_bal <= 1e-9 and c_converted:
            c_bal = 0.0
            if c_payoff_month is None:
                c_payoff_month = month

        if fcf[month] < 0 and covenant_trigger_month is None:
            covenant_trigger_month = month
            a_rate = A_ELEVATED_ANNUAL_RATE
            forced_pik_month = month + 1

        if cash < min_cash_balance:
            min_cash_balance = cash
            min_cash_month = month

        if month == CHECKPOINT_MONTH:
            checkpoint_balances[CHECKPOINT_MONTH] = (a_bal, b_bal, c_bal)

    return {
        "covenant_trigger_month": covenant_trigger_month,
        "tranche_a_payoff_month": a_payoff_month,
        "tranche_b_payoff_month": b_payoff_month,
        "tranche_c_conversion_month": c_conversion_month,
        "tranche_c_payoff_month": c_payoff_month,
        "total_tranche_a_cash_interest_usd": round(total_a_cash_interest, 2),
        "total_tranche_b_cash_interest_usd": round(total_b_cash_interest, 2),
        "total_tranche_b_pik_interest_usd": round(total_b_pik_interest, 2),
        "total_tranche_c_pik_interest_usd": round(total_c_pik_interest, 2),
        "total_tranche_c_cash_interest_usd": round(total_c_cash_interest, 2),
        "month_12_tranche_a_balance_usd": round(checkpoint_balances[12][0], 2),
        "month_12_tranche_b_balance_usd": round(checkpoint_balances[12][1], 2),
        "month_12_tranche_c_balance_usd": round(checkpoint_balances[12][2], 2),
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
