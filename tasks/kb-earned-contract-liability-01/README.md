# kb-earned-contract-liability-01 — reviewer notes

Not shown to the agent. Sourcing, eligibility, construction, and what was
and wasn't live-verified during authoring.

## Source

**Type:** published paper (single-paper Code Generation task).

- **Paper:** Kerper, J. and Bowron, L. (2026). "The Kerper–Bowron Method:
  A Foundational Change for Service Contract Claim Estimation and
  Accounting." *Risks*, 14(3), 44.
  [https://doi.org/10.3390/risks14030044](https://doi.org/10.3390/risks14030044).
- **Published:** 24 February 2026 (received 29 December 2025, accepted
  10 February 2026).
- **License:** CC BY 4.0. MDPI journals (including *Risks*) publish all
  articles under a blanket CC BY 4.0 license; this was cross-checked
  against MDPI's own stated open-access policy during authoring, not
  assumed.
- **Recency relative to model knowledge:** published after this
  session's own model knowledge cutoff (January 2026) and, per the
  session in which this task was authored, very likely after the
  calibration models' cutoffs too — this is a genuine, verifiable
  knowledge gap, not an assumed one, unlike `macrs-midquarter-
  depreciation-01`'s domain-fact gap (which turned out to be fully
  known despite being withheld from the task materials, because MACRS is
  old and exhaustively documented).

## Why this task exists

Seven prior tasks in this repo tested three eligibility philosophies —
fully-specified rule sets, a withheld-but-old domain fact, and genuine
source conflict — and none produced a single sub-0.5 score; the last two
landed at a flat, perfect 1.0 across every tier. The common thread: every
mechanism tried was, in principle, something a sufficiently
well-trained model could already know or infer from material that
existed before its training cutoff. This task tests a structurally
different, harder-to-refute kind of knowledge gap: a method published
*after* the tested models' training data existed, sourced the way
SciCode-style evaluation frameworks source their hardest Code Generation
and Hypothesis Validation tasks — from a single recent paper, with a
recency cutoff chosen specifically to guarantee the material could not
have been memorized.

## A scoping decision made during authoring, worth recording

The cited paper's full Kerper–Bowron Method has three components:
(1) a probabilistic exposure calculation using a lognormal distribution
fit to monthly mileage data (Section 6.1, Equations 9–13), (2) a
Generalized Linear Model with a Tweedie distribution fit to historical
claims to produce a modeled pure premium (Section 6.2), and (3) the
Earned Contract formula that converts a monthly loss-forecast stream into
earned/unearned percentages (Section 2, Equations 1–6).

During authoring, the paper's equations 9–13 (the lognormal exposure
formulas) rendered as blank placeholders when the page was fetched for
extraction — the surrounding prose was informative but not precise
enough to reconstruct the exact intended formula with full confidence
(MathML/LaTeX content did not survive the text conversion). Rather than
guess at a formula I could not fully verify and risk building a task
whose own golden answer misreads the paper, this task deliberately uses
only the two components that were extracted with full, unambiguous
confidence from clean prose: the Earned Contract formula (Section 2, used
essentially verbatim) and the qualitative exposure-exclusion concept from
Section 6.1 (a service contract has zero exposure while the
manufacturer's warranty remains in effect, tested independently by
"whichever comes first" on months vs. miles for each party) — adapted to
a flat, deterministic mileage assumption instead of the paper's own
probabilistic lognormal distribution.

This also sidesteps a second, independent risk: the paper's GLM
component requires fitting a statistical model to data, which does not
have a single "correct" fitted result (different reasonable
implementations — regularization, encoding choices, convergence
tolerance — would diverge) and would have undermined this project's
requirement for one gradable golden answer. The pure premium is instead
given directly to the agent as stated model output, consistent with how
every other task in this repo gives derived facts as inputs rather than
requiring the agent to re-derive them from raw data.

This is disclosed here in full rather than silently narrowed, consistent
with this project's practice of being honest about what was and wasn't
verified.

## Construction mechanism

1. Read the cited paper's Introduction, Sections 2, 5, and 6.1–6.3 in
   full via the live page (not from memory, and not assuming familiarity
   with a paper published after the authoring session's own knowledge
   cutoff).
2. Selected concrete VSC/warranty terms (36mo/30,000mi warranty vs.
   60mo/75,000mi VSC, flat 1,000 mi/month) specifically so the two
   "whichever comes first" tests resolve in **opposite** directions —
   the warranty is mileage-bound (month 30, not 36) while the VSC is
   time-bound (month 60, not a mileage-derived month) — making the
   independence of the two tests something a solver actually has to get
   right, not something that happens to be moot in this instance.
3. `solution/solve.py` deterministically implements the exposure rule and
   the Earned Contract formula from the excerpt; nothing in
   `solution/answer.json` or `solution/report.md` was hand-typed.
4. Constructed the two most plausible misreadings (ignoring the
   warranty-exclusion concept entirely; applying only the month-based
   limit to the warranty) during authoring and confirmed both produce
   large divergence — see "Verification performed" below.

## Eligibility

