# loan-daycount-accrual-01 — reviewer notes

Not shown to the agent. Sourcing, eligibility, construction, and what
was and wasn't live-verified during authoring.

## Source

**Type:** expert-designed (no single external source paper/dataset).
Actual/360 is a standard, widely-used real-world commercial loan
day-count convention; the specific company, loan terms, and monthly
cash-flow series here are synthetic but internally consistent — every
number in `environment/data/` and `solution/answer.json` derives from a
single simulation (`solution/solve.py`) run once over a fixed input
series, not independently invented per field.

## Why this task exists

Built directly after `debt-covenant-runoff-01`'s real calibration also
failed to clear the 0.5 ceiling (Haiku 0.955, Sonnet 0.977, Opus 1.000)
despite using a structurally different mechanism (multi-rule sequencing)
than `fpa-variance-analysis-01`'s hidden-ratio mismatch. Both prior
mechanisms shared a common trait: once the rule was stated explicitly
and completely, a model with code-execution tools implemented it
correctly regardless of how many steps or how unusual the sequencing.

This task tests a different kind of difficulty: a **plausible wrong
convention that is fully specified in the prompt materials, but easy to
substitute for a superficially similar and much more common
convention** — specifically, defaulting to a flat 1/12-of-the-annual-rate
monthly interest fraction (the convention used, correctly, in this
task's own predecessor `debt-covenant-runoff-01`) or a 30/360 day-count,
instead of implementing true Actual/360 with the real number of calendar
days per month. Reusing the identical loan mechanics, cash-flow series,
and dollar magnitudes as `debt-covenant-runoff-01` (only the interest
day-count basis changes) makes the two tasks directly comparable and
means a model that pattern-matches "this looks like the same kind of
loan-schedule problem I've solved before" and reapplies the old flat
1/12 shortcut will produce **exactly** that predecessor task's golden
answer — a clean, unambiguous, and easily detected wrong-answer
signature.

The 24-month window (January 2027 - December 2028) was deliberately
chosen to span two different Februaries — 2027 (28 days, not a leap
year) and 2028 (29 days, a leap year, since 2028 is divisible by 4) — so
a correct implementation must also get real calendar/leap-year day
counts right, not just recognize that Actual/360 differs from a flat
fraction in the abstract.

## Construction mechanism

1. Reused `debt-covenant-runoff-01`'s exact principal, scheduled
   amortization, covenant rate step-up, starting cash, minimum cash
   threshold, sweep percentage, and monthly free-cash-flow series
   unchanged.
2. Replaced the interest section of `loan_terms.md` with an explicit
   Actual/360 day-count definition, explicitly naming and ruling out
   the 30/360 alternative by name, and anchored the schedule to a real
   calendar starting January 2027 so `solution/solve.py` could compute
   real day counts via Python's `calendar.monthrange()`.
3. `solution/solve.py` deterministically simulates all 24 months;
   nothing in `solution/answer.json` or `solution/report.md` was
   hand-typed.
4. Constructed both plausible wrong-convention bugs (flat 1/12, and
   30/360 with a fixed 30-day month) during authoring and confirmed both
   collapse to numerically identical wrong output — see "Verification
   performed" below.

## Eligibility

Not paper-sourced, so the paper-recency requirement doesn't apply.
Eligibility rests on internal validity and fairness: Actual/360's exact
formula is stated in full in `loan_terms.md` (this is not a task that
withholds the formula and expects the agent to already know it from
outside knowledge) — the discriminator is whether the agent notices and
correctly applies the stated, unusual convention rather than defaulting
to a more familiar one it wasn't told to use.

## Verification performed during authoring

- **Programmatic correctness:** `solution/solve.py` computes every
  `answer.json` field from `loan_terms.md`'s fixed constants and
  `monthly_cash_flow.csv`; rerunning it reproduces `answer.json`
  byte-for-byte.
- **Bug construction and detection, stress-tested before finalizing the
  checker:** built both plausible wrong-convention implementations
  (flat annual-rate/12, and 30/360 with a fixed 30-day month) and
  confirmed they produce **numerically identical** wrong output to each
  other (expected: 30/360 = 1/12 exactly when every month is treated as
  30 days) — and that this wrong output is byte-for-byte the golden
  `answer.json` of `debt-covenant-runoff-01`, the predecessor task that
  correctly used flat 1/12 throughout. The smallest golden-vs-bug field
  delta is $160.35 (`month_6_balance_usd`); reused the same flat $25
  absolute tolerance from the predecessor task's checker (already
  justified there against a percentage-tolerance flaw) and confirmed it
  fails the bug on 5 of 10 fields (score 0.5) while scoring 1.0 against
  the golden answer. Also re-verified: missing agent directory scores
  0.0 without crashing; malformed JSON scores 0.0 without crashing;
  UTF-8-BOM-prefixed valid JSON scores 1.0.
- **Orchestration (`tests/test.sh`):** run end-to-end against the golden
  solution (`solve.sh` output copied into a scratch results directory
  alongside `solution/report.md`). `check_programmatic.py` correctly
  scored 1.0. The LLM judge step was run with no API key configured
  (deliberately, to avoid spending a shared credential not provisioned
  for this purpose) and correctly degraded to 0.0 with a clear note; the
  combined reward came out to 0.30, matching `0.30*1.0 + 0.70*0.0`
  exactly.
- **Judge scoring logic (`tests/llm_judge.py`):** verified separately
  with the model call mocked (no live API spend): an all-PASS mock
  response yields a judge score of exactly 1.0; a mock that fails
  exactly one criterion (the highest-weight one,
  `daycount-basis-correct-not-flat-monthly`, weight 5 of 62 total)
  yields the exact expected reduced score (0.9194); a malformed
  (non-PASS/FAIL) mock response is caught and reported as a graceful
  error rather than crashing.
- **Not live-verified:** an actual LLM call grading the golden report
  end-to-end, and a live `docker build` of `environment/Dockerfile` (no
  Docker runtime available in the authoring environment) — same caveats
  as the two predecessor tasks in this repo, for the same reasons.
