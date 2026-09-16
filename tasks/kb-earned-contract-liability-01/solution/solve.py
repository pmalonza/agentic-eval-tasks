#!/usr/bin/env python3
"""Deterministic oracle for kb-earned-contract-liability-01.

Implements two components of the Kerper-Bowron Method (Kerper and Bowron
2026, "The Kerper-Bowron Method: A Foundational Change for Service
Contract Claim Estimation and Accounting", Risks 14(3):44,
https://doi.org/10.3390/risks14030044, CC BY 4.0):

1. Exposure exclusion (paper Section 6.1, adapted to a flat assumed
   mileage rate instead of the paper's own probabilistic lognormal
   mileage-distribution approach -- see the task README for why): a
   month is exposed only after the manufacturer's warranty has
   terminated (by whichever of its month or mile limit comes first) and
   at or before the VSC's own termination (by whichever of its own month
   or mile limit comes first).
2. The Earned Contract formula (paper Section 2, Equations 1-6): given
   the monthly loss-forecast stream, compute the total loss forecast,
   each month's Earned Contract fraction, cumulative earned, and
   unearned.

Usage: solve.py <output_dir>
Writes <output_dir>/answer.json and prints it to stdout.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

WARRANTY_TERM_MONTHS = 36
WARRANTY_TERM_MILES = 30_000
VSC_TERM_MONTHS = 60
VSC_TERM_MILES = 75_000
ASSUMED_MILES_PER_MONTH = 1_000
PURE_PREMIUM_PER_EXPOSED_MONTH = 50.00
GROSS_PREMIUM = 1_800.00

VALUATION_MONTHS = (12, 24, 36, 48, 60)


def _month_limit_from_miles(term_miles: int) -> int:
    """First month by which the given mileage limit is reached, at the
    assumed flat mileage rate (ceiling: mileage is reached partway
    through the month in which cumulative miles first meets the limit)."""
    return math.ceil(term_miles / ASSUMED_MILES_PER_MONTH)


def compute() -> dict:
    warranty_mile_month = _month_limit_from_miles(WARRANTY_TERM_MILES)
    warranty_expiration_month = min(WARRANTY_TERM_MONTHS, warranty_mile_month)

    vsc_mile_month = _month_limit_from_miles(VSC_TERM_MILES)
    vsc_expiration_month = min(VSC_TERM_MONTHS, vsc_mile_month)

    first_exposed_month = warranty_expiration_month + 1
    last_exposed_month = vsc_expiration_month
    total_exposed_months = max(0, last_exposed_month - warranty_expiration_month)

    e = vsc_expiration_month  # months until final expiration, per the paper's notation

    f = [0.0] * (e + 1)  # 1-indexed; f[0] unused
    for month in range(1, e + 1):
        if first_exposed_month <= month <= last_exposed_month:
            f[month] = PURE_PREMIUM_PER_EXPOSED_MONTH

    a = sum(f[1:])

    ec = [0.0] * (e + 1)
    for month in range(1, e + 1):
        ec[month] = (f[month] / a) if a else 0.0

    cumulative_ec = [0.0] * (e + 1)
    running = 0.0
    for month in range(1, e + 1):
        running += ec[month]
        cumulative_ec[month] = running

    valuation_results = {}
    for v in VALUATION_MONTHS:
        if v > e:
            continue
        ec_v = cumulative_ec[v]
        uec_v = 1.0 - ec_v
        valuation_results[str(v)] = {
            "earned_contract_pct": round(ec_v * 100, 4),
            "unearned_contract_pct": round(uec_v * 100, 4),
            "unearned_liability_usd": round(uec_v * GROSS_PREMIUM, 2),
        }

    return {
        "warranty_effective_expiration_month": warranty_expiration_month,
        "vsc_effective_expiration_month": vsc_expiration_month,
        "first_exposed_month": first_exposed_month,
        "total_exposed_months": total_exposed_months,
        "total_loss_forecast_usd": round(a, 2),
        "valuation_results": valuation_results,
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
