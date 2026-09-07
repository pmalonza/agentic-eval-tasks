#!/usr/bin/env python3
"""Programmatic checks for fpa-variance-analysis-01.

Compares the agent's answer.json against the golden answer.json (baked
from solution/solve.py) within a 5% relative tolerance for numeric
fields, and exact match for the two string-enum fields. Never raises:
a missing file, malformed JSON, or missing key scores that field 0
rather than crashing the harness -- an agent that fails to produce
usable output should score 0 on this checker, not take down the run.

Usage: check_programmatic.py <agent_results_dir> [golden_dir]
Prints a JSON report to stdout: {"score": float in [0,1], "fields": {...}}
Always exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TOLERANCE_PCT = 0.05

NUMERIC_FIELDS = [
    "total_gm_miss_points",
    "total_gp_variance_usd",
    "product_a_miss_points_as_booked",
    "product_b_miss_points_as_booked",
    "product_a_miss_points_corrected",
    "product_b_miss_points_corrected",
    "one_time_cost_usd",
    "one_time_cost_corrected_product_a_usd",
    "one_time_cost_corrected_product_b_usd",
]
ENUM_FIELDS = ["largest_single_driver", "recommended_focus_product"]
ALL_FIELDS = NUMERIC_FIELDS + ENUM_FIELDS


def _load_json_safe(path: Path) -> dict | None:
    try:
        # utf-8-sig transparently strips a leading UTF-8 BOM if present
        # (e.g. from PowerShell's default UTF-8 write behavior) and is a
        # no-op for files without one -- an agent's JSON should not be
        # marked malformed over a BOM its own real work is correct past.
        with open(path, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _numeric_within_tolerance(agent_value, golden_value) -> bool:
    try:
        agent_value = float(agent_value)
    except (TypeError, ValueError):
        return False
    tolerance = max(abs(golden_value) * TOLERANCE_PCT, 0.01)
    return abs(agent_value - golden_value) <= tolerance


def score(agent_results_dir: Path, golden_dir: Path) -> dict:
    golden = _load_json_safe(golden_dir / "answer.json")
    if golden is None:
        # A broken golden file is a task-authoring bug, not an agent
        # failure -- surface it loudly rather than silently scoring 0.
        raise RuntimeError(f"golden answer.json missing or malformed at {golden_dir}")

    agent = _load_json_safe(agent_results_dir / "answer.json")
    fields: dict[str, bool] = {}

    if agent is None:
        for field in ALL_FIELDS:
            fields[field] = False
        return {"score": 0.0, "fields": fields, "note": "agent answer.json missing or malformed"}

    for field in NUMERIC_FIELDS:
        if field not in agent or field not in golden:
            fields[field] = False
            continue
        fields[field] = _numeric_within_tolerance(agent[field], golden[field])

    for field in ENUM_FIELDS:
        if field not in agent or field not in golden:
            fields[field] = False
            continue
        fields[field] = str(agent[field]).strip() == str(golden[field]).strip()

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
