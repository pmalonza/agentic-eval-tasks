# Agentic Eval Tasks

A small collection of expert-authored tasks for evaluating whether an AI
agent can do real, professional-grade work — not toy puzzles with one
right answer, graded criterion-by-criterion against an expert rubric
rather than exact-match.

This follows the design logic behind evaluation frameworks like
AfterQuery's frontier-model benchmarks and Mercor's APEX methodology:
calibrate difficulty so the *best* models mostly succeed and weaker or
specific models fail on a predictable, diagnosable point — a task every
model aces (or every model fails) produces no signal. See
[`docs/task-authoring-guide.md`](docs/task-authoring-guide.md) for the
full authoring contract every task in this repo follows.

## Tasks

| Task | Domain | Type | Calibration | Description |
|---|---|---|---|---|
| [`fpa-variance-analysis-01`](tasks/fpa-variance-analysis-01/) | Finance / FP&A | Result Interpretation | ❌ **Fail (too easy)** — see below | Explain a Q2 gross-margin miss from a budget-vs-actual P&L and a cost allocation schedule that contains a booking error — correctly re-attributing the miss between two product lines requires cross-checking the allocation basis against an email thread, not just reconciling the arithmetic. |
| [`debt-covenant-runoff-01`](tasks/debt-covenant-runoff-01/) | Finance / Credit Analysis | End-to-End Analysis | ❌ **Fail (too easy)** — see below | Build a 24-month term-loan runoff schedule with an interacting covenant rate step-up and cash sweep — getting the month-to-month sequencing right (rate-step-up timing, interest basis, sweep-after-debt-service ordering, payoff cutoff) matters as much as any single formula. |
| [`loan-daycount-accrual-01`](tasks/loan-daycount-accrual-01/) | Finance / Credit Analysis | End-to-End Analysis | ❌ **Fail (too easy)** — see below | Same loan mechanics as `debt-covenant-runoff-01`, but interest accrues on a real-calendar Actual/360 basis (spanning a leap-year February) instead of a flat monthly fraction — the trap is a plausible, named-but-easy-to-substitute wrong day-count convention that collapses to a different task's already-correct answer. |
| [`tranche-waterfall-runoff-01`](tasks/tranche-waterfall-runoff-01/) | Finance / Credit Analysis | End-to-End Analysis | ❌ **Fail (too easy)** — see below | A three-tranche (Senior/Mezzanine/Subordinated) credit facility with a strict payment waterfall, a PIK-vs-cash toggle, and a single covenant trigger producing two effects of deliberately different duration — testing whether compound multi-entity complexity, not just one loan's rules, could push a weaker tier below the ceiling. It didn't. |
| [`macrs-midquarter-depreciation-01`](tasks/macrs-midquarter-depreciation-01/) | Finance / Corporate Tax | End-to-End Analysis | ❌ **Fail (too easy)** — see below | Tests a domain-knowledge gap instead of a fully-specified rule: the task never states that IRS rules require the MACRS mid-quarter depreciation convention when >40% of a year's basis is placed in service in Q4. All three tiers already knew the rule and the exact percentage tables cold, with no internet access — the flattest (1.0/1.0/1.0) result of any task in this repo. |
| [`rate-conflict-interest-analysis-01`](tasks/rate-conflict-interest-analysis-01/) | Finance / Treasury | End-to-End Analysis | ❌ **Fail (too easy)** — see below | Tests an epistemic/behavioral failure mode instead of knowledge or rule-following: two equally authoritative source documents genuinely and irreconcilably conflict on a loan's interest margin, with no hint that they disagree. All three tiers spontaneously noticed and flagged the conflict rather than silently picking a side — a second flat 1.0/1.0/1.0 result. |
| [`kb-earned-contract-liability-01`](tasks/kb-earned-contract-liability-01/) | Finance / Actuarial | Code Generation | ❌ **Fail (too easy)** — see below | First paper-sourced task: implements a real actuarial method published February 2026 (CC BY 4.0, after this session's own training cutoff) that no model could have memorized. Genuinely novel content was implemented essentially flawlessly by all three tiers — the clearest evidence yet that novelty itself isn't the missing difficulty ingredient. |
| [`gauss-legendre-quadrature-01`](tasks/gauss-legendre-quadrature-01/) | Mathematics / Numerical Analysis | Code Generation (SciCode-style) | Not yet run | First task outside finance and the first in the SciCode sub-problem-decomposition format: build Gauss-Legendre quadrature from scratch (Legendre polynomial evaluation → Newton-method root-finding → quadrature weights) and apply it to the complete elliptic integral of the first kind, cross-validated against an independent arithmetic-geometric-mean reference. Graded by `pytest`, not an LLM judge. |

### `fpa-variance-analysis-01` calibration: honest negative result

Real 3-tier calibration (Haiku/Sonnet/Opus, three independent rounds,
graded with the task's actual scoring pipeline) never got a single
model at or below the 0.5 difficulty ceiling — not in the original
version, not after fixing a leaked-procedure prompt, not after removing
the data files' narrated allocation basis. Scores ranged 0.93-1.00
across all three rounds. Full writeup, including *why* two rounds of
difficulty-strengthening didn't move the needle and what a real fix
would require, is in
[the task's README](tasks/fpa-variance-analysis-01/README.md#calibration-verdict-final).
Kept in this repo as a worked example of the calibration process itself
— including what it looks like when a task genuinely doesn't clear the
bar — not as a claim that the task is calibration-ready.

### `debt-covenant-runoff-01` calibration: honest negative result, second mechanism

Built specifically to test a *different* difficulty mechanism than the
FP&A task's hidden-ratio mismatch — long-horizon state tracking with
several interacting timing rules, where a plausible one-rule
misreading (applying a covenant rate step-up a month early) produces a
confidently-wrong answer. Real single-round calibration (Haiku/Sonnet/
Opus, blind, actual scoring pipeline) again found no model at or below
0.5: Haiku 0.955, Sonnet 0.977, Opus 1.000. All three got every
`answer.json` field numerically exact and correctly reasoned through
the rate-step-up timing trap via code execution. Full writeup,
including the per-model rubric breakdown and what actually
differentiated the (small) score gaps between tiers, is in
[the task's README](tasks/debt-covenant-runoff-01/README.md#calibration-verdict).
Together with `fpa-variance-analysis-01`, this is now the second
independent difficulty mechanism tested for real and found not to be
enough — see that task's recommendation for what a harder trap would
need to look like.

### `loan-daycount-accrual-01` calibration: honest negative result, third mechanism

Reuses `debt-covenant-runoff-01`'s exact loan mechanics and cash-flow
series, changing only the interest day-count basis from a flat monthly
fraction to true Actual/360 over a real calendar spanning a leap-year
February — a plausible wrong shortcut (flat 1/12, numerically identical
to 30/360) that was verified during authoring to collapse to a different
task's already-correct golden answer, a clean and unambiguous
wrong-answer signature. Real single-round calibration again found no
model at or below 0.5: Haiku 0.831, Sonnet 0.944, Opus 1.000. All three
correctly applied Actual/360 and got the leap year right — none
defaulted to the wrong shortcut. This is the widest tier-to-tier spread
of any task in this repo so far (driven mostly by whether each model's
*report* demonstrated its reasoning, not by numeric correctness — all
three got `answer.json` exact), but still nowhere near the ceiling. Full
writeup, including the per-model rubric breakdown and a real
environment-contamination finding Opus caught and self-corrected, is in
[the task's README](tasks/loan-daycount-accrual-01/README.md#calibration-verdict).
Three independent difficulty mechanisms (hidden cross-file
inconsistency, multi-rule sequencing, named-but-substitutable wrong
convention) have now each been tested for real and each left every
tier comfortably above 0.5 — see that task's recommendation for what
kind of mechanism would need to be different next.

### `tranche-waterfall-runoff-01` calibration: honest negative result, and the compound-complexity hypothesis is refuted

Built to test a specifically different hypothesis than the three
predecessor tasks: instead of one loan with one or two interacting rules,
this uses three tranches with a strict payment waterfall, a PIK-vs-cash
toggle, and a covenant trigger producing two effects of deliberately
different duration — the bet being that compounding *state* across
multiple entities, not just rules on one loan, would create enough
surface area for a bug to cascade and depress a weaker tier's score. Real
single-round calibration refutes this directly: **every score is higher
than the simpler day-count task's** — Haiku 0.959, Sonnet 0.979, Opus
1.000. All three tiers got `answer.json` numerically exact across all 16
fields with zero exceptions, correctly handling the asymmetric covenant
durations and the two-tranche-dependent conversion gate on a single blind
attempt via code execution. Opus even independently identified a subtle
edge case (a sweep-excess-doesn't-cascade rule) the task's own author had
to verify by hand. Full writeup, including the per-model rubric breakdown
and the updated recommendation after four consecutive negative results,
is in
[the task's README](tasks/tranche-waterfall-runoff-01/README.md#calibration-verdict).

**Four independent difficulty mechanisms — hidden cross-file
inconsistency, multi-rule sequencing, a named-but-substitutable wrong
convention, and now compound multi-entity state — have each been tested
for real and each left every tier comfortably above 0.5.** All four share
one shape: a fully-specified, deterministic rule set a model with
code-execution tools can translate into a correct simulation once it
reads the rules carefully, regardless of how large or complex that rule
set is. Based on this evidence, further tasks in this family (bigger,
more rules, more entities) are unlikely to clear the ceiling; the
`tranche-waterfall-runoff-01` README's recommendation section lays out
what a structurally different class of difficulty — genuine ambiguity,
an undocumented domain-knowledge gap, or messy unstructured source data —
would need to look like instead.

### `macrs-midquarter-depreciation-01` calibration: honest negative result, and the flattest one yet

Tested the other class of difficulty flagged above: instead of a
fully-specified rule set, this task withholds the governing rule
entirely. Nowhere in the task materials does it say that IRS rules
require the MACRS mid-quarter depreciation convention (instead of the
default half-year convention) whenever more than 40% of a year's
depreciable basis is placed in service in Q4 — the agent has to know or
derive this real, IRS-codified rule (IRC §168(d)(3), Publication 946) the
way a real corporate tax preparer would, with **no internet access**
during calibration to make sure the test measured actual knowledge, not
lookup ability. Real single-round calibration produced the flattest
result of any task in this repo: **Haiku 1.0, Sonnet 1.0, Opus 1.0** —
zero differentiation. All three correctly identified the >40% Q4 trigger
with no hint, and two of the three (Sonnet, Opus) had the exact published
percentage tables memorized well enough to reproduce all six years of
two different quarter-specific tables from memory, unprompted. Full
writeup, including a genuine (if ungraded) nuance where Haiku's
unrequested extended calculations revealed shallower table recall than
the larger models despite an identical score, is in
[the task's README](tasks/macrs-midquarter-depreciation-01/README.md#calibration-verdict).

**Five independent difficulty mechanisms across two fundamentally
different eligibility philosophies — fully-specified rule sets of
increasing size and complexity, and now a withheld, real,
professionally-standard domain fact — have each been tested for real and
none has produced a single sub-0.5 score.** The remaining, untested axes
are a domain fact that is real but *not* heavily represented in public
training material (hard to source reliably without introducing its own
fairness or accuracy risk), and tasks requiring a genuine judgment call
under real ambiguity, where reasonable experts could disagree rather than
there being one mechanically-or-factually-determined correct answer —
see `macrs-midquarter-depreciation-01`'s recommendation section for the
full reasoning.

### `rate-conflict-interest-analysis-01` calibration: honest negative result, a third eligibility philosophy, still flat

Tested a structurally different failure mode than every prior task:
instead of computing a confident answer correctly (rule-following or
fact-recall), this task tests whether the agent notices, with **no
hint anywhere in the materials**, that two equally authoritative source
documents — an executed Credit Agreement fixing a loan's interest margin
at 350 bps with an explicit amendment-only change clause, and a later
lender notice stating 375 bps with no explanation — genuinely and
irreconcilably conflict, and flags this rather than silently picking a
side and reporting one confident number. Real single-round calibration
produced a second flat, perfect result: **Haiku 1.0, Sonnet 1.0, Opus
1.0.** All three tiers spontaneously noticed the conflict, computed both
scenarios exactly, correctly reasoned about which document could validly
govern under the contract's own amendment clause, and recommended
escalation rather than resolving it themselves — Opus went further,
identifying a real methodological risk (day-count convention) the task
itself hadn't required. Full writeup is in
[the task's README](tasks/rate-conflict-interest-analysis-01/README.md#calibration-verdict).

**Seven independent difficulty mechanisms across three fundamentally
different eligibility philosophies — fully-specified rule sets, a
withheld domain fact, and now genuine unresolvable source conflict — have
each been tested for real, multiple times, against the same three tiers,
and none has produced a single sub-0.5 score. The last two attempts
landed at a flat, perfect 1.0 across every tier tested.** At this point
the evidence supports a plain conclusion: for financial/quantitative
analysis tasks with a well-defined deliverable, current frontier and
mid-tier models do not fail in ways this project's mechanisms can
produce — not through rule complexity, not through withheld facts, and
not through requiring epistemic caution under contradiction. The two
genuinely untested categories are unstructured/messy source extraction
(where the difficulty is in what a document actually says, not in
reasoning about known facts) and tasks whose grading itself does not rest
on one correct answer (judgment calls scored on reasoning quality rather
than a match to a golden answer) — both would require a different kind of
task-authoring investment than anything tried in this repo, and neither
should be assumed to work without testing it for real, given this
series's seven-for-seven track record. See
`rate-conflict-interest-analysis-01`'s recommendation section for the
full reasoning.

### `kb-earned-contract-liability-01` calibration: the eighth failure, and the cleanest test of novelty itself

Every task up to this point reused this repo's original eligibility
principle — every rule needed to solve the task is stated somewhere in
the materials, however deeply hidden or complexly interacting. This task
tests the one remaining variant of that principle worth trying: what if
the *method itself*, not just a fact about it, genuinely could not have
been seen during training? Built from a real, single, recently published
paper — Kerper and Bowron (2026), *Risks* 14(3):44, CC BY 4.0, published
24 February 2026, after this session's own model knowledge cutoff — per
SciCode-style paper-sourcing guidelines for Code Generation tasks. The
task implements two of the paper's genuinely novel ideas (a service
contract has zero loss exposure while the underlying manufacturer's
warranty remains in effect, and the warranty's and the contract's own
"whichever comes first" month-vs-mileage termination tests are
independent and can resolve in opposite directions) from a plain-language
excerpt, with no equation the agent could look up.

Real single-round calibration: **Haiku 0.947, Sonnet 1.000, Opus 1.000.**
All three got every field of `answer.json` numerically exact. Sonnet and
Opus both volunteered, unprompted, a direct numerical contrast against
what a naive pro-rata approach would show — confirming they'd correctly
applied the novel method rather than defaulting to a familiar one — and
Opus added an independent closed-form recomputation and a sensitivity
analysis showing exactly how the answer would change under the most
likely misreading. Full writeup is in
[the task's README](tasks/kb-earned-contract-liability-01/README.md#calibration-verdict).

**Eight independent difficulty mechanisms across four eligibility
philosophies — fully-specified rule sets, a withheld old domain fact,
genuine unresolvable source conflict, and now a genuinely novel
post-cutoff method — have each been tested for real and none has
produced a sub-0.5 score.** The pattern that emerges across all eight is
not really about any one axis; it's that every task in this repo, however
different its surface mechanism, reduces to the same underlying shape:
*correctly translate a precisely-specified procedure into a computed
answer*. That translation step — reading exact prose, whether familiar or
brand new, and turning it into correct code — is evidently not where
these models struggle. Clearing the ceiling from here most likely
requires a task that doesn't reduce to that shape at all: not a harder
procedure to translate, but one that isn't fully specified anywhere
(genuine ambiguity requiring judgment, not resolvable by careful
reading), or one where the hard part is extracting a fact from
realistically messy source material rather than computing from a fact
already cleanly given. See `kb-earned-contract-liability-01`'s
recommendation section for the full reasoning.

### `gauss-legendre-quadrature-01`: a new domain and a new format

The eight tasks above are all finance, all graded via a rubric + LLM
judge. `gauss-legendre-quadrature-01` is the first departure on both
axes: mathematics/numerical analysis instead of finance, and the
SciCode-style sub-problem-decomposition format (a `problem.md`
specification, a golden `solution.py`, and a `pytest` unit test suite
that grades each sub-problem independently) instead of a rubric graded
by an LLM judge. Every claim in this domain — a polynomial recurrence, a
root location, a quadrature weight, a special-function value — has an
objectively checkable answer, so correctness is determined entirely by
unit tests; there is no rubric or judge model involved. See
[the task's README](tasks/gauss-legendre-quadrature-01/README.md) for
the full verification trail, including a real gap found during authoring
(an initial-guess bug that silently passed all 107 original tests
because Newton's method converges to the same answer regardless, given a
generous iteration budget) and how it was fixed with a tight-iteration-
budget test that actually catches it. Calibration against real models has
not yet been run for this task.

## Repo layout

Every task lives under `tasks/<task_name>/` and follows the same fixed
contract:

```
tasks/<task_name>/
├── instruction.md          the ONLY file the agent sees (the prompt)
├── README.md               reviewer-only: sources, eligibility, how the task was built
├── task.toml                metadata: domain, task type, labels
├── solution/
│   ├── solve.py             deterministic oracle -> writes answer.json (+ figures)
│   ├── solve.sh             canonical runner: `python solve.py <output_dir>`
│   ├── report.md            golden expert write-up (must score >90% on the rubric)
│   └── answer.json          reference answers, written by solve.py — never hand-edited
├── tests/
│   ├── rubric.json          15-25 weighted binary criteria for the LLM judge
│   ├── check_programmatic.py  numeric checks against answer.json, within stated tolerance
│   ├── judge_config.json    context + file paths given to the LLM judge
│   ├── llm_judge.py         judge harness (reference implementation, see the docstring)
│   └── test.sh              orchestrator -> writes reward.txt (0.30*programmatic + 0.70*judge)
└── environment/
    ├── data/                 agent-visible inputs (never leaks answers or construction notes)
    └── Dockerfile             the agent's runtime image
```

The agent only ever sees `instruction.md` and whatever is under
`environment/`. Everything else — the golden solution, the rubric, the
judge, the reviewer notes — is invisible to the agent and used only for
scoring.

## Running a task's grader locally

```bash
cd tasks/fpa-variance-analysis-01
bash solution/solve.sh solution        # regenerate the golden answer.json
bash tests/test.sh solution            # score the golden solution against itself -> reward.txt
cat reward.txt                         # should be 1.0
```

## License

MIT — see [LICENSE](LICENSE).
