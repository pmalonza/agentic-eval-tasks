# Actuarial Pricing Model Output — Rating Cell for VSC-88214

The firm's actuarial pricing model (a Generalized Linear Model fit to
historical claims for this vehicle segment and coverage level, per the
Kerper–Bowron Method's Section 6.2 model-development approach) has
already been run for this rating cell. Its output, which you should use
directly, is:

- **Modeled pure premium: $50.00 per exposed month.** This is the
  expected loss-and-cancel dollars per month for any month in which the
  VSC has exposure (i.e., any month that is within the VSC's own term
  and past the manufacturer's warranty's termination, per the exposure
  rule in `kb_method_excerpt.md`).
- This rate is already fully adjusted for seasonality, trend, and this
  vehicle segment's specific rating factors — do not apply any further
  adjustment to it.
- A non-exposed month (one still covered by the manufacturer's warranty,
  or one after the VSC's own termination) has a modeled pure premium of
  $0.00 — the manufacturer, not this service contract, bears the risk in
  that month.
