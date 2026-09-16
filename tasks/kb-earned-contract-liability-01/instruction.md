# Earned Contract and unearned liability analysis

You are an actuarial analyst. Compute the Earned Contract schedule and
unearned liability for vehicle service contract VSC-88214, following the
method described in the provided reference excerpt.

## Inputs

All files are under `/home/agent/data/`:

- `kb_method_excerpt.md` — an excerpt of the reference method you must
  apply, including its exposure rule and its Earned Contract formula.
  Read it carefully and in full: it describes a method that is not
  standard industry practice, so do not substitute a different
  (e.g., simple pro-rata) approach.
- `contract_terms.md` — the specific terms of the manufacturer's warranty
  and the service contract, and the mileage assumption to use.
- `pricing_model_output.md` — the modeled pure premium to use for exposed
  months.

Read all three files carefully and in full before starting your analysis.

## What to produce

Following the method described in `kb_method_excerpt.md` exactly,
determine each month's exposure status, build the monthly loss-forecast
stream, and compute the Earned Contract / Unearned Contract schedule for
the life of the contract. Report the Earned/Unearned percentages and
unearned dollar liability at valuation Months 12, 24, 36, 48, and 60.

## Deliverables

Write to `/home/agent/results/`:

- `report.md` — your analysis. Must include: (1) an executive summary
  stating your headline result(s), (2) an explanation of how you
  determined each party's effective expiration month, (3) the monthly
  loss-forecast and Earned Contract schedule (or an equivalent grouped
  presentation covering all 60 months), and (4) a validation section.
- `answer.json` — a JSON object with exactly these keys:
  - `warranty_effective_expiration_month` (integer): the manufacturer's
    warranty's effective expiration month
  - `vsc_effective_expiration_month` (integer): the VSC's own effective
    expiration month
  - `first_exposed_month` (integer): the first month with nonzero
    exposure
  - `total_exposed_months` (integer): the total count of exposed months
  - `total_loss_forecast_usd` (float): the total loss forecast (`a`)
  - `valuation_results` (object): a mapping from each valuation month
    (as a string key: `"12"`, `"24"`, `"36"`, `"48"`, `"60"`) to an
    object with three keys: `earned_contract_pct` (float, e.g. `20.0`
    for 20%), `unearned_contract_pct` (float), and
    `unearned_liability_usd` (float)

## Execution notes

Work autonomously in a single turn. Do not ask clarifying questions —
make a reasonable, stated assumption if something is genuinely
ambiguous, and note it in `report.md`. Submit once; there is no
opportunity to revise after submission. Report all dollar figures to the
nearest cent and all percentages to two decimal places in `answer.json`.
