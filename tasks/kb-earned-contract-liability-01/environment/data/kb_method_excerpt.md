# Reference Method: The Kerper–Bowron Method (KB Method)

**Source:** Kerper, J. and Bowron, L. (2026). "The Kerper–Bowron Method: A
Foundational Change for Service Contract Claim Estimation and Accounting."
*Risks*, 14(3), 44. https://doi.org/10.3390/risks14030044. Published 24
February 2026. Licensed CC BY 4.0.

The excerpts and formulas below are adapted from the cited paper for use
in this analysis. Apply them exactly as given.

## 1. Exposure: excluding the manufacturer's warranty period

Under the KB Method, a vehicle service contract ("VSC") does not begin
generating expected losses on the day it is sold. For as long as the
vehicle's underlying manufacturer's warranty is still in effect, any
covered repair is the manufacturer's liability, not the service
contract's — the service contract has **zero exposure** during that
period. This differs from traditional "age from sale" reserving methods,
which ignore the manufacturer's warranty entirely and treat every month
since sale as equally exposed.

Both the manufacturer's warranty and the VSC itself terminate at
**whichever comes first: the stated term in months, or the stated term
in miles** (given an assumed average monthly mileage rate for the
vehicle). This "whichever comes first" test must be applied
**independently** to the warranty and to the VSC — one may be
mileage-bound (terminates due to reaching its mileage limit before its
month limit) while the other is time-bound (terminates due to reaching
its month limit before its mileage limit), and there is no reason the
two must resolve the same way.

A month of the VSC's term is "exposed" (generates expected loss dollars)
if and only if it falls **after the manufacturer's warranty has
terminated** (by whichever of its own month or mile limits comes first)
**and at or before the VSC's own termination** (by whichever of its own
month or mile limits comes first).

## 2. The Earned Contract formula

Once the exposed months and their associated monthly loss forecasts are
known, the KB Method defines the Earned Contract as follows (Kerper and
Bowron 2026, Section 2, Equations 1–6):

Let `f_i` be the forecast expected loss dollars for month `i` after the
sale of the contract (zero for any non-exposed month), and let `e` be
the number of months until the contract's final expiration date. Then:

- **Total loss forecast at sale:** `a = f_1 + f_2 + f_3 + ... + f_e`
- **Earned Contract fraction for month i:** `EC_i = f_i / a`
- **Cumulative Earned Contract through month v:** `EC_v = EC_1 + EC_2 +
  ... + EC_v` (the sum of `EC_i` for `i` from 1 through `v`)
- **Unearned Contract at month v:** `UEC_v = 1 - EC_v` (equivalently, the
  sum of `EC_i` for `i` from `v+1` through `e`)
- By construction, `EC_1 + EC_2 + ... + EC_e = 1.00` (the contract is
  100% earned by its final expiration month).

Note that this earning pattern is driven entirely by **where the
forecast loss dollars fall**, not by the simple passage of time. A month
with zero exposure (e.g., because it falls within the manufacturer's
warranty period) contributes `f_i = 0` and therefore `EC_i = 0` — no
revenue is recognized as "earned" for that month under this method,
regardless of how much of the contract's calendar term has elapsed.

## 3. Converting to dollar liabilities

Given the VSC's gross premium (the price the customer paid for the
contract), the dollar amount of unearned liability at any valuation month
`v` is the gross premium multiplied by `UEC_v`. This follows standard
unearned-premium accounting convention and is not itself a KB Method
formula.

## Scope note

This excerpt covers only the exposure-exclusion concept (Section 6.1)
and the Earned Contract formula (Section 2) of the cited paper. It does
not include the paper's Generalized Linear Model loss-cost modeling
(Section 6.2), cancellation-rate adjustment (Section 6.3.1), or
seasonality/trend adjustment (Section 6.3.2) — for this analysis, the
monthly pure premium rate is given directly to you in
`pricing_model_output.md` rather than needing to be modeled from claims
data.
