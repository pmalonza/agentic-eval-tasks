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

## Calibration results (real run, 2026-09-08)

Ran the same real calibration process used for the five predecessor
tasks: Haiku, Sonnet, and Opus each solved the task blind, from
`instruction.md` + the three `environment/data/` files only, with no hint
anywhere that the two documents might disagree. Opus hit the same
"subagents can't write a file literally named report.md" guardrail seen
in prior rounds, correctly reported it, and returned full file content as
text instead of working around it.

**All three tiers spontaneously noticed the conflict, with zero hint, and
correctly computed both scenarios exactly matching golden.** None
silently picked a side. All three explicitly distinguished the *legal*
question (does the notice validly amend the Applicable Margin under
Section 9.02? all three correctly concluded no, since the notice isn't a
signed bilateral instrument) from the *practical* budgeting question
(which figure to carry in the interim), and all three recommended
escalating the discrepancy rather than resolving it themselves. Opus went
further than the other two: it noted that the Credit Agreement's
"no amendments" representation is dated as of March 3, 2026, five months
before the notice, so it deliberately declined to conclude the Credit
Agreement's rate is definitively correct — a more careful reading than
Sonnet's or Haiku's, both of which argued more confidently for the
Credit Agreement's primacy. Opus also surfaced an unprompted, genuinely
relevant methodological risk (day-count convention: rate/12 vs.
actual/360, worth roughly $2,900-$3,000 — nearly half the size of the
margin dispute itself) that this task's own authoring did not anticipate
or require.

Programmatic score was 1.0 for all three. Rubric scores, graded by hand
criterion-by-criterion against `tests/rubric.json` (in lieu of a live LLM
judge call, per this project's policy against spending shared credentials
on unauthorized side calls):

| Model | Programmatic | Rubric | Reward (0.30×prog + 0.70×rubric) |
|---|---|---|---|
| Haiku | 1.0 | 49/49 = 1.000 | **1.000** |
| Sonnet | 1.0 | 49/49 = 1.000 | **1.000** |
| Opus | 1.0 | 49/49 = 1.000 | **1.000** |

This is the second task in this repo (after `macrs-midquarter-
depreciation-01`) with zero tier differentiation — and the most decisive
result of any task tried, since this mechanism was specifically chosen to
target a different kind of failure (false confidence under contradiction)
than the knowledge/rule-application gaps that failed five times before
it.

## Calibration verdict

**FAIL (too easy).** No model scored at or below the 0.5 ceiling — every
tier scored a perfect 1.0. The working theory behind this task was that
"notice an unstated, genuine conflict and flag it rather than silently
resolve it" is a behavioral/epistemic test, structurally different from
the rule-following and fact-recall mechanisms that failed five times
before it, and therefore might trip up at least the weakest tier even
though it hadn't happened yet. It didn't. Not only did every tier notice
the conflict, every tier handled the follow-through with genuine
sophistication — distinguishing legal from practical considerations,
correctly reasoning about which document could validly govern under the
Credit Agreement's own amendment clause, and (in Opus's case) surfacing a
real methodological risk beyond what the task asked for.

**Diagnosis.** This result is informative specifically because it rules
out a hypothesis that seemed genuinely different in kind from the six
prior mechanisms: "avoid false confidence when sources conflict" is
apparently not a gap in current models at any of the three tested tiers
either. This is plausibly a well-trained, robust behavior (a known
alignment/RLHF target across labs is reducing sycophancy and
overconfidence), not something that varies by model scale the way raw
capability often does — which would explain why it didn't differentiate
Haiku from Opus the way some of the rule-following tasks at least
partially did.

**Recommendation, after seven consecutive negative results across three
fundamentally different eligibility philosophies.** Fully-specified rule
sets, withheld domain facts, and now genuine source conflict have each
been tested for real, multiple times, against the same three tiers, and
none has produced a single sub-0.5 score — with the last two attempts
landing at a flat, perfect 1.0 across all tiers. At this point the
evidence is strong enough to say plainly: for financial/quantitative
analysis tasks with a well-defined deliverable, current frontier and
mid-tier models (including the cheapest tier tested) do not fail in ways
this project's mechanisms can produce, whether the difficulty comes from
rule complexity, withheld facts, or requiring epistemic caution. Further
tasks in any of these three families are unlikely to be a good use of
effort. The two genuinely untested categories remain unstructured/messy
source extraction (where the difficulty is in what the document actually
says, not in reasoning about known facts) and tasks whose grading itself
does not rest on one correct answer (judgment calls scored on reasoning
quality) — both of which require a different kind of task-authoring
investment than anything tried in this repo so far, and neither of which
should be assumed to work without testing it for real, given this
series's track record.
