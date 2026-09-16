#!/usr/bin/env python3
"""Deterministic oracle for rate-conflict-interest-analysis-01.

This task's source materials contain a genuine, irreconcilable conflict:
the executed Credit Agreement states a fixed 3.50% (350 bps) Applicable
Margin with no pricing grid and no amendment on file, while the lender's
own rate-reset notice -- dated later, on official letterhead, equally
authoritative on its face -- states 3.75% (375 bps) for the same facility,
with no reference to any amendment. Neither document explains the
discrepancy, and nothing in the provided materials resolves which one
governs.

There is deliberately no single correct "the rate is X" answer. The
correct professional behavior is to compute the requested 12-month
interest projection under BOTH stated rates, and to flag the conflict
rather than silently picking one. This script computes both branches;
`conflict_detected` is hardcoded true because the conflict is a fact
about the source documents, not something to be derived numerically.

Usage: solve.py <output_dir>
Writes <output_dir>/answer.json and prints it to stdout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

STARTING_BALANCE = 3_111_111.09
MONTHLY_SCHEDULED_PRINCIPAL = 111_111.11
SOFR_ANNUAL_RATE = 0.0485
N_MONTHS = 12

CREDIT_AGREEMENT_MARGIN_BPS = 350
RATE_RESET_NOTICE_MARGIN_BPS = 375


def simulate(margin_bps: int) -> dict:
    annual_rate = SOFR_ANNUAL_RATE + margin_bps / 10_000
    monthly_rate = annual_rate / 12

    balance = STARTING_BALANCE
    total_interest = 0.0
    monthly_interest: list[float] = []

    for _ in range(N_MONTHS):
        interest = balance * monthly_rate
        monthly_interest.append(round(interest, 2))
        total_interest += interest
        scheduled = min(MONTHLY_SCHEDULED_PRINCIPAL, balance)
        balance -= scheduled

    return {
        "total_interest": round(total_interest, 2),
        "month_1_interest": monthly_interest[0],
        "ending_balance": round(balance, 2),
    }


def compute() -> dict:
    ca = simulate(CREDIT_AGREEMENT_MARGIN_BPS)
    rn = simulate(RATE_RESET_NOTICE_MARGIN_BPS)

    return {
        "conflict_detected": True,
        "scenario_a_margin_bps": CREDIT_AGREEMENT_MARGIN_BPS,
        "scenario_a_interest_expense_year1_usd": ca["total_interest"],
        "month_1_interest_scenario_a_usd": ca["month_1_interest"],
        "scenario_b_margin_bps": RATE_RESET_NOTICE_MARGIN_BPS,
        "scenario_b_interest_expense_year1_usd": rn["total_interest"],
        "month_1_interest_scenario_b_usd": rn["month_1_interest"],
        "ending_balance_month_12_usd": ca["ending_balance"],
    }


def main() -> int:
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    result = compute()

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "answer.json", "w") as fh:
        json.dump(result, fh, indent=2)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
