# Fixed asset depreciation schedule

You are a corporate tax analyst. Compute Meridian Fabrication Works LLC's
federal income tax depreciation for the fixed assets listed below, for the
company's controller.

## Inputs

All files are under `/home/agent/data/`:

- `asset_register.csv` — the five assets placed in service, each with its
  placed-in-service date and cost basis.
- `company_context.md` — the tax year, recovery method, and the elections
  (or non-elections) that apply to these assets. Read it carefully and in
  full.

## What to produce

Compute regular MACRS depreciation for each asset for its first two tax
years, following all applicable IRS rules for 5-year GDS property exactly
as a corporate tax preparer would.

## Deliverables

Write to `/home/agent/results/`:

- `report.md` — your analysis. Must include: (1) an executive summary
  stating the headline outcomes, (2) an explanation of which averaging
  convention applies to these assets and why, (3) a table showing each
  asset's depreciation for both tax years, and (4) a validation section
  confirming your six-year totals reconcile to the assets' cost basis.
- `answer.json` — a JSON object with exactly these keys:
  - `convention_used` (string): either `"half_year"` or `"mid_quarter"`
  - `q4_basis_percentage_of_total` (float): the percentage of total
    depreciable basis placed in service in the fourth quarter, to two
    decimal places
  - `year1_depreciation_by_asset` (object): a mapping from each asset's
    `Asset_ID` to its first-tax-year depreciation (float)
  - `year2_depreciation_by_asset` (object): a mapping from each asset's
    `Asset_ID` to its second-tax-year depreciation (float)
  - `total_year1_depreciation_usd` (float): sum of all five assets' first-
    tax-year depreciation
  - `total_year2_depreciation_usd` (float): sum of all five assets'
    second-tax-year depreciation
  - `total_six_year_depreciation_usd` (float): sum of all five assets'
    depreciation over their full recovery period (all years until each
    asset is fully depreciated)

## Execution notes

Work autonomously in a single turn. Do not ask clarifying questions —
make a reasonable, stated assumption if something is genuinely ambiguous,
and note it in `report.md`. Submit once; there is no opportunity to
revise after submission. Report all dollar figures to the nearest cent in
`answer.json` and to the nearest dollar in `report.md`.
