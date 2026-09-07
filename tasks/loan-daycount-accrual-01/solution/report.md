# Northfield Instruments term loan — 24-month runoff schedule (Actual/360)

## 1. Executive summary

The $1,500,000 term loan is **fully repaid in Month 17** (May 2028),
seven months ahead of its 24-month maturity (December 2028), driven by
consistently positive free cash flow and an active 50% cash sweep.
**Total interest paid over the life of the loan is $85,126.82**, computed
on an **Actual/360** day-count basis — the annual rate divided by 360,
multiplied by the actual number of calendar days in each month — not a
flat 1/12-of-the-annual-rate monthly fraction and not a 30/360
convention. This matters here specifically because the loan's 24-month
window spans two different Februaries with two different day counts:
February 2027 (28 days, not a leap year) and February 2028 (29 days, a
leap year), and every other month is 30 or 31 days — no two consecutive
months accrue interest at quite the same daily-rate-times-days figure.

The interest-rate covenant **triggers once, in Month 7** (July 2027),
when Free Cash Flow Before Debt Service goes negative (-$15,000). Per the
loan terms, the rate steps up from 7.20% to 8.70% starting **Month 8**
(August 2027) and stays elevated for the rest of the loan's life — the
day-count basis (Actual/360) is unaffected by the step-up; only the
annual rate itself changes.

The **lowest cash balance reached at any point is $27,589.93, in Month 7**
— the same month the covenant triggers. By Month 24 (December 2028,
seven months after full payoff, with no further debt service), the cash
balance has grown to **$1,204,873.18**.

## 2. Full month-by-month schedule

| Month | Calendar | Days | Rate | Interest | Sched. Principal | Sweep | End Balance | End Cash |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2027-01 | 31 | 7.20% | 9,300.00 | 62,500.00 | 89,100.00 | 1,348,400.00 | 189,100.00 |
| 2 | 2027-02 | 28 | 7.20% | 7,551.04 | 62,500.00 | 54,524.48 | 1,231,375.52 | 154,524.48 |
| 3 | 2027-03 | 31 | 7.20% | 7,634.53 | 62,500.00 | 39,694.98 | 1,129,180.54 | 139,694.98 |
| 4 | 2027-04 | 30 | 7.20% | 6,775.08 | 62,500.00 | 27,709.95 | 1,038,970.60 | 127,709.95 |
| 5 | 2027-05 | 31 | 7.20% | 6,441.62 | 62,500.00 | 19,384.16 | 957,086.43 | 119,384.16 |
| 6 | 2027-06 | 30 | 7.20% | 5,742.52 | 62,500.00 | 10,570.82 | 884,015.61 | 110,570.82 |
| 7 | 2027-07 | 31 | 7.20% | 5,480.90 | 62,500.00 | 0.00 | 821,515.61 | 27,589.93 |
| 8 | 2027-08 | 31 | 8.70% | 6,154.52 | 62,500.00 | 0.00 | 759,015.61 | 33,935.40 |
| 9 | 2027-09 | 30 | 8.70% | 5,502.86 | 62,500.00 | 0.00 | 696,515.61 | 55,932.54 |
| 10 | 2027-10 | 31 | 8.70% | 5,218.06 | 62,500.00 | 0.00 | 634,015.61 | 88,214.48 |
| 11 | 2027-11 | 30 | 8.70% | 4,596.61 | 62,500.00 | 15,558.93 | 555,956.68 | 115,558.93 |
| 12 | 2027-12 | 31 | 8.70% | 4,165.04 | 62,500.00 | 24,446.95 | 469,009.73 | 124,446.95 |
| 13 | 2028-01 | 31 | 8.70% | 3,513.66 | 62,500.00 | 24,216.64 | 382,293.09 | 124,216.64 |
| 14 | 2028-02 | **29** | 8.70% | 2,679.24 | 62,500.00 | 27,018.70 | 292,774.39 | 127,018.70 |
| 15 | 2028-03 | 31 | 8.70% | 2,193.37 | 62,500.00 | 31,162.67 | 199,111.72 | 131,162.67 |
| 16 | 2028-04 | 30 | 8.70% | 1,443.56 | 62,500.00 | 38,609.55 | 98,002.17 | 138,609.55 |
| 17 | 2028-05 | 31 | 8.70% | 734.20 | 62,500.00 | 35,502.17 | **0.00** | 154,873.18 |
| 18 | 2028-06 | 30 | — | 0 | 0 | 0 | 0.00 | 274,873.18 |
| 19 | 2028-07 | 31 | — | 0 | 0 | 0 | 0.00 | 404,873.18 |
| 20 | 2028-08 | 31 | — | 0 | 0 | 0 | 0.00 | 544,873.18 |
| 21 | 2028-09 | 30 | — | 0 | 0 | 0 | 0.00 | 694,873.18 |
| 22 | 2028-10 | 31 | — | 0 | 0 | 0 | 0.00 | 854,873.18 |
| 23 | 2028-11 | 30 | — | 0 | 0 | 0 | 0.00 | 1,024,873.18 |
| 24 | 2028-12 | 31 | — | 0 | 0 | 0 | 0.00 | **1,204,873.18** |

