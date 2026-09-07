# Credit Facility Summary — Facility #TW-2027-311

**Borrower:** Northfield Instruments LLC
**Term:** 24 months
**Structure:** Three tranches, ranked in strict payment priority: **Tranche A
(Senior)**, **Tranche B (Mezzanine)**, **Tranche C (Subordinated)**. Tranche A
is paid before Tranche B in every respect (interest, scheduled principal, and
cash-sweep prepayment); Tranche B is paid before Tranche C in every respect.
A lower-priority tranche never receives any payment in a month until the
tranche(s) above it have received everything they are entitled to that month.

## Tranche A — Senior

- **Principal:** $2,000,000.00.
- **Scheduled amortization:** straight-line, $2,000,000.00 / 24 =
  $83,333.33... per month, or the remaining balance if less.
- **Base interest rate:** 8.00% per annum, charged monthly at 1/12th of the
  annual rate.
- Interest for a given month is calculated on the balance as of the **start
  of that month** — i.e., after the *previous* month's scheduled principal
  and any cash-sweep prepayment. Both interest and scheduled principal on
  Tranche A are always paid in cash; Tranche A has no PIK option.

## Tranche B — Mezzanine

- **Principal:** $800,000.00.
- **Interest-only** for the life of the facility: Tranche B has no scheduled
  principal payment of its own. Its balance only decreases via a cash-sweep
  prepayment (see below), and only increases via a PIK accrual (see below).
- **Interest rate:** 11.00% per annum, charged monthly at 1/12th of the
  annual rate, on the balance as of the start of the month.
- **PIK-vs-cash toggle:** Each month, after Tranche A's interest and
  scheduled principal have been paid in cash, Tranche B's interest for that
  month is paid in cash **if** the remaining cash balance (after Tranche A's
  debt service, before any sweep) is at least equal to that month's Tranche B
  interest. **If it is not**, the entire month's Tranche B interest is
  capitalized (PIK'd) — added to Tranche B's principal balance — rather than
  partially paid; there is no partial cash / partial PIK split in any month.
- **Forced PIK override:** see the Financial Covenant section below for one
  additional, narrower circumstance in which Tranche B's interest is PIK'd
  regardless of cash sufficiency.

## Tranche C — Subordinated

- **Principal:** $500,000.00.
- **Interest rate:** 14.00% per annum, charged monthly at 1/12th of the
  annual rate, on the balance as of the start of the month.
- **PIK until both senior tranches are retired:** Tranche C's interest is
  **fully capitalized (PIK'd) every month for as long as Tranche A's balance
  or Tranche B's balance (or both) is still greater than zero as of the
  start of that month.** Tranche C makes no cash payments of any kind —
  interest or principal — while either senior tranche has any balance
  outstanding.
- **Conversion to cash-pay:** Starting with the first month in which
  **both** Tranche A's and Tranche B's balances are zero as of the start of
  that month, Tranche C permanently converts to cash-pay interest-only (no
  more PIK), and becomes eligible for cash-sweep prepayment from that month
  onward. This conversion depends on **both** senior tranches being fully
  retired — Tranche A alone reaching zero, with Tranche B still outstanding,
  does **not** trigger conversion.

## Financial covenant (Senior rate step-up and Mezzanine liquidity relief)

If the borrower's Free Cash Flow Before Debt Service (see
`monthly_cash_flow.csv`) is **negative in any month**, two distinct things
happen, effective the **month immediately following** the negative month —
and they do **not** last the same length of time:

1. **Tranche A's annual rate permanently steps up** from 8.00% to 9.00%,
   effective that following month and every month thereafter for the
   remainder of the facility's life, regardless of the borrower's cash flow
   in later months. This is a one-time, permanent change: a later negative
   month (if any) has no further effect on the rate.
2. **Tranche B's interest is forced into PIK for that one following month
   only** — regardless of whether cash would otherwise have been sufficient
   to pay it in cash that month. This is a one-time liquidity relief valve,
   not a permanent change: starting the month after that, Tranche B's normal
   PIK-vs-cash cash-sufficiency test (described above) resumes exactly as
   before, with no lingering effect from the covenant event.

Both effects share the same trigger and the same one-month lag, but only
the first (Tranche A's rate) is permanent — the second (Tranche B's forced
PIK) applies to exactly one calendar month.

## Cash sweep

- **Minimum operating cash balance:** $150,000.00.
- **Starting cash balance (beginning of Month 1):** $400,000.00.
- Each month, after that month's Free Cash Flow Before Debt Service has been
  added to cash, and after Tranche A's interest and scheduled principal
  (always cash) and Tranche B's interest (cash or PIK, per the toggle above)
  and Tranche C's interest (cash, only if converted; otherwise PIK) have all
  been applied, if the resulting cash balance exceeds the $150,000.00
  minimum, **50% of the excess above $150,000.00** is swept to prepay
  principal that same month.
- The sweep follows the same strict waterfall priority as everything else:
  it is applied **first and entirely to Tranche A** (up to A's remaining
  balance) if Tranche A's balance is still greater than zero; **only if**
  Tranche A's balance is already zero does any sweep amount go to Tranche B
  (up to B's remaining balance, which may include previously PIK'd amounts);
  **only if** both Tranche A's and Tranche B's balances are zero does any
  sweep amount go to Tranche C (and only once Tranche C has converted to
  cash-pay per the rule above). The sweep never splits across two tranches
  in the same month — whichever single tranche is highest-priority with a
  balance remaining absorbs the entire swept amount, up to its own balance.
- Once a tranche's balance reaches zero, no further interest, scheduled
  principal, or sweep applies to that tranche for the remainder of the
  facility's life.
