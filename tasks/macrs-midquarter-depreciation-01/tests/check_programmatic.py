#!/usr/bin/env python3
"""Programmatic checks for macrs-midquarter-depreciation-01.

Compares the agent's answer.json against the golden answer.json (baked
from solution/solve.py). The load-bearing domain-knowledge gap this task
is built to catch: whether the agent knows that IRS rules require the
mid-quarter convention (not the default half-year convention) whenever
more than 40% of the year's depreciable basis is placed in service in the
fourth quarter -- and that each asset then uses ITS OWN quarter's
percentage table for every year of its recovery period, not just its
first year.

The two most plausible failure modes were constructed and verified during
authoring:
  - Ignoring the mid-quarter trigger entirely and using half-year
    percentages for everything: overstates total Year 1 depreciation by
    $11,500 (a 30% overstatement) and, per-asset, overstates the two Q4
    assets' Year 1 depreciation by 4x ($18,000 vs. the correct $4,500 for
    EQ-104 alone).
  - Correctly applying mid-quarter timing for Year 1 but reverting to the
    half-year table for Year 2 onward (treating mid-quarter as a
    first-year-only adjustment): understates total Year 2 depreciation by
    $4,600.
Both bugs are caught with a flat $10 absolute tolerance on dollar fields
(legitimate rounding here should only ever be pennies, since every
percentage in the underlying IRS tables is stated to two decimal places
and multiplied against a fixed cost basis) -- see "Verification
performed" in the task README for the exact bug-injection results.

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

DOLLAR_TOLERANCE_ABSOLUTE = 10.0  # flat, not a percentage -- see module docstring
PERCENTAGE_TOLERANCE_ABSOLUTE = 0.5

ASSET_IDS = ["EQ-101", "EQ-102", "EQ-103", "EQ-104", "EQ-105"]

TOP_LEVEL_DOLLAR_FIELDS = [
    "total_year1_depreciation_usd",
    "total_year2_depreciation_usd",
    "total_six_year_depreciation_usd",
]
PER_ASSET_FIELDS = ["year1_depreciation_by_asset", "year2_depreciation_by_asset"]


def _load_json_safe(path: Path) -> dict | None:
    try:
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


def score(agent_results_dir: Path, golden_dir: Path) -> dict:
    golden = _load_json_safe(golden_dir / "answer.json")
    if golden is None:
        raise RuntimeError(f"golden answer.json missing or malformed at {golden_dir}")

    agent = _load_json_safe(agent_results_dir / "answer.json")
    fields: dict[str, bool] = {}

    all_field_names = (
        ["convention_used", "q4_basis_percentage_of_total"]
        + TOP_LEVEL_DOLLAR_FIELDS
        + [f"year1_depreciation_by_asset.{aid}" for aid in ASSET_IDS]
        + [f"year2_depreciation_by_asset.{aid}" for aid in ASSET_IDS]
    )

    if agent is None:
        for field in all_field_names:
            fields[field] = False
        return {"score": 0.0, "fields": fields, "note": "agent answer.json missing or malformed"}

    fields["convention_used"] = agent.get("convention_used") == golden["convention_used"]

    q4_agent = agent.get("q4_basis_percentage_of_total")
    try:
        fields["q4_basis_percentage_of_total"] = (
            abs(float(q4_agent) - golden["q4_basis_percentage_of_total"]) <= PERCENTAGE_TOLERANCE_ABSOLUTE
        )
    except (TypeError, ValueError):
        fields["q4_basis_percentage_of_total"] = False

    for field in TOP_LEVEL_DOLLAR_FIELDS:
        if field not in agent:
            fields[field] = False
            continue
        fields[field] = _dollar_within_tolerance(agent[field], golden[field])

    for per_asset_field in PER_ASSET_FIELDS:
        agent_map = agent.get(per_asset_field) if isinstance(agent.get(per_asset_field), dict) else {}
        golden_map = golden[per_asset_field]
        for asset_id in ASSET_IDS:
            key = f"{per_asset_field}.{asset_id}"
            if asset_id not in agent_map:
                fields[key] = False
                continue
            fields[key] = _dollar_within_tolerance(agent_map[asset_id], golden_map[asset_id])

    passed = sum(1 for v in fields.values() if v)
    total = len(all_field_names)
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
