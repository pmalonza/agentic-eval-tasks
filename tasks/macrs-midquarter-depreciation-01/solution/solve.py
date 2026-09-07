#!/usr/bin/env python3
"""Deterministic oracle for macrs-midquarter-depreciation-01.

Computes regular MACRS (GDS, 200% declining balance, 5-year property)
depreciation for a small fixed-asset register, correctly applying the IRS's
mid-quarter convention trigger: if more than 40% of the aggregate
depreciable basis of personal property placed in service during the tax
year falls in the fourth quarter, EVERY asset placed in service that year
must use the mid-quarter convention (not the default half-year convention)
-- and, importantly, each asset then uses the percentage table for the
SPECIFIC quarter it was placed in service, for every year of its recovery
period (not just its first year).

The percentage tables below (IRS Publication 946, Appendix A, Tables A-1
through A-5, for 5-year property) were cross-verified against two
independent secondary sources during authoring, plus an internal
consistency check (each table's six years sum to exactly 100.00%). See
the task README for the verification trail.

Usage: solve.py <output_dir>
Writes <output_dir>/answer.json and prints it to stdout.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import date
from pathlib import Path

# IRS Publication 946, Appendix A, Table A-1: 5-year property, half-year convention.
TABLE_HALF_YEAR = [20.00, 32.00, 19.20, 11.52, 11.52, 5.76]

# IRS Publication 946, Appendix A, Tables A-2 through A-5: 5-year property,
# mid-quarter convention, indexed by the quarter (1-4) the asset was placed
# in service.
TABLE_MID_QUARTER = {
    1: [35.00, 26.00, 15.60, 11.01, 11.01, 1.38],
    2: [25.00, 30.00, 18.00, 11.37, 11.37, 4.26],
    3: [15.00, 34.00, 20.40, 12.24, 11.30, 7.06],
    4: [5.00, 38.00, 22.80, 13.68, 10.94, 9.58],
}

MID_QUARTER_TRIGGER_PCT = 40.0


def quarter_of(d: date) -> int:
    return (d.month - 1) // 3 + 1


def load_assets(data_dir: Path) -> list[dict]:
    assets = []
    with open(data_dir / "asset_register.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            assets.append(
                {
                    "asset_id": row["Asset_ID"],
                    "placed_in_service": date.fromisoformat(row["Placed_In_Service_Date"]),
                    "cost_basis": float(row["Cost_Basis_USD"]),
                }
            )
    return assets


def compute(assets: list[dict]) -> dict:
    total_basis = sum(a["cost_basis"] for a in assets)
    q4_basis = sum(a["cost_basis"] for a in assets if quarter_of(a["placed_in_service"]) == 4)
    q4_pct = (q4_basis / total_basis) * 100.0 if total_basis else 0.0

    mid_quarter = q4_pct > MID_QUARTER_TRIGGER_PCT
    convention = "mid_quarter" if mid_quarter else "half_year"

    year1_by_asset: dict[str, float] = {}
    year2_by_asset: dict[str, float] = {}
    six_year_by_asset: dict[str, float] = {}

    for asset in assets:
        if mid_quarter:
            table = TABLE_MID_QUARTER[quarter_of(asset["placed_in_service"])]
        else:
            table = TABLE_HALF_YEAR

        basis = asset["cost_basis"]
        year1_by_asset[asset["asset_id"]] = round(basis * table[0] / 100.0, 2)
        year2_by_asset[asset["asset_id"]] = round(basis * table[1] / 100.0, 2)
        six_year_by_asset[asset["asset_id"]] = round(sum(basis * pct / 100.0 for pct in table), 2)

    return {
        "convention_used": convention,
        "q4_basis_percentage_of_total": round(q4_pct, 2),
        "year1_depreciation_by_asset": year1_by_asset,
        "year2_depreciation_by_asset": year2_by_asset,
        "total_year1_depreciation_usd": round(sum(year1_by_asset.values()), 2),
        "total_year2_depreciation_usd": round(sum(year2_by_asset.values()), 2),
        "total_six_year_depreciation_usd": round(sum(six_year_by_asset.values()), 2),
    }


def main() -> int:
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    data_dir = Path(__file__).resolve().parent.parent / "environment" / "data"

    assets = load_assets(data_dir)
    result = compute(assets)

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "answer.json", "w") as fh:
        json.dump(result, fh, indent=2)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
