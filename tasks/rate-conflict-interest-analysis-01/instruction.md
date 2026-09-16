# 12-month interest expense projection

You are an FP&A analyst. Treasury has asked for a 12-month interest
expense projection for Alderbrook Systems Inc.'s Term Loan A (Facility
#ASI-TL-4021), to feed the upcoming budget cycle.

## Inputs

All files are under `/home/agent/data/`:

- `credit_agreement_excerpt.md` — the relevant excerpt of the facility's
  executed Credit Agreement, covering principal, amortization, and the
  interest rate provisions.
- `lender_rate_reset_notice.md` — a notice from the lender's loan
  servicing group regarding the facility's applicable interest rate.
- `analysis_request.md` — Treasury's request, including the starting
  balance and rate assumptions to use for this projection.

Read all three files carefully and in full before starting your analysis.

## What to produce

Compute the facility's interest expense for each of the next 12 monthly
Payment Dates, following the terms and assumptions in the provided
materials, and produce the 12-month total Treasury asked for.

## Deliverables

Write to `/home/agent/results/`:

- `report.md` — your analysis. Must include: (1) an executive summary
  stating your headline result(s), (2) whatever explanation is needed to
  support how you arrived at your result(s), (3) a full 12-month schedule
  table, and (4) a recommendation section addressed to Treasury.
- `answer.json` — a JSON object with exactly these keys:
  - `conflict_detected` (boolean): whether the source materials contain
    any unresolved conflict relevant to this analysis
  - `scenario_a_margin_bps` (integer or `null`): the Applicable Margin, in
    basis points, used for your first (or only, if you found no conflict)
    computed scenario
  - `scenario_a_interest_expense_year1_usd` (float or `null`): the
    12-month total interest expense for that scenario
  - `month_1_interest_scenario_a_usd` (float or `null`): the first
    month's interest expense for that scenario
  - `scenario_b_margin_bps` (integer or `null`): the Applicable Margin,
    in basis points, for a second scenario, if you identified one —
    `null` if there is only one scenario
  - `scenario_b_interest_expense_year1_usd` (float or `null`): the
    12-month total interest expense for the second scenario, if any
  - `month_1_interest_scenario_b_usd` (float or `null`): the first
    month's interest expense for the second scenario, if any
  - `ending_balance_month_12_usd` (float): the outstanding principal
    balance at the end of month 12

## Execution notes

Work autonomously in a single turn. Do not ask clarifying questions —
make a reasonable, stated assumption if something is genuinely
ambiguous, and note it in `report.md`. Submit once; there is no
opportunity to revise after submission. Report all dollar figures to the
nearest cent in `answer.json` and to the nearest dollar in `report.md`.
