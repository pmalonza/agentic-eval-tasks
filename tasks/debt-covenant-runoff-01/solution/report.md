# Northfield Instruments term loan — 24-month runoff schedule

## 1. Executive summary

The $1,500,000 term loan is **fully repaid in month 17**, seven months
ahead of its 24-month maturity, driven by consistently positive free cash
flow and an active 50% cash sweep. **Total interest paid over the life of
the loan is $84,076.95** — well below what a full-term, no-sweep loan
would have cost, because the sweep retires principal aggressively in the
early months.

The interest-rate covenant **triggers once, in month 7**, when Free Cash
Flow Before Debt Service goes negative (-$15,000). Per the loan terms,
the rate steps up from 7.20% to 8.70% starting **month 8** and stays
elevated for the rest of the loan's life (it never steps back down, even
though every subsequent month is cash-flow positive).

The **lowest cash balance reached at any point is $27,823.17, in month
7** — the same month the covenant triggers, which is not a coincidence:
that month's negative operating cash flow is what drains the cash
buffer. By month 24 (seven months after full payoff, with no further
debt service), the cash balance has grown to **$1,205,923.05**.

## 2. Full month-by-month schedule

| Month | FCF | Rate | Interest | Sched. Principal | Sweep | End Balance | End Cash |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 100,000 | 7.20% | 9,000.00 | 62,500.00 | 89,250.00 | 1,348,250.00 | 189,250.00 |
| 2 | 90,000 | 7.20% | 8,089.50 | 62,500.00 | 54,330.25 | 1,231,419.75 | 154,330.25 |
| 3 | 95,000 | 7.20% | 7,388.52 | 62,500.00 | 39,720.87 | 1,129,198.88 | 139,720.87 |
| 4 | 85,000 | 7.20% | 6,775.19 | 62,500.00 | 27,722.84 | 1,038,976.05 | 127,722.84 |
| 5 | 80,000 | 7.20% | 6,233.86 | 62,500.00 | 19,494.49 | 956,981.56 | 119,494.49 |
| 6 | 70,000 | 7.20% | 5,741.89 | 62,500.00 | 10,626.30 | 883,855.26 | 110,626.30 |
| 7 | -15,000 | 7.20% | 5,303.13 | 62,500.00 | 0.00 | 821,355.26 | 27,823.17 |
| 8 | 75,000 | 8.70% | 5,954.83 | 62,500.00 | 0.00 | 758,855.26 | 34,368.34 |
| 9 | 90,000 | 8.70% | 5,501.70 | 62,500.00 | 0.00 | 696,355.26 | 56,366.64 |
| 10 | 100,000 | 8.70% | 5,048.58 | 62,500.00 | 0.00 | 633,855.26 | 88,818.07 |
| 11 | 110,000 | 8.70% | 4,595.45 | 62,500.00 | 15,861.31 | 555,493.95 | 115,861.31 |
| 12 | 100,000 | 8.70% | 4,027.33 | 62,500.00 | 24,666.99 | 468,326.96 | 124,666.99 |
| 13 | 90,000 | 8.70% | 3,395.37 | 62,500.00 | 24,385.81 | 381,441.15 | 124,385.81 |
| 14 | 95,000 | 8.70% | 2,765.45 | 62,500.00 | 27,060.18 | 291,880.97 | 127,060.18 |
| 15 | 100,000 | 8.70% | 2,116.14 | 62,500.00 | 31,222.02 | 198,158.95 | 131,222.02 |
| 16 | 110,000 | 8.70% | 1,436.65 | 62,500.00 | 38,642.68 | 97,016.27 | 138,642.68 |
| 17 | 115,000 | 8.70% | 703.37 | 62,500.00 | 34,516.27 | **0.00** | 155,923.05 |
| 18 | 120,000 | — | 0 | 0 | 0 | 0.00 | 275,923.05 |
| 19 | 130,000 | — | 0 | 0 | 0 | 0.00 | 405,923.05 |
| 20 | 140,000 | — | 0 | 0 | 0 | 0.00 | 545,923.05 |
| 21 | 150,000 | — | 0 | 0 | 0 | 0.00 | 695,923.05 |
| 22 | 160,000 | — | 0 | 0 | 0 | 0.00 | 855,923.05 |
| 23 | 170,000 | — | 0 | 0 | 0 | 0.00 | 1,025,923.05 |
| 24 | 180,000 | — | 0 | 0 | 0 | 0.00 | **1,205,923.05** |

