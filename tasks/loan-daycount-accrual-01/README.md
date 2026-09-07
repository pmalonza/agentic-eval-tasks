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

## Calibration results (real run, 2026-09-08)

Ran the same real calibration process used for the two predecessor
tasks: Haiku, Sonnet, and Opus each solved the task blind, from
`instruction.md` + the two `environment/data/` files only, using code
execution to run the actual simulation. Opus hit the same "subagents
can't write a file literally named report.md" guardrail seen in prior
rounds, correctly reported it, and returned full file content as text
instead of working around it.

**All three tiers got `answer.json` numerically exact** — none defaulted
to the flat-1/12 or 30/360 shortcut. All three correctly derived that
February 2028 has 29 days (a leap year) and February 2027 has 28, and
applied Actual/360 throughout. One incidental finding: Opus discovered a
stale pre-existing `answer.json` at its write path using the wrong
30/360-style figures (apparently left over from shared sandbox state
across subagent runs in this session, not something this task's
authoring introduced) and correctly identified it as inconsistent with
the stated day-count convention before overwriting it with the correct
Actual/360 result — a genuinely reassuring sign of the model
cross-checking its own output rather than trusting a suspicious existing
file.

Programmatic score was 1.0 for all three. Rubric scores, graded by hand
criterion-by-criterion against `tests/rubric.json` (in lieu of a live
LLM judge call, per this project's policy against spending shared
credentials on unauthorized side calls):

| Model | Programmatic | Rubric | Reward (0.30×prog + 0.70×rubric) |
|---|---|---|---|
| Haiku | 1.0 | 47/62 = 0.758 | **0.831** |
| Sonnet | 1.0 | 57/62 = 0.919 | **0.944** |
| Opus | 1.0 | 62/62 = 1.000 | **1.000** |

This is the widest spread seen across all three tasks calibrated in this
repo so far. Haiku's report never once names "Actual/360" or states any
day-count formula despite computing it correctly under the hood, has no
day-count column in its schedule table, has no assumptions section, and
mischaracterizes the $100,000 cash threshold as an enforceable
"liquidity covenant breach" requiring a "compliance" fix — `loan_terms.md`
only ever describes that figure as the cash-sweep computation floor, not
an independently breachable covenant with consequences. Sonnet lost
points only on failing to state the Actual/360 formula explicitly in the
report itself (it names the convention and shows day-counts, but never
writes out `annual_rate/360 × days`). Opus explicitly stated the formula,
showed a day-count column, included a totals row that reconciles
scheduled principal + sweeps to the original principal, and — critically
— included an assumption explicitly clarifying that the $100,000
threshold is "a sweep threshold, not a hard funding constraint," despite
using the looser word "covenant" once in its executive summary,
correcting what could otherwise have been the same misstatement Haiku
made.

## Calibration verdict

**FAIL (too easy).** No model scored at or below the 0.5 ceiling — even
Haiku, the weakest tier and the one that showed real, substantive
report-quality gaps, still scored 0.831. This is the third independent
difficulty mechanism tested for real in this repo (after a hidden
cross-file ratio mismatch and multi-rule sequencing/timing), and the
third to fail to clear the ceiling.

**Diagnosis.** The design bet here was specifically that a plausible,
well-known wrong shortcut (defaulting to flat 1/12, indistinguishable in
practice from 30/360) — fully specified as wrong in the prompt materials
but still tempting because it's the more common and simpler convention
— would trip up at least one tier. It didn't: all three models correctly
read the Actual/360 instruction, correctly derived real calendar day
counts including the leap year, and produced numerically exact answers.
The rubric did surface the largest tier-to-tier spread of any task in
this repo (0.831 to 1.000), driven by whether a model's *report*
demonstrated the reasoning behind the correct numbers (explicit formula,
day-count column, correct characterization of what the $100k figure
actually is) rather than just landing on them — but demonstrating
reasoning quality is a communication/rigor axis, not a correctness axis,
and it isn't severe enough on its own to pull a score below 0.5.

**Recommendation.** Three different difficulty mechanisms — hidden
cross-file inconsistency, multi-rule sequencing, and a named-but-easy-
to-substitute wrong convention — have now each been tested for real
against the same three tiers and each left every tier comfortably above
0.5, with Haiku's worst showing (0.831 here) still nearly double the
ceiling. All three mechanisms share a common shape: a fully-specified
rule that a model with code-execution tools can implement exactly once
it reads the rule. The next attempt should test a mechanism that doesn't
share that shape — either a genuine judgment call under real ambiguity
(not a hidden-but-resolvable inconsistency), or enough additional
interacting state (e.g. a multi-tranche payment waterfall with priority
ordering) that a single implementation bug plausibly cascades across
most of the schedule rather than costing a few rubric points on
communication quality.
