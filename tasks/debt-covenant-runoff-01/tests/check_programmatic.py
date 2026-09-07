#!/usr/bin/env python3
"""Programmatic checks for debt-covenant-runoff-01.

Compares the agent's answer.json against the golden answer.json (baked
from solution/solve.py). Unlike a typical percentage-tolerance financial
check, this task's failure modes are SMALL, systematic timing errors
(e.g. applying the covenant rate one month early shifts total interest
by only ~1.4%, about $1,145) that don't scale with each field's own
magnitude -- a percentage tolerance large enough to be safe on a small
field (like total interest, ~$84k) is loose enough to hide the same
absolute-dollar bug on a larger field (like ending cash, ~$1.2M). So
dollar fields use a flat $25 absolute tolerance instead: every field in
this simulation should match to within a few cents if genuinely computed
correctly (rounding only the final reported values, per the prompt), so
$25 comfortably covers legitimate rounding while still catching a
~$1,145 systematic error on any field, regardless of that field's own
size. Integer/null outcome fields (covenant_trigger_month, payoff_month,
min_cash_month) require an exact match; these are discrete facts about
the schedule, not estimates.

Never raises: a missing file, malformed JSON, or missing key scores
that field 0 rather than crashing the harness.

Usage: check_programmatic.py <agent_results_dir> [golden_dir]
Prints a JSON report to stdout: {"score": float in [0,1], "fields": {...}}
Always exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DOLLAR_TOLERANCE_ABSOLUTE = 25.0  # flat, not a percentage -- see module docstring

DOLLAR_FIELDS = [
    "total_interest_paid_usd",
    "month_6_balance_usd",
    "month_12_balance_usd",
    "month_18_balance_usd",
    "month_24_balance_usd",
    "month_24_cash_balance_usd",
    "min_cash_balance_usd",
]
EXACT_FIELDS = ["covenant_trigger_month", "payoff_month", "min_cash_month"]
ALL_FIELDS = DOLLAR_FIELDS + EXACT_FIELDS


def _load_json_safe(path: Path) -> dict | None:
    try:
        # utf-8-sig transparently strips a leading UTF-8 BOM if present
        # and is a no-op for files without one.
        with open(path, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _dollar_within_tolerance(agent_value, golden_value) -> bool:
    try:
        agent_value = float(agent_value)
    except (TypeError, ValueError):
        return False
    return abs(agent_value - golden_value) <= DOLLAR_TOLERANCE_ABSOLUTE


def _exact_match(agent_value, golden_value) -> bool:
    if golden_value is None:
        return agent_value is None
    try:
        return int(agent_value) == int(golden_value)
    except (TypeError, ValueError):
        return False


def score(agent_results_dir: Path, golden_dir: Path) -> dict:
    golden = _load_json_safe(golden_dir / "answer.json")
    if golden is None:
        raise RuntimeError(f"golden answer.json missing or malformed at {golden_dir}")

    agent = _load_json_safe(agent_results_dir / "answer.json")
    fields: dict[str, bool] = {}

    if agent is None:
        for field in ALL_FIELDS:
            fields[field] = False
        return {"score": 0.0, "fields": fields, "note": "agent answer.json missing or malformed"}

    for field in DOLLAR_FIELDS:
        if field not in agent or field not in golden:
            fields[field] = False
            continue
        fields[field] = _dollar_within_tolerance(agent[field], golden[field])

    for field in EXACT_FIELDS:
        if field not in agent or field not in golden:
            fields[field] = False
            continue
        fields[field] = _exact_match(agent[field], golden[field])

    passed = sum(1 for v in fields.values() if v)
    total = len(ALL_FIELDS)
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
