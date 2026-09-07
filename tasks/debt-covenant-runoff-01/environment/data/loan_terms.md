# Term Loan Summary — Facility #TL-2024-118

**Borrower:** Northfield Instruments LLC
**Original principal:** $1,500,000.00
**Term:** 24 months
**Effective date:** Month 1 (this schedule starts at the beginning of Month 1)

## Scheduled amortization

Principal amortizes on a straight-line basis: **$1,500,000.00 / 24 = $62,500.00**
of scheduled principal is due each month, for 24 months, or the remaining
loan balance if less than $62,500.00 (i.e. the final scheduled payment is
whatever principal is still outstanding).

## Interest

- **Base rate:** 7.20% per annum, charged monthly at 1/12th of the annual
  rate (0.60% per month).
- Interest for a given month is calculated on the loan balance as of the
  **start of that month** — i.e., the balance remaining after the
  *previous* month's scheduled principal payment **and** any cash-sweep
  prepayment from the previous month (see below). Interest is calculated
  before that month's own scheduled principal payment and cash-sweep
  prepayment are applied.

## Financial covenant (interest rate step-up)

If the borrower's Free Cash Flow Before Debt Service (see
`monthly_cash_flow.csv`) is **negative in any month**, the annual interest
rate steps up from 7.20% to **8.70%**, effective the **month immediately
following** the month in which negative cash flow occurred. The elevated
rate applies to that following month and **every month thereafter for the
remainder of the loan term**, regardless of the borrower's cash flow in
later months. This is a one-time, permanent step-up: once triggered, later
negative-cash-flow months (if any) have no further effect on the rate.

## Cash sweep

- **Minimum operating cash balance:** $100,000.00.
- **Starting cash balance (beginning of Month 1):** $250,000.00.
- Each month, after that month's Free Cash Flow Before Debt Service is
  added to the cash balance and that month's interest and scheduled
  principal are paid, if the resulting cash balance exceeds the $100,000.00
  minimum, **50% of the excess above $100,000.00** is swept to prepay loan
  principal that same month, in addition to the scheduled principal
  payment. The swept amount cannot exceed the loan balance remaining after
  that month's scheduled principal payment (the loan cannot be prepaid
  below zero). The cash balance carried into the next month is what
  remains after the sweep.
- Once the loan is fully repaid (scheduled principal + any cash sweeps
  reduce the balance to zero), no further interest accrues and no further
  scheduled principal or sweep payments are due for the remaining months
  in the 24-month window. Free Cash Flow Before Debt Service for any month
  after full repayment simply adds to the cash balance with no debt
  service deducted.
