# Q2 gross margin variance analysis

You are an FP&A analyst. Gross margin for Q2 came in at 23.33% against a
budget of 28.42%. Finance needs a variance bridge that explains the miss
and a recommendation for Q3 reporting.

## Inputs

All files are under `/home/agent/data/`:

- `q2_budget_vs_actual.csv` — budget vs. actual P&L by product line
  (Product A, Product B), including volume, price, direct cost, allocated
  overhead, COGS, gross profit, and gross margin %.
- `cost_allocation_schedule.csv` — the Q2 overhead allocation detail:
  each cost pool component, its stated allocation basis, the total
  amount, and how much was allocated to each product line.
- `email_thread.md` — a short Finance/Ops email thread about a warehouse
  consolidation that happened mid-quarter.

## What to produce

Build a gross-profit variance bridge from budget to actual that ties out
exactly (budget GP + sum of your bridge components = actual GP, within
$1). Then produce a product-line attribution of the miss: how much of
it belongs to Product A vs. Product B, both as currently booked and
under whatever correction your own review of the source material
supports, if any.

State which single factor is the largest driver of the total miss, and
which product line should be the priority for corrective action based
on your corrected attribution.

## Deliverables

Write to `/home/agent/results/`:

- `report.md` — your analysis. Must include: (1) an executive summary
  stating the headline numbers and your recommendation, (2) the full
  variance bridge with dollar figures for every component, (3) your
  assessment of the Q2 cost allocation schedule, including any
  concerns about how costs were assigned to each product line, (4) a
  product-line attribution table (budget GM%, as-booked actual GM%,
  your attribution's GM%, and the point miss under each, for both
  products), and (5) a recommendation for Q3 reporting.
- `answer.json` — a JSON object with exactly these keys:
  - `total_gm_miss_points` (float): budget GM% minus actual GM%, in
    percentage points
  - `total_gp_variance_usd` (float): actual GP minus budget GP, in
    dollars (negative if GP declined)
  - `product_a_miss_points_as_booked` (float)
  - `product_b_miss_points_as_booked` (float)
  - `product_a_miss_points_corrected` (float)
  - `product_b_miss_points_corrected` (float)
  - `largest_single_driver` (string): one of `"volume"`, `"price"`,
    `"overhead"`
  - `one_time_cost_usd` (float): the dollar amount of the one-time cost
    item you identify in the allocation schedule
  - `one_time_cost_corrected_product_a_usd` (float): what you determine
    Product A's fair share of that cost should be, based on your own
    review of the source material
  - `one_time_cost_corrected_product_b_usd` (float): same, for Product B
  - `recommended_focus_product` (string): `"Product A"` or `"Product B"`
    — whichever line should be the priority for corrective action based
    on your attribution

## Execution notes

Work autonomously in a single turn. Do not ask clarifying questions —
make a reasonable, stated assumption if something is genuinely
ambiguous, and note it in `report.md`. Submit once; there is no
opportunity to revise after submission. All dollar figures should be
accurate to the nearest $100 and all point figures to the nearest 0.1
point.
