#!/usr/bin/env python3
"""Programmatic checks for rate-conflict-interest-analysis-01.

Unlike every other task in this repo, this checker's most important field
is not a computed dollar figure -- it's whether the agent noticed that the
source materials contain a genuine, unresolved conflict at all
(`conflict_detected`). The two source documents (an executed Credit
Agreement stating a fixed 350 bps margin, and a later lender rate-reset
notice stating 375 bps, with no amendment or pricing grid connecting the
two) were deliberately constructed with no legitimate way to determine
which one governs from the provided materials alone. The correct
professional behavior is to compute the requested projection under BOTH
stated rates and flag the conflict -- not to silently pick one and report
a single confident number.

The answer schema deliberately does NOT label the two scenarios after
their source documents (it uses unordered "scenario_a"/"scenario_b"
slots) so that noticing there are two scenarios, and which two rates they
correspond to, is left entirely to the agent -- the schema must not hand
over the correct strategy. Because "a" and "b" are therefore arbitrary
(an agent might put the 350 bps scenario in either slot), this checker
matches scenarios by their reported margin value, not by slot position.

The two most plausible failure modes were constructed and verified during
authoring: silently adopting the Credit Agreement's 350 bps rate as if
uncontested, and silently adopting the rate-reset notice's 375 bps rate as
if uncontested. Both are caught primarily via `conflict_detected` (which
should be true) and via the fact that only one distinct margin/total pair
will be present at all -- so the other golden scenario's dollar fields
have nothing to match against and score 0.

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

DOLLAR_TOLERANCE_ABSOLUTE = 10.0


def _load_json_safe(path: Path) -> dict | None:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _close(agent_value, golden_value) -> bool:
    try:
        return abs(float(agent_value) - golden_value) <= DOLLAR_TOLERANCE_ABSOLUTE
    except (TypeError, ValueError):
        return False


def _extract_scenarios(payload: dict) -> dict[int, dict]:
    """Map margin_bps -> {total, month1} for whichever of the a/b slots are populated."""
    scenarios: dict[int, dict] = {}
    for slot in ("a", "b"):
        margin = payload.get(f"scenario_{slot}_margin_bps")
        total = payload.get(f"scenario_{slot}_interest_expense_year1_usd")
        month1 = payload.get(f"month_1_interest_scenario_{slot}_usd")
        try:
            margin = int(margin)
        except (TypeError, ValueError):
            continue
        scenarios[margin] = {"total": total, "month1": month1}
    return scenarios


def score(agent_results_dir: Path, golden_dir: Path) -> dict:
    golden = _load_json_safe(golden_dir / "answer.json")
    if golden is None:
        raise RuntimeError(f"golden answer.json missing or malformed at {golden_dir}")

    agent = _load_json_safe(agent_results_dir / "answer.json")

    golden_scenarios = _extract_scenarios(golden)
    field_names = (
        ["conflict_detected", "ending_balance_month_12_usd"]
        + [f"scenario_{margin}bps_total" for margin in sorted(golden_scenarios)]
        + [f"scenario_{margin}bps_month1" for margin in sorted(golden_scenarios)]
    )

    if agent is None:
        fields = {name: False for name in field_names}
        return {"score": 0.0, "fields": fields, "note": "agent answer.json missing or malformed"}

    fields: dict[str, bool] = {}
    fields["conflict_detected"] = agent.get("conflict_detected") is True

    ending_balance = agent.get("ending_balance_month_12_usd")
    fields["ending_balance_month_12_usd"] = _close(ending_balance, golden["ending_balance_month_12_usd"])

    agent_scenarios = _extract_scenarios(agent)
    for margin, golden_vals in golden_scenarios.items():
        total_key = f"scenario_{margin}bps_total"
        month1_key = f"scenario_{margin}bps_month1"
        if margin not in agent_scenarios:
            fields[total_key] = False
            fields[month1_key] = False
            continue
        fields[total_key] = _close(agent_scenarios[margin]["total"], golden_vals["total"])
        fields[month1_key] = _close(agent_scenarios[margin]["month1"], golden_vals["month1"])

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
