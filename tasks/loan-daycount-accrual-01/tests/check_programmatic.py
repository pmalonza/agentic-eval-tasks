#!/usr/bin/env python3
"""Programmatic checks for loan-daycount-accrual-01.

Compares the agent's answer.json against the golden answer.json (baked
from solution/solve.py). The load-bearing bug this task is built to
catch is a wrong day-count convention: reverting to a flat annual-rate/12
monthly fraction, or to a 30/360 day-count (which is numerically
identical to flat 1/12 whenever every month is treated as exactly 30
days), instead of true Actual/360 with the real number of calendar days
per month. Both of those plausible wrong conventions were verified during
authoring to collapse to the exact same wrong figure -- $84,076.95 total
interest, $1,205,923.05 ending cash, etc. -- which is byte-for-byte the
golden answer from the predecessor task (debt-covenant-runoff-01) that
used flat 1/12 throughout. The smallest legitimate golden-vs-bug field
delta is $160.35 (month_6_balance_usd), so the same flat $25 absolute
tolerance used in that predecessor task (see its check_programmatic.py
docstring for why a percentage tolerance is unsafe here) comfortably
separates a correct Actual/360 implementation from either wrong-convention
shortcut on every dollar field.

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
