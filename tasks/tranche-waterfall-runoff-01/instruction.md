# Three-tranche credit facility runoff schedule

You are a credit analyst. Build the full 24-month runoff schedule for
Northfield Instruments LLC's three-tranche credit facility and report the
key outcomes Credit Committee needs for the annual review.

## Inputs

All files are under `/home/agent/data/`:

- `loan_terms.md` — the facility's structure (three tranches in strict
  payment priority), each tranche's principal, amortization and interest
  terms, the PIK-vs-cash rules, the financial covenant, and the cash-sweep
  waterfall mechanics. Read it carefully and in full: the tranches interact
  with each other every month (which tranche gets paid, which gets swept,
  and which stays on PIK all depend on the other tranches' balances), and
  some rules that share a common trigger do not share the same duration —
  getting the sequencing and timing right within and across months matters
  as much as getting any single formula right.
- `monthly_cash_flow.csv` — Free Cash Flow Before Debt Service for each of
  the 24 months, the input the covenant and cash sweep both depend on.

## What to produce

Compute the month-by-month balance, interest (cash or PIK, as applicable),
scheduled principal, and cash-sweep prepayment for each of the three
tranches, for all 24 months, following the rules in `loan_terms.md`
exactly. From that schedule, report:

- Whether and when the financial covenant was triggered, and exactly what
  effect(s) that had on each tranche.
- Whether and when each tranche was fully repaid within the 24-month
  window (and, for the Subordinated tranche, when it converted from PIK to
  cash-pay, if it did).
- Total interest paid in cash, and total interest capitalized (PIK'd), for
  each tranche where applicable.
- The single lowest cash balance reached at any point in the 24 months,
  and when it occurred.

## Deliverables

Write to `/home/agent/results/`:

- `report.md` — your analysis. Must include: (1) an executive summary
  stating the headline outcomes for all three tranches, (2) a month-by-month
  schedule table covering all three tranches (balance, interest mode and
  amount, scheduled principal, sweep recipient and amount — one row per
  month, all 24 months), (3) an explanation of exactly when and why the
  covenant triggered and what effect(s) it had, (4) an explanation of the
  payment waterfall and cash-sweep mechanics and their effect on each
  tranche's payoff timeline, and (5) a short note on liquidity risk based
  on the lowest cash point reached.
- `answer.json` — a JSON object with exactly these keys:
  - `covenant_trigger_month` (integer or `null`): the month whose negative
    cash flow triggered the covenant, or `null` if never triggered
  - `tranche_a_payoff_month` (integer or `null`): the first month Tranche
    A's balance reaches exactly zero, or `null`
  - `tranche_b_payoff_month` (integer or `null`): the first month Tranche
    B's balance reaches exactly zero, or `null`
  - `tranche_c_conversion_month` (integer or `null`): the first month
    Tranche C converts from PIK to cash-pay, or `null` if it never converts
  - `tranche_c_payoff_month` (integer or `null`): the first month Tranche
    C's balance reaches exactly zero, or `null`
  - `total_tranche_a_cash_interest_usd` (float): sum of all cash interest
    paid on Tranche A across all 24 months
  - `total_tranche_b_cash_interest_usd` (float): sum of all cash-paid
    interest on Tranche B across all 24 months
  - `total_tranche_b_pik_interest_usd` (float): sum of all PIK'd interest
    on Tranche B across all 24 months
  - `total_tranche_c_pik_interest_usd` (float): sum of all PIK'd interest
    on Tranche C across all 24 months (before conversion)
  - `total_tranche_c_cash_interest_usd` (float): sum of all cash-paid
    interest on Tranche C across all 24 months (after conversion)
  - `month_12_tranche_a_balance_usd` (float): Tranche A's balance at the
    end of month 12
  - `month_12_tranche_b_balance_usd` (float): Tranche B's balance at the
    end of month 12
  - `month_12_tranche_c_balance_usd` (float): Tranche C's balance at the
    end of month 12
  - `month_24_cash_balance_usd` (float): cash balance at the end of month 24
  - `min_cash_balance_usd` (float): the lowest cash balance reached at the
    end of any month during the 24-month window
  - `min_cash_month` (integer): the month in which that lowest cash balance
    occurred

## Execution notes

Work autonomously in a single turn. Do not ask clarifying questions — make
a reasonable, stated assumption if something is genuinely ambiguous, and
note it in `report.md`. Submit once; there is no opportunity to revise
after submission. Report all dollar figures to the nearest cent in
`answer.json` (rounding only the final reported values, not intermediate
month-to-month calculations) and to the nearest dollar in `report.md`.