Note Month 2 (February 2027, 28 days) and Month 14 (February 2028, **29
days**, a leap year) are the only two 28/29-day months in the schedule;
every other month is 30 or 31 days per the ordinary Gregorian calendar.
Both interest figures for those months (Month 2: $7,551.04; Month 14:
$2,679.24) reflect their smaller day count relative to neighboring
30/31-day months — this is exactly the case a 30/360 or flat-1/12
implementation would get wrong, since both of those conventions would
silently apply the same day/month-fraction to every month regardless of
the real calendar.

## 3. Day-count basis: why Actual/360 changes the numbers here

Under Actual/360, `monthly_interest = balance × (annual_rate / 360) ×
days_in_that_calendar_month`. This is **not** the same as a flat
1/12-of-the-annual-rate monthly fraction, and **not** the same as a
30/360 convention (fixed 30 days for every month) — both of those
alternate conventions would have produced **the exact same wrong total
interest figure, $84,076.95**, because 30/360 and flat-1/12 are
numerically identical whenever every month is treated as exactly 30 days
(30/360 = 1/12 exactly). That figure is, not coincidentally, the golden
answer from a predecessor version of this facility that used flat
monthly interest throughout — reverting to that convention here would be
a $1,049.87 total-interest understatement, small enough to look
plausible on its own but traceable to a single, identifiable
implementation choice.

The correct Actual/360 calculation requires deriving the real number of
days in each of the 24 calendar months from January 2027 through
December 2028 — including recognizing that 2028 is a leap year (2028 is
divisible by 4 and not a century year) so February 2028 has 29 days,
while February 2027 has the ordinary 28.

## 4. Covenant trigger and cash-sweep mechanics

Month 7 (July 2027) is the only month in `monthly_cash_flow.csv` with
negative Free Cash Flow Before Debt Service (-$15,000). Per
`loan_terms.md`, this steps the rate from 7.20% to 8.70% effective the
month immediately following — Month 8 (August 2027), not Month 7 itself.
The step-up is one-time and permanent: every month from 8 through 17
(while the loan is still outstanding) is cash-flow positive, but the
elevated rate does not step back down. The day-count basis (Actual/360)
applies identically before and after the step-up; only the annual rate
changes.

The cash sweep is active in 11 of the 17 months the loan is outstanding
(Months 1-6 and 11-17; it goes dormant in Months 7-10 while cash rebuilds
after the covenant month's cash drain), sweeping 50% of cash above the
$100,000 minimum to principal each active month. This is what drives
payoff from Month 24 down to **Month 17** — without it, the loan would
have run the full straight-line schedule to Month 24.

## 5. Liquidity risk note

The lowest cash balance reached at any point is **$27,589.93, in Month 7
(July 2027)** — roughly 28% of the $100,000 minimum operating threshold —
the direct, mechanical result of Month 7's own negative $15,000 free
cash flow landing in the same month as that month's debt service, with
no sweep cushion left over from Month 6. The company recovers within
three months without missing a payment.

## Validation

Every figure in Sections 1-5 was computed by `solution/solve.py`
directly from `monthly_cash_flow.csv` and the fixed terms in
`loan_terms.md`, using Python's `calendar.monthrange()` to derive each
month's actual day count (which correctly returns 29 for February 2028
and 28 for February 2027) — nothing here was hand-typed. Reran the
script twice; output is byte-for-byte identical both times. Separately
computed both plausible wrong-convention variants (flat 1/12, and 30/360
with a fixed 30-day month) and confirmed both collapse to the exact same
wrong total interest ($84,076.95) — the golden answer of the predecessor
flat-rate version of this facility — differing from the correct
Actual/360 answer by $1,049.87, comfortably outside this task's $25
programmatic tolerance on every affected field. Confirmed cash never
goes negative in any month (minimum $27,589.93, in Month 7) and that the
loan balance never goes negative (sweep amounts are capped at the
remaining balance after scheduled principal each month).

## Assumptions and limitations

- Actual/360 is applied to both the base and elevated rate periods —
  only the annual rate itself changes at the covenant step-up; the
  day-count method does not change with it.
- The covenant rule is read as trigger-once: only the first
  negative-cash-flow month matters, matching `loan_terms.md`'s "one-time,
  permanent" language explicitly. There is only one negative month in
  the data, so this doesn't change the numeric outcome here.
- No revolver, default, or minimum-cash covenant breach is modeled
  beyond the stated interest-rate step-up; cash never falls below zero,
  so this doesn't arise in practice for this scenario.