Departs from this repo's "everything derivable from the provided
materials" default in the same direction as `macrs-midquarter-
depreciation-01`, but for a different reason: the *method itself* (not a
general domain fact) is given to the agent in full via
`kb_method_excerpt.md` — nothing about how to apply it is withheld. The
knowledge gap this task tests is not "does the agent know this obscure
fact" but "can the agent correctly implement a method it has never seen
before, under time pressure, from a plain-language description," which
is a closer analogue to genuine paper-derived Code Generation than a
withheld-fact task is.

## Verification performed during authoring

- **Source verification:** confirmed the paper's title, authors, DOI,
  journal, publication date, and CC BY 4.0 license directly from the
  live MDPI page (not from a search-result summary alone) before using
  any of its content.
- **Programmatic correctness:** `solution/solve.py` computes every
  `answer.json` field from the stated contract terms and pricing model
  output; rerunning it reproduces `answer.json` byte-for-byte.
- **Bug construction and detection, stress-tested before finalizing the
  checker:** built both plausible misreadings — (a) ignoring the
  manufacturer's-warranty exclusion entirely (traditional age-from-sale
  reserving, the exact practice the cited paper explicitly contrasts
  itself against), and (b) applying only the warranty's month-based
  limit while ignoring that its mileage limit binds first. Against
  `check_programmatic.py` (flat $5 tolerance on dollar fields, 0.5
  percentage-point tolerance on percentage fields), golden scores 1.0,
  bug (a) scores **0.2**, and bug (b) scores **0.5** — both caught
  substantially. Also re-verified: missing agent directory and malformed
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
  `warranty-mileage-bound-correctly-identified`, weight 5 of 53 total)
  yields the exact expected reduced score (0.9057); a malformed
  (non-PASS/FAIL) mock response is caught as a graceful error rather than
  crashing.
- **Not live-verified:** an actual LLM call grading the golden report
  end-to-end, and a live `docker build` of `environment/Dockerfile` — same
  caveats as the seven predecessor tasks in this repo, for the same
  reasons.

## Calibration results (real run, 2026-09-16)

Ran the same real calibration process used for the seven predecessor
tasks: Haiku, Sonnet, and Opus each solved the task blind, from
`instruction.md` + the three `environment/data/` files only, explicitly
instructed to use no internet access (so the test measured whether the
method could be correctly implemented from the excerpt alone, not
whether it could be looked up). Opus hit the same "subagents can't write
a file literally named report.md" guardrail seen in prior rounds,
correctly reported it, and returned full file content as text instead of
working around it; it also discovered a stale `answer.json` left in its
sandbox from an unrelated earlier run and correctly overwrote it with its
own independently-derived figures rather than trusting the pre-existing
file.

**All three tiers got `answer.json` numerically exact.** All three
correctly determined that the manufacturer's warranty is mileage-bound
(effective expiration month 30, not its nominal 36-month term) while the
VSC itself is time-bound (month 60, not a mileage-derived month) —
the two "whichever comes first" tests resolving in opposite directions,
exactly as the task was designed to require. Sonnet and Opus both
volunteered, unprompted, a direct numerical contrast against what a
naive pro-rata approach would show at the same valuation dates,
confirming they hadn't defaulted to the more familiar convention. Opus
went further still: an independent closed-form recomputation of every
valuation checkpoint, a monotonicity/reasonableness check against the
pro-rata comparison, and a sensitivity analysis showing exactly how the
answer would have changed had the warranty been (incorrectly) read as
time-bound.

Programmatic score was 1.0 for all three. Rubric scores, graded by hand
criterion-by-criterion against `tests/rubric.json` (in lieu of a live LLM
judge call, per this project's policy against spending shared credentials
on unauthorized side calls):

| Model | Programmatic | Rubric | Reward (0.30×prog + 0.70×rubric) |
|---|---|---|---|
| Haiku | 1.0 | 49/53 = 0.925 | **0.947** |
| Sonnet | 1.0 | 53/53 = 1.000 | **1.000** |
| Opus | 1.0 | 53/53 = 1.000 | **1.000** |

Haiku's only gap: it correctly computed and clearly labeled both
"whichever comes first" resolutions, but never explicitly ran the
numerical pro-rata contrast that Sonnet and Opus both volunteered
unprompted — a communication-depth gap, not a correctness gap.

## Calibration verdict

**FAIL (too easy).** No model scored at or below the 0.5 ceiling. Even
genuinely novel content — a method published after the tested models'
training data existed, never seen before by any of them, correctly
excerpted with no ambiguity — was implemented essentially flawlessly by
all three tiers. This is the most direct test yet of whether raw novelty
(as opposed to withheld-but-old facts, or complexity, or conflicting
sources) could be the missing ingredient, and it wasn't.

**Diagnosis.** The result suggests that for these models, correctly
implementing a plainly-stated, self-contained method from a written
description is not meaningfully different in difficulty from applying a
method they already know — the skill being tested (reading precise
prose, translating it into correct code, handling the one deliberately
counter-intuitive consequence of the method) is evidently robust to
whether the method itself is familiar. This is consistent with, not
contradictory to, this repo's seven prior results: all eight tasks now
share a deeper commonality than their surface differences suggest —
each one asks the agent to correctly translate a *fully and precisely
specified* procedure into a computed answer, and that translation step
itself is not where these models struggle, regardless of what's on the
other side of it (a known rule, an unknown rule, a withheld fact, a
conflict to notice, or a novel formula).

**Recommendation, after eight consecutive negative results across four
eligibility philosophies.** Fully-specified rule sets, a withheld old
domain fact, genuine source conflict, and now a genuinely novel
post-cutoff method have each been tested for real, multiple times,
against the same three tiers, and none has produced a single sub-0.5
score. The evidence increasingly points to a conclusion less about any
one axis and more about the whole *shape* of this task family: any task
that reduces to "correctly translate a precisely-specified procedure
into a computed answer" is within reach of current frontier and mid-tier
models with code execution, no matter where the procedure comes from or
how novel it is. Clearing the ceiling likely requires abandoning that
shape entirely — not a harder version of "translate a precise procedure"
but a task where no amount of correct translation suffices, because the
procedure itself is not fully specified anywhere (genuinely ambiguous
prose requiring a judgment call, not resolvable by careful reading), or
because the hard part is extracting a fact from realistically messy,
partially-irrelevant source material rather than computing from a fact
already cleanly stated.
