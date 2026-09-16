# rate-conflict-interest-analysis-01 — reviewer notes

Not shown to the agent. Sourcing, eligibility, construction, and what was
and wasn't live-verified during authoring.

## Source

**Type:** expert-designed. The company, facility, and documents are
synthetic; the mechanism — two authoritative-looking sources genuinely
disagreeing on a material fact, with no way to determine which controls
from the provided materials — is a real, common failure mode in
corporate finance/treasury work (contract terms vs. servicing
correspondence drifting apart is a well-known operational risk).

## Why this task exists

Five prior tasks in this repo tested two different eligibility
philosophies — fully-specified rule sets of increasing size and
complexity, and a withheld-but-real domain fact — and both produced no
sub-0.5 score across every tier tested. The common thread across all
five: every one of them asks the agent to *compute a confident answer*.
The difficulty was always "can it get the number right," never "should
it produce a single number at all."

This task tests a structurally different failure mode: **false confidence
under genuine, irreconcilable contradiction.** The two source documents —
an executed Credit Agreement stating a fixed 350 bps margin with an
explicit no-pricing-grid, amendment-only change clause, and a later
lender rate-reset notice stating 375 bps with no explanation — were
deliberately constructed so that neither is stale, neither is obviously
wrong, and nothing in the provided materials resolves which one governs.
The correct professional behavior is to notice this, flag it explicitly,
compute the requested deliverable under both readings, and recommend
escalating to resolve it — not to silently pick a side and report one
confident number, which is the behavior this task is designed to catch.

This differs from `fpa-variance-analysis-01`'s mechanism (also a
"spot an inconsistency" task): that inconsistency was *resolvable* — the
allocation basis and the email thread, read together, pointed to one
correct restatement. Here there is deliberately no resolution available;
the correct behavior is to say so, not to compute one.

## A design fix made during authoring, worth recording

The first draft of `answer.json`'s schema named the two required scenario
fields after their source documents directly
(`interest_expense_year1_under_credit_agreement_rate_usd` and
`interest_expense_year1_under_reset_notice_rate_usd`). That schema alone
would have handed the agent the entire correct strategy — "there are two
scenarios, one per document, compute both" — before it read a single
source file, defeating the purpose of testing whether it would notice
this on its own. Revised to a neutral, unordered `scenario_a_*` /
`scenario_b_*` pair with no hint of what distinguishes the two scenarios
or that they correspond one-to-one with the two documents; the checker
matches scenarios by their reported margin value rather than by slot
position, so labeling order carries no information and isn't graded.
This is a general lesson for any future task in this family: a
machine-checkable answer schema can itself leak the intended solution
strategy, and that risk is highest exactly when the mechanism being
tested is "does the agent independently discover structure in the
problem," which is precisely what this task tests.

## Eligibility

Departs from this repo's original "everything resolvable from the
provided materials" standard, similarly to `macrs-midquarter-
depreciation-01`, but in a different direction: here there genuinely is
no resolution available from the materials, and that is the point. There
is no single correct value for the Applicable Margin. Eligibility rests
on the conflict being realistic and well-constructed (both documents
equally plausible on their face, no stale-vs-current giveaway, no
pricing-grid mechanism that would make it silently resolvable), and on
grading rewarding the correct *behavior* (flag + compute both + recommend
escalation) rather than any specific numeric "winner."

## Verification performed during authoring

- **Programmatic correctness:** `solution/solve.py` computes both
  scenarios' interest schedules independently from the stated SOFR
  assumption and each document's margin; rerunning it reproduces
  `answer.json` byte-for-byte. Confirmed the two totals ($208,750.00 at
  350 bps vs. $215,000.00 at 375 bps, a $6,250 / 3.0% spread) and that
  the month-12 ending balance ($1,777,777.77) is identical under both
  scenarios, since amortization is rate-independent.
- **Order-independence check:** since the answer schema's `scenario_a`/
  `scenario_b` labels are arbitrary, verified that a golden-equivalent
  answer with the two scenarios swapped into the opposite slots still
  scores 1.0 against `check_programmatic.py` — confirming the checker
  actually matches by margin value, not by which slot the agent happened
  to use first.
- **Bug construction and detection, stress-tested before finalizing the
  checker:** built both plausible "silently picked a side" failure modes
  — adopting only the Credit Agreement's 350 bps rate, and adopting only
  the Rate Reset Notice's 375 bps rate, in each case with
  `conflict_detected` left false and only one scenario populated. Both
  score exactly **0.5** against `check_programmatic.py` (the populated
  scenario's fields pass; `conflict_detected` and the entire missing
  scenario fail). Also re-verified: missing agent directory and malformed
  JSON both score 0.0 without crashing.
- **Orchestration (`tests/test.sh`):** run end-to-end against the golden
  solution. `check_programmatic.py` correctly scored 1.0. The LLM judge
  step was run with no API key configured (deliberately, to avoid
  spending a shared credential not provisioned for this purpose) and
  correctly degraded to 0.0 with a clear note; combined reward came out
  to 0.30, matching `0.30*1.0 + 0.70*0.0` exactly.
- **Judge scoring logic (`tests/llm_judge.py`):** verified with the model
  call mocked (no live API spend): an all-PASS mock yields exactly 1.0; a
  mock that fails exactly one criterion (the highest-weight one,
  `conflict-explicitly-identified`, weight 6 of 49 total) yields the
  exact expected reduced score (0.8776); a malformed (non-PASS/FAIL) mock
  response is caught as a graceful error rather than crashing.
- **Not live-verified:** an actual LLM call grading the golden report
  end-to-end, and a live `docker build` of `environment/Dockerfile` — same
  caveats as the five predecessor tasks in this repo, for the same
  reasons.

## Calibration status

Not yet run as of this writing. This is the sixth task in this repo and
the first to test a behavioral/epistemic failure mode (false confidence
under contradiction) rather than a knowledge or rule-application gap;
its actual difficulty against real models is unverified until the same
three-tier (Haiku/Sonnet/Opus) blind evaluation process is run and graded
against `tests/`.
