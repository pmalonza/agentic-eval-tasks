# Term loan runoff schedule

You are a credit analyst. Build the full 24-month runoff schedule for
Northfield Instruments LLC's term loan and report the key outcomes Credit
Committee needs for the annual review.

## Inputs

All files are under `/home/agent/data/`:

- `loan_terms.md` — the loan's principal, amortization schedule, interest
  rate and covenant step-up rule, and cash sweep mechanics. Read it
  carefully and in full: several of the rules interact with each other
  month to month (the interest rate depends on covenant history, the
  loan balance depends on both scheduled amortization and the cash
  sweep, and the cash sweep depends on that month's debt service), so
  getting the sequencing right within and across months matters as much
  as getting any single formula right.
- `monthly_cash_flow.csv` — Free Cash Flow Before Debt Service for each
  of the 24 months, the input the covenant and cash sweep both depend on.

## What to produce

Compute the month-by-month loan balance, interest, scheduled principal,
cash-sweep prepayment, and cash balance for all 24 months, following the
rules in `loan_terms.md` exactly. From that schedule, report:

- Whether and when the interest-rate covenant was triggered.
- Whether and when the loan was fully repaid within the 24-month window.
- Total interest paid over the life of the loan.
- The loan balance at several points across the term, and the ending
  cash balance.
- The single lowest cash balance reached at any point in the 24 months,
  and when it occurred.

## Deliverables

Write to `/home/agent/results/`:

- `report.md` — your analysis. Must include: (1) an executive summary
  stating the headline outcomes, (2) a month-by-month schedule table
  (loan balance, interest, scheduled principal, sweep, cash balance —
  one row per month, all 24 months), (3) an explanation of exactly when
  and why the covenant triggered (or why it didn't), (4) an explanation
  of the cash-sweep mechanics and their effect on the payoff timeline,
  and (5) a short note on liquidity risk based on the lowest cash point
  reached.
- `answer.json` — a JSON object with exactly these keys:
  - `covenant_trigger_month` (integer or `null`): the month whose
    negative cash flow caused the rate step-up (i.e. the month
    described in the covenant rule as the trigger), or `null` if the
    covenant was never triggered
  - `payoff_month` (integer or `null`): the first month in which the
    loan balance reaches exactly zero, or `null` if the loan is not
    fully repaid within the 24-month window
  - `total_interest_paid_usd` (float): sum of all interest across all
    24 months
  - `month_6_balance_usd` (float): loan balance at the end of month 6
  - `month_12_balance_usd` (float): loan balance at the end of month 12
  - `month_18_balance_usd` (float): loan balance at the end of month 18
  - `month_24_balance_usd` (float): loan balance at the end of month 24
  - `month_24_cash_balance_usd` (float): cash balance at the end of
    month 24
  - `min_cash_balance_usd` (float): the lowest cash balance reached at
    the end of any month during the 24-month window
  - `min_cash_month` (integer): the month in which that lowest cash
    balance occurred

## Execution notes

Work autonomously in a single turn. Do not ask clarifying questions —
make a reasonable, stated assumption if something is genuinely
ambiguous, and note it in `report.md`. Submit once; there is no
opportunity to revise after submission. Report all dollar figures to
the nearest cent in `answer.json` (rounding only the final reported
values, not intermediate month-to-month calculations) and to the
nearest dollar in `report.md`.