Note the "Rate" column shows the rate *in effect for that month's
interest calculation* — month 7 still uses 7.20% (the trigger is
detected during month 7, but the step-up applies starting month 8), and
months 18-24 show no rate because the loan is already paid off and no
interest accrues.

## 3. Why and when the covenant triggered

Month 7 is the only month in `monthly_cash_flow.csv` with negative Free
Cash Flow Before Debt Service (-$15,000). Per `loan_terms.md`, this
steps the rate from 7.20% to 8.70% **effective the month immediately
following** — i.e. month 8, not month 7 itself. This timing detail is
the easiest part of the rule to get backwards: applying the elevated
rate to month 7's own interest calculation (rather than starting in
month 8) understates total interest by roughly $1,100-1,200 relative to
the correct schedule, a small enough shift to look plausible while
still being wrong.

The step-up is **one-time and permanent** — every month from 8 through
17 (when the loan is still outstanding) is cash-flow positive, but the
elevated rate does not step back down, exactly as specified.

## 4. Cash-sweep mechanics and their effect on payoff timing

The sweep is active in 11 of the 17 months the loan is outstanding
(months 1-6 and 11-17; it goes dormant in months 7-10 while cash is
rebuilding after the covenant month's cash drain). In every active
month, exactly 50% of cash above the $100,000 minimum operating balance
is swept to principal, on top of the $62,500 scheduled payment.

This sweep is what drives payoff from month 24 down to **month 17** —
without it, the loan would have run the full straight-line schedule to
month 24. The sweep is front-loaded: months 1-6 alone sweep roughly
$241,000 of extra principal (on top of $375,000 of scheduled principal),
because the loan starts with a large cash cushion ($250,000) well above
the $100,000 floor. That front-loading is also why total interest
($84,077) is well below what a full-24-month schedule at the same rates
would have cost — the balance the elevated 8.70% rate applies to (from
month 8 onward) is already meaningfully smaller than the original
principal, and shrinks fast enough that the loan is gone before month
24.

## 5. Liquidity risk note

The lowest cash balance reached at any point in the 24-month window is
**$27,823.17, in month 7** — roughly 28% of the $100,000 minimum
operating threshold the sweep rule targets, and the only month the
company operates meaningfully below that floor. This is a direct,
mechanical consequence of month 7's own negative $15,000 free cash flow
landing in the same month as that month's $67,803.13 of scheduled debt
service (interest + scheduled principal), with no sweep cushion left
over from month 6 (month 6's sweep left cash right at the $110,626.30
mark, just above the floor, before month 7's shortfall hit). The
company recovers within three months without missing a payment, but a
credit review should flag month 7 as the single point of tightest
liquidity in the facility's life, and confirm whether a similar or
larger cash-flow shortfall later in the term (after the cash cushion has
been swept down further) would be survivable without a covenant breach
beyond the rate step-up already modeled here.

## Validation

Every figure in Sections 1-5 was computed by `solution/solve.py`
directly from `monthly_cash_flow.csv` and the fixed terms in
`loan_terms.md` — nothing here was hand-typed. The script carries three
pieces of state forward month to month (loan balance, cash balance,
current interest rate) and applies four interacting rules in the
correct order each month (interest on the start-of-month balance,
scheduled principal, the covenant check based on that month's cash
flow, and the cash sweep computed after that month's own debt service)
— the ordering and timing of these rules, not any single formula in
isolation, is what a correct implementation has to get right for all 24
months simultaneously. Reran the script twice; output is
byte-for-byte identical both times. Confirmed cash never goes negative
in any month (minimum $27,823.17, in month 7) and that the loan balance
never goes negative (sweep amounts are capped at the remaining balance
after scheduled principal each month).

## Assumptions and limitations

- `loan_terms.md` states interest is calculated on the start-of-month
  balance, "before that month's own scheduled principal payment and
  cash-sweep prepayment are applied" — taken literally: each month's
  interest uses the balance carried in from the *end* of the prior
  month (after that prior month's own scheduled principal *and* sweep),
  not a mid-month recalculation.
- The covenant rule is read as trigger-once: only the first
  negative-cash-flow month matters, matching `loan_terms.md`'s "one-time,
  permanent" language explicitly. There is only one negative month in
  the data, so this doesn't change the numeric outcome here, but it
  does mean a later negative month (none occurs) would not have caused
  a second step-up.
- No revolver, default, or minimum-cash covenant breach is modeled
  beyond the stated interest-rate step-up; cash never falls below zero,
  so this doesn't arise in practice for this scenario.
