# debt-covenant-runoff-01 — reviewer notes

Not shown to the agent. Sourcing, eligibility, construction, and what
was and wasn't live-verified during authoring.

## Source

**Type:** expert-designed (no single external source paper/dataset). A
term loan with a covenant-triggered rate step-up and a discretionary
cash sweep is a standard credit-analysis structure; the specific
company, loan terms, and monthly cash-flow series here are synthetic
but internally consistent — every number in `environment/data/` and
`solution/answer.json` derives from a single simulation
(`solution/solve.py`) run once over a fixed input series, not
independently invented per field.

## Why this task exists

Built directly after `fpa-variance-analysis-01` was calibration-tested
three times and never produced a model score at or below the 0.5
ceiling (see that task's README). The diagnosis there was that
"compute a ratio, notice a mismatch, connect it to one stated fact" is
not a hard mechanism for current frontier models, however well the
surface narration is hidden. This task deliberately uses a
**structurally different** difficulty mechanism: long-horizon,
multi-period state tracking with several interacting timing rules,
where a plausible misreading of exactly one rule (most likely: applying
the covenant's rate step-up starting the trigger month itself, instead
of the month after) produces a confidently-wrong-but-plausible final
answer.

The key design bet: tedious arithmetic across 24 months is *not*
inherently hard for an agent with code-execution tools — it will just
write a script and get exact numbers, same as the golden solution does.
The difficulty has to come from correctly interpreting the
*specification*, not from the volume of arithmetic. `loan_terms.md` is
written as precise prose (deliberately not a table or pseudocode) that
requires the agent to correctly sequence, per month: (1) interest
accrues on the balance carried in from the end of the prior month,
after that month's scheduled principal *and* sweep; (2) the covenant
check happens each month, but the rate step-up applies starting the
*following* month, not the trigger month itself; (3) the sweep is
computed *after* that month's own interest and scheduled principal are
deducted, not before; (4) once the balance hits zero, no further debt
service occurs even though the loan hasn't reached its 24-month
maturity date.

## Construction mechanism

1. Fixed loan terms were set first (principal, term, scheduled
   principal, base/elevated rates, minimum cash threshold, starting
   cash, sweep percentage) — see `environment/data/loan_terms.md`.
2. A 24-month free-cash-flow series was authored with exactly one
   negative month (month 7, -$15,000) to give the covenant exactly one,
   unambiguous trigger point, and enough positive cash flow elsewhere
   for the sweep to meaningfully accelerate payoff before month 24 (so
   the "payoff stops debt service" rule is actually exercised, not just
   theoretical).
3. `solution/solve.py` deterministically simulates all 24 months from
   those two inputs — nothing in `solution/answer.json` or
   `solution/report.md` was hand-typed; both were generated from the
   simulation's output.
4. `tests/check_programmatic.py`'s tolerance was stress-tested against
   a deliberately constructed instance of the most tempting misreading
   (applying the elevated rate to the trigger month itself) before
   being finalized — see "Verification performed" below.

## Eligibility

Not paper-sourced, so the paper-recency requirement doesn't apply.
Eligibility rests on internal validity: the simulation is a single
coherent construction, every reported figure is reproducible
byte-for-byte by rerunning `solve.py`, and the discriminating rules
(rate-step-up timing, interest basis, sweep ordering, payoff cutoff)
are all stated plainly in `loan_terms.md` — nothing is hidden or
requires information outside the provided files.

## Verification performed during authoring

- **Programmatic correctness:** `solution/solve.py` computes every
  `answer.json` field from `loan_terms.md`'s fixed constants and
  `monthly_cash_flow.csv` (nothing hand-typed); rerunning it reproduces
  `answer.json` byte-for-byte.
- **Tolerance design, stress-tested against a real bug:**
  `tests/check_programmatic.py` initially used a percentage-based
  tolerance (`max($50, 0.3%×golden)`) per dollar field. Testing it
  against a deliberately constructed "same-month rate timing" bug
  (applying 8.70% to month 7's own interest instead of starting month
  8 — a $1,145 systematic error) showed the tolerance correctly failed
  the smaller-magnitude `total_interest_paid_usd` field (~$84k, so
  0.3%≈$252, well under the $1,145 bug) but **incorrectly passed** the
  larger-magnitude `month_24_cash_balance_usd` field (~$1.2M, so
  0.3%≈$3,617, larger than the bug) — the same absolute-dollar bug
  slipped through on one field purely because percentage tolerance
  scales with a field's own magnitude while the bug's dollar impact
  does not. Fixed by switching every dollar field to a flat $25
  absolute tolerance (justified: correct implementations should match
  to pennies here, since the prompt specifies rounding only final
  reported values). Re-verified: golden-vs-golden still scores 1.0, and
  the same constructed bug now correctly fails on both affected fields
  (score dropped from 0.9 to 0.8). Also verified: missing agent
  directory scores 0.0 without crashing; malformed JSON scores 0.0
  without crashing; a UTF-8-BOM-prefixed but otherwise valid
  `answer.json` scores 1.0 (lesson carried over from a real bug found
  during `fpa-variance-analysis-01`'s calibration).
- **Orchestration (`tests/test.sh`):** run end-to-end against the
  golden solution (`solve.sh` output copied into a scratch results
  directory alongside `solution/report.md`). `check_programmatic.py`
  correctly scored 1.0. The LLM judge step was run with no API key
  configured (deliberately, to avoid spending a shared credential not
  provisioned for this purpose) and correctly degraded to a score of
  0.0 with a clear note rather than crashing; the combined reward came
  out to 0.30, matching `0.30*1.0 + 0.70*0.0` exactly.
- **Judge scoring logic (`tests/llm_judge.py`):** verified separately
  with the model call mocked (no live API spend): an all-PASS mock
  response yields a judge score of exactly 1.0; a mock that fails
  exactly one criterion (the highest-weight one, `covenant-month-
  correct-with-timing-explained`, weight 5 of 62 total) yields the
  exact expected reduced score (0.9194) and flags exactly that
  criterion; a malformed (non-PASS/FAIL) mock response is caught and
  reported as a graceful error (`score: 0.0`, explanatory note) rather
  than crashing.
- **Not live-verified:** an actual LLM call grading the golden report
  end-to-end (requires a provisioned judge API key — not exercised
  during authoring, per above), and a live `docker build` of
  `environment/Dockerfile` (no Docker runtime available in the
  authoring environment). The Dockerfile uses the same standard,
  well-trodden `python:3.11-slim` + `pip install` pattern already used
  (unverified for the same reason) by `fpa-variance-analysis-01`.

## Calibration results (real run, 2026-09-08)

Ran the same real calibration process used for `fpa-variance-analysis-01`:
Haiku, Sonnet, and Opus each solved the task blind, from `instruction.md`
+ the two `environment/data/` files only, using code execution to run
the actual 24-month simulation (not hand arithmetic). Each was explicitly
instructed to stop and report rather than route around any tool block —
both Opus and Haiku hit the same "subagents can't write a file literally
named report.md" guardrail seen during `fpa-variance-analysis-01`'s
calibration, correctly reported it, and returned full file content as
text instead of working around it.

**All three tiers got `answer.json` numerically exact** —
`covenant_trigger_month=7`, `payoff_month=17`,
`total_interest_paid_usd=84076.95`, and every other field matched the
golden values to the cent. None of the three models misread the
rate-step-up timing (the trap this task was specifically built around):
all three explicitly stated that Month 7's own interest is still charged
at the base rate and that the elevated 8.70% rate first applies in
Month 8, and all three explicitly reasoned about (not just stumbled
into) the sweep-after-debt-service ordering.

Programmatic score was 1.0 for all three (every field within the flat
$25 tolerance / exact match). Rubric scores, graded by hand
criterion-by-criterion against `tests/rubric.json` (in lieu of a live
LLM judge call, per this project's policy against spending shared
credentials on unauthorized side calls):

| Model | Programmatic | Rubric | Reward (0.30×prog + 0.70×rubric) |
|---|---|---|---|
| Haiku | 1.0 | 58/62 = 0.935 | **0.955** |
| Sonnet | 1.0 | 60/62 = 0.968 | **0.977** |
| Opus | 1.0 | 62/62 = 1.000 | **1.000** |

The two rubric points Haiku lost: it never stated an explicit
assumption anywhere a reading of `loan_terms.md` was ambiguous (no
"Assumptions" section at all, unlike Sonnet and Opus), and its own
reconciliation math didn't tie out — it reported total cash sweeps of
"$456,649" and separately noted this "exceeds the original $1.50M by
$19,149 due to rounding," when $19,149 is a real arithmetic
inconsistency (its own per-month sweep figures sum to ~$437,500,
matching golden), not a rounding artifact — a sign the schedule wasn't
actually checked for internal consistency, even though `answer.json`
itself came out exact. Sonnet lost the same "internal validation"
point for a different reason: it claimed the files were "verified...
cross-checked by hand" but that claim lived in its chat response, not
inside `report.md` itself, so the deliverable alone doesn't demonstrate
the check. Opus's `report.md` included an in-report reconciliation
(scheduled principal + sweeps = original principal, cash roll-forward
ties to the cent) and lost no points.

## Calibration verdict

**FAIL (too easy).** No model scored at or below the 0.5 ceiling — the
lowest of three tiers, Haiku, still scored 0.955. Unlike
`fpa-variance-analysis-01`, this is a **single-round** result (the
mechanism wasn't iterated on after this first real test), but the
outcome is the same: switching to a structurally different difficulty
mechanism (long-horizon sequencing/timing rules instead of a hidden
cross-file ratio mismatch) did not clear the ceiling either. All three
models, including Haiku, correctly navigated every interacting rule
this task was designed to trip up on — the rate-step-up timing, the
interest-basis lag, and the sweep-after-debt-service ordering — via
code execution, exactly as the design bet anticipated they might.

**Diagnosis.** The design bet was that correct *rule interpretation*
(as opposed to arithmetic volume) would be the hard part for a model
with code-execution tools. That bet was wrong in the way that mattered
for calibration: writing a correct simulation from a precisely-worded
prose spec turned out to be well within reach for all three tiers
tested, including Haiku. The rubric did surface real, if minor,
differentiation between tiers (Haiku's missing assumptions section and
uncaught arithmetic inconsistency, Sonnet's validation claim living
outside the deliverable) — so the discriminator isn't completely inert,
it just isn't nearly severe enough to pull any tier below 0.5.

**Recommendation.** As with `fpa-variance-analysis-01`, do not tune
this task's data or rubric weights to chase the 0.5 ceiling — that
would mean reverse-engineering the rubric from which criteria these
three models happened to fail, which is explicitly against this
project's own authoring rules. A future attempt at clearing calibration
for either task would need a *harder class of trap* than either
"spot a mismatched ratio" or "get a multi-rule sequencing spec right" —
both have now been tested for real and both leave every tested tier
comfortably above 0.5.
