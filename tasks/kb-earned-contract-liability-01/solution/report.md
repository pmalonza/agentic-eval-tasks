# VSC-88214 — Earned Contract and Unearned Liability Analysis (Kerper–Bowron Method)

## 1. Executive summary

Applying the Kerper–Bowron Method's exposure-exclusion rule (Kerper and
Bowron 2026, Section 6.1) to VSC-88214: the manufacturer's warranty
(nominally 36 months / 30,000 miles) actually terminates at **Month 30**,
because at the assumed 1,000 miles/month rate, the 30,000-mile limit is
reached before the 36-month limit — the warranty is **mileage-bound**,
not time-bound. The VSC itself (60 months / 75,000 miles) terminates at
**Month 60**, because at the same mileage rate, 75,000 miles would not be
reached until Month 75 — the VSC is **time-bound**, not mileage-bound.
These two "whichever comes first" tests resolve in opposite directions.

**The VSC therefore has zero exposure for its first 30 months** — the
manufacturer's warranty bears all risk during that window — and is
exposed for **Months 31 through 60 (30 exposed months)**. Applying the
Earned Contract formula (Section 2, Equations 1–6) to this loss-forecast
stream produces a **materially back-loaded earning pattern**: the
contract is **0% earned through Month 30**, reaching **20% by Month 36**,
**60% by Month 48**, and 100% at final expiration (Month 60). A
traditional pro-rata (age-from-sale) approach would have shown roughly
20% earned by Month 12 alone — the KB Method's loss-based approach shows
**zero** earned at that point, since no loss dollars are forecast to
emerge until the manufacturer's warranty exclusion period ends.

| Valuation month | Earned % | Unearned % | Unearned liability ($1,800 premium) |
|---:|---:|---:|---:|
| 12 | 0.00% | 100.00% | $1,800.00 |
| 24 | 0.00% | 100.00% | $1,800.00 |
| 36 | 20.00% | 80.00% | $1,440.00 |
| 48 | 60.00% | 40.00% | $720.00 |
| 60 | 100.00% | 0.00% | $0.00 |

## 2. Exposure determination

| | Manufacturer's warranty | VSC (this contract) |
|---|---|---|
| Stated term (months) | 36 | 60 |
| Stated term (miles) | 30,000 | 75,000 |
| Month at which mileage limit is reached (30,000 ÷ 1,000, 75,000 ÷ 1,000) | 30 | 75 |
| Binding limit (whichever comes first) | **Mileage** (30 < 36) | **Time** (60 < 75) |
| Effective expiration month | **30** | **60** |

Per `kb_method_excerpt.md`, a month is exposed only if it falls **after**
the warranty's effective expiration **and** at or before the VSC's own
effective expiration. That window is **Month 31 through Month 60** — 30
exposed months.

## 3. Monthly loss forecast and Earned Contract schedule

Modeled pure premium (given): $50.00 per exposed month; $0.00 for any
non-exposed month (Months 1–30, still covered by the manufacturer's
warranty).

- **Total loss forecast:** `a = 30 months × $50.00 = $1,500.00`
- **Earned Contract fraction per exposed month:** `EC_i = $50.00 /
  $1,500.00 = 3.3333%` for each of Months 31–60; `EC_i = 0%` for Months
  1–30.

| Month range | Monthly f_i | Monthly EC_i | Cumulative EC at end of range |
|---|---:|---:|---:|
| 1–30 | $0.00 | 0.0000% | 0.00% (no exposure yet) |
| 31 | $50.00 | 3.3333% | 3.33% |
| 32–35 | $50.00 each | 3.3333% each | 16.67% (end of Month 35) |
| 36 | $50.00 | 3.3333% | **20.00%** |
| 37–47 | $50.00 each | 3.3333% each | 56.67% (end of Month 47) |
| 48 | $50.00 | 3.3333% | **60.00%** |
| 49–59 | $50.00 each | 3.3333% each | 96.67% (end of Month 59) |
| 60 | $50.00 | 3.3333% | **100.00%** |

Cumulative EC at Month 36 = 6 exposed months (31–36) × 3.3333% = 20.00%,
matching the table in Section 1. Cumulative EC at Month 48 = 18 exposed
months (31–48) × 3.3333% = 60.00%.

## 4. Validation

- The sum of all 60 months' `EC_i` equals exactly 100.00%, confirming
  the Earned Contract fully recognizes the total loss forecast by the
  VSC's expiration month, per Equation 6 of the cited method.
- Total loss forecast ($1,500.00) equals `30 exposed months × $50.00`
  exactly, with no unaccounted-for exposure.
- Recomputed `solution/solve.py` twice; output is byte-for-byte
  identical both times.

## Assumptions

- Per `contract_terms.md`, mileage is assumed flat at 1,000 miles/month
  for the life of the contract (no probabilistic mileage distribution is
  used for this analysis, per the task's explicit instruction — this is
  a simplification of the cited method's own Section 6.1 lognormal
  mileage-distribution approach, not a reproduction of it).
- The "whichever comes first" test was applied independently to the
  manufacturer's warranty and to the VSC itself, per
  `kb_method_excerpt.md` — there is no requirement that both resolve on
  the same basis (mileage vs. time), and here they resolve oppositely.
- Unearned liability in dollar terms was computed as `Gross Premium ×
  UEC_v`, a standard unearned-premium accounting convention noted in
  `kb_method_excerpt.md` as separate from the KB Method's own
  loss-forecast formula.
