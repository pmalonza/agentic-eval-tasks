# Q2 gross margin variance analysis — golden solution

## Executive summary

Gross margin missed budget by **5.09 points** (28.42% budget vs. 23.33%
actual), a $124,200 gross-profit shortfall. The single largest driver is
**Product B's price cut** ($15.00 -> $14.00, a $58,000 GP hit — 46.7% of
the total miss), not the unit-volume decline that's the most visually
obvious thing in the data (volume is only 18.5% of the miss).

The cost allocation schedule books a $55,000 one-time warehouse
consolidation cost 100% to Product A, while the source email thread
describes that cost as shared, company-wide infrastructure. Reallocating
it consistently with the standard pool's own pro-rata-by-revenue basis
flips which product line looks like the bigger problem: **as booked**,
Product A's miss (5.67 points) looks larger than Product B's (4.52); **
corrected**, Product A's real miss is a modest 3.09 points and Product
B's is 7.61 — nearly double what the booked numbers suggest.

**Recommendation:** direct corrective attention at Product B's pricing,
not Product A's operations, and reallocate one-time/shared costs
pro-rata by revenue going forward rather than defaulting to whichever
cost center happens to get the invoice.

## The variance bridge

| Bridge component | $ impact | % of total miss |
|---|---|---|
| Budget gross profit | $540,000 | — |
| Volume effect (both products, net of proportional direct cost) | -$23,000 | 18.5% |
| Price effect (Product B's cut; Product A's price is unchanged) | -$58,000 | 46.7% |
| Overhead effect (net cost of the warehouse consolidation, correctly attributed at the company level) | -$43,200 | 34.8% |
| Overhead misallocation between Product A and Product B | $0 (nets to zero company-wide) | — |
| **Actual gross profit (as booked)** | **$415,800** | — |

Ties out exactly: $540,000 - $23,000 - $58,000 - $43,200 = $415,800.

Two things matter here beyond the arithmetic:

1. **Volume is the smallest driver**, even though it's the most visible
   thing in the raw data (units are down for both products). Leading a
   variance narrative with volume is directionally true but materially
   misleading about how much of the story it is.
2. **The $43,200 overhead effect is real and unavoidable at the company
   level** — the consolidation genuinely cost that much net of the lower
   base overhead pool from reduced revenue. What's *not* structurally
   determined is which product line absorbs it, which is where the
   booking issue lives.

## The allocation issue

`cost_allocation_schedule.csv` allocates the standard $178,200 overhead
pool pro-rata by product revenue share (Product A 54.43%, Product B
45.57%, consistent with the stated Q2 policy) — but allocates the entire
$55,000 warehouse consolidation cost to Product A's cost center alone,
with no stated rationale beyond "charged to Product A cost center."

The email thread establishes that the consolidation was **not**
Product-A-specific: "Both sites currently store and ship for the whole
product catalog, so this is a shared-infrastructure move, not tied to
one line of business" (Kessler, May 8). Nothing in the thread mentions
booking the cost to a single product, or gives any reason it should be —
it is simply how Facilities coded the GL entry.

Reallocating that $55,000 on the same pro-rata basis already used for
the standard pool (54.43% / 45.57%) gives $29,938 to Product A and
$25,062 to Product B, instead of $55,000 / $0. That's a $25,062 swing
between the two products' cost lines — enough to flip which one looks
like the priority.

## Corrected product-line attribution

| | Budget GM% | As-booked actual GM% | As-booked miss | Corrected actual GM% | Corrected miss |
|---|---|---|---|---|---|
| Product A | 30.00% | 24.33% | 5.67 pts | 26.91% | **3.09 pts** |
| Product B | 26.67% | 22.14% | 4.52 pts | 19.06% | **7.61 pts** |

As booked, Product A appears to have the bigger problem. Correctly
allocated, that's backwards: Product A's real miss is mostly just its
own small volume decline (97,000 vs. 100,000 budgeted units), while
Product B's real miss — driven by the price cut — is the larger of the
two once it's no longer being shielded from its fair share of the
consolidation cost.

## Validation

All figures above were computed by `solution/solve.py` directly from the
three source files (`q2_budget_vs_actual.csv`, `cost_allocation_schedule.csv`,
`email_thread.md`) — none were hand-typed. The script identifies the
anomalous allocation row programmatically (the one whose product split
deviates from a pro-rata-by-revenue allocation by more than 1%, rather
than by matching a hardcoded row name), so the same logic would catch an
equivalent anomaly if the source numbers changed. The bridge is verified
to tie out to the cent (`sum of components == actual GP - budget GP`)
and the corrected/booked overhead splits are verified to sum to the same
total overhead pool ($233,200) either way, confirming the misallocation
is a pure attribution issue, not a change to the total-company number.

## Assumptions and limitations

- The one-time cost's "correct" allocation basis is assumed to be the
  same pro-rata-by-revenue basis already documented for the standard
  pool, since the email thread doesn't specify an alternative basis and
  this is the only basis already in use and defensible from the source
  data. A different reasonable basis (e.g., by shipment volume) would
  shift the split by at most a few thousand dollars and would not change
  which product line is the larger corrected miss.
- Direct cost per unit is unchanged in both products between budget and
  actual, so there is no "cost creep" story on the direct-cost line —
  the entire cost-side story is the overhead allocation.
