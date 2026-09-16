#!/usr/bin/env python3
"""Programmatic checks for kb-earned-contract-liability-01.

Compares the agent's answer.json against the golden answer.json (baked
from solution/solve.py). The load-bearing trap this task is built to
catch: a month is only "exposed" (generates loss forecast dollars) after
BOTH (a) the manufacturer's warranty has terminated, by whichever of its
own month or mile limit comes first, and (b) it is at or before the
VSC's own termination, again by whichever of ITS month or mile limit
comes first -- these two "whichever comes first" tests are independent
and do not have to resolve the same way (here the warranty is
mileage-bound at month 30 despite a nominal 36-month term, while the VSC
is time-bound at month 60 despite a 75,000-mile allowance that would not
be reached until month 75).

Two plausible failure modes were constructed and verified during
authoring: (a) ignoring the manufacturer's-warranty exclusion entirely
(traditional "age from sale" reserving), which overstates exposure by
double and produces a materially different Earned Contract schedule at
every checkpoint before final expiration; and (b) applying only the
month-based limit to the warranty and ignoring that its mileage limit is
reached first, which understates exposure by 6 months and shifts every
valuation checkpoint's earned/unearned split. Both are caught primarily
via the non-valuation fields (warranty_effective_expiration_month,
first_exposed_month, total_exposed_months, total_loss_forecast_usd) and
via the Month 36 and Month 48 valuation checkpoints, which diverge
under both bugs.

Never raises: a missing file, malformed JSON, or missing key scores that
field 0 rather than crashing the harness.

Usage: check_programmatic.py <agent_results_dir> [golden_dir]
Prints a JSON report to stdout: {"score": float in [0,1], "fields": {...}}
Always exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DOLLAR_TOLERANCE_ABSOLUTE = 5.0
PCT_TOLERANCE_ABSOLUTE = 0.5  # percentage points

EXACT_FIELDS = [
    "warranty_effective_expiration_month",
    "vsc_effective_expiration_month",
    "first_exposed_month",
    "total_exposed_months",
]
VALUATION_MONTHS = ["12", "24", "36", "48", "60"]
VALUATION_SUBFIELDS = ["earned_contract_pct", "unearned_contract_pct", "unearned_liability_usd"]


def _load_json_safe(path: Path) -> dict | None:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _exact_match(agent_value, golden_value) -> bool:
    try:
        return int(agent_value) == int(golden_value)
    except (TypeError, ValueError):
        return False


def _close(agent_value, golden_value, tolerance: float) -> bool:
    try:
        return abs(float(agent_value) - golden_value) <= tolerance
    except (TypeError, ValueError):
        return False


def score(agent_results_dir: Path, golden_dir: Path) -> dict:
    golden = _load_json_safe(golden_dir / "answer.json")
    if golden is None:
        raise RuntimeError(f"golden answer.json missing or malformed at {golden_dir}")

    agent = _load_json_safe(agent_results_dir / "answer.json")

    field_names = list(EXACT_FIELDS) + ["total_loss_forecast_usd"]
    for v in golden["valuation_results"]:
        for sub in VALUATION_SUBFIELDS:
            field_names.append(f"valuation_{v}.{sub}")

    if agent is None:
        fields = {name: False for name in field_names}
        return {"score": 0.0, "fields": fields, "note": "agent answer.json missing or malformed"}

    fields: dict[str, bool] = {}

    for field in EXACT_FIELDS:
        fields[field] = _exact_match(agent.get(field), golden[field])

    fields["total_loss_forecast_usd"] = _close(
        agent.get("total_loss_forecast_usd"), golden["total_loss_forecast_usd"], DOLLAR_TOLERANCE_ABSOLUTE
    )

    agent_valuations = agent.get("valuation_results") if isinstance(agent.get("valuation_results"), dict) else {}
    for v, golden_vals in golden["valuation_results"].items():
        agent_vals = agent_valuations.get(v) if isinstance(agent_valuations.get(v), dict) else {}
        for sub in VALUATION_SUBFIELDS:
            key = f"valuation_{v}.{sub}"
            if sub not in agent_vals:
                fields[key] = False
                continue
            tolerance = DOLLAR_TOLERANCE_ABSOLUTE if sub.endswith("_usd") else PCT_TOLERANCE_ABSOLUTE
            fields[key] = _close(agent_vals[sub], golden_vals[sub], tolerance)

    passed = sum(1 for v in fields.values() if v)
    total = len(field_names)
    return {"score": passed / total, "fields": fields}


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"score": 0.0, "fields": {}, "note": "usage: check_programmatic.py <agent_results_dir> [golden_dir]"}))
        return 0

    agent_results_dir = Path(sys.argv[1])
    golden_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / "solution"

    try:
        result = score(agent_results_dir, golden_dir)
    except Exception as exc:  # noqa: BLE001 - deliberately broad: this must never crash the harness
        result = {"score": 0.0, "fields": {}, "note": f"checker error: {exc}"}

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
