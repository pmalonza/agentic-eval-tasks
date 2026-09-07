# fpa-variance-analysis-01 — reviewer notes

Not shown to the agent. Sourcing, eligibility, construction, and what
was and wasn't live-verified during authoring.

## Source

**Type:** expert-designed (no single external source paper/dataset).
Financial-planning variance analysis with a hidden allocation error is a
recurring, realistic failure mode in real FP&A work; the specific
company, product lines, and dollar figures here are synthetic but
internally consistent — every number in `environment/data/` and
`solution/answer.json` is derived from a single coherent underlying
scenario (see the construction mechanism below), not independently
invented per file.

## Construction mechanism

1. A budget P&L for two product lines was defined first (units, price,
   direct cost/unit, and a 10%-of-revenue overhead pool allocated
   pro-rata by revenue share).
2. An "actual" quarter was defined by three independent perturbations:
   a modest volume decline in both products (real, but deliberately the
   smallest driver), a price cut in Product B only (the real root
   cause), and a one-time $55,000 cost (the warehouse consolidation)
   added to the overhead pool.
3. The allocation error was introduced as a single change: the one-time
   cost's split was set to 100%/0% (Product A / Product B) instead of
   the pro-rata-by-revenue split used for the rest of the pool. This is
   the only place in the whole construction where the "as booked" and
   "correctly allocated" views diverge — everything else is identical
   between them.
4. The email thread was written last, to describe the warehouse
   consolidation as shared/company-wide infrastructure *without* ever
   mentioning how the cost was booked — establishing the fact needed to
   catch the anomaly, without stating the anomaly itself.
5. Every downstream number (`environment/data/*.csv`,
   `solution/answer.json`, the bridge and attribution tables in
   `solution/report.md`) was computed programmatically from step 1-3 by
   `solution/solve.py` and cross-checked by hand before being written
   into the CSVs — see "Verification performed" below.

## Eligibility

Not paper-sourced, so the paper-recency requirement doesn't apply.
Eligibility here rests on internal validity: the scenario is a single
coherent construction (not independently-invented numbers stitched
together), the bridge ties out exactly, and the trap is discoverable
strictly from the provided files (no external knowledge required, no
information hidden from all three source files simultaneously).

## Why this is hard because of the domain, not because of confusion

The difficulty is that the allocation anomaly is *plausible* — nothing
in `cost_allocation_schedule.csv` is internally inconsistent, and
nothing in `email_thread.md` explicitly says the booking was wrong. The
only way to catch it is to notice that the one-time cost's allocation
basis (100% to one product) doesn't match the standard pool's basis
(pro-rata by revenue) *and* that the email thread gives no reason for
that difference — a cross-file consistency check a shallow reader has no
reason to perform unless they already suspect something.

## Verification performed during authoring

- **Programmatic correctness:** `solution/solve.py` computes every
  `answer.json` field from the three source CSVs/text file (nothing
  hand-typed); rerunning it reproduces `answer.json` byte-for-byte.
  `tests/check_programmatic.py` was run against the golden answer
  (score 1.0), against a missing agent directory (score 0.0, no crash),
  against malformed JSON (score 0.0, no crash), and against a
  deliberately-wrong answer (correctly scored 9/11 fields, flagging
  exactly the two wrong ones).
- **Bridge tie-out:** verified programmatically that budget GP + the
  sum of the bridge components equals actual GP to the cent, and that
  the corrected vs. as-booked overhead split sums to the same total
  overhead pool either way (confirming the misallocation is a pure
  attribution effect, not a change to the total-company number).
- **Orchestration (`tests/test.sh`):** run end-to-end against the golden
  solution. `check_programmatic.py` correctly scored 1.0. The LLM judge
  step was run with no API key configured (deliberately, to avoid
  spending a shared credential not provisioned for this purpose) and
  correctly degraded to a score of 0.0 with a clear note rather than
  crashing; the combined reward came out to 0.30, matching
  `0.30*1.0 + 0.70*0.0` exactly.
- **Judge scoring logic (`tests/llm_judge.py`):** verified separately
  with the model call mocked (no live API spend): an all-PASS mock
  response yields a judge score of exactly 1.0 against `rubric.json`'s
  weights; a mock that fails exactly one criterion yields the correct
  reduced score and flags exactly that criterion; a malformed
  (non-PASS/FAIL) mock response is caught and reported as a graceful
  error rather than crashing.
- **Not live-verified:** an actual LLM call grading the golden report
  end-to-end (requires a provisioned judge API key — not exercised
  during authoring, per above), and a live `docker build` of
  `environment/Dockerfile` (no Docker runtime available in the
  authoring environment). The Dockerfile uses a standard, well-trodden
  `python:3.11-slim` + `pip install` pattern; a reviewer with Docker
  available should confirm the build before this task is used against
  a real agent.
