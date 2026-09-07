# tranche-waterfall-runoff-01 — reviewer notes

Not shown to the agent. Sourcing, eligibility, construction, and what
was and wasn't live-verified during authoring.

## Source

**Type:** expert-designed (no single external source paper/dataset). A
multi-tranche payment waterfall with a PIK-vs-cash toggle is a standard
structured-finance mechanism (leveraged loan facilities and CLOs routinely
have exactly this shape); the specific company, tranche sizes, and
cash-flow series here are synthetic but internally consistent — every
number in `environment/data/` and `solution/answer.json` derives from a
single simulation (`solution/solve.py`) run once over a fixed input
series.

## Why this task exists

Built after three consecutive real calibration failures on structurally
different single-loan mechanisms — a hidden cross-file ratio mismatch
(`fpa-variance-analysis-01`), multi-rule sequencing/timing
(`debt-covenant-runoff-01`), and a named-but-substitutable wrong day-count
convention (`loan-daycount-accrual-01`) — all three left every tested tier
(Haiku/Sonnet/Opus) comfortably above the 0.5 difficulty ceiling. All three
shared a common shape: a single, fully-specified rule that a model with
code-execution tools could implement correctly once it read the rule
carefully.

This task tests a different kind of difficulty on purpose: instead of one
loan with one or two interacting rules, it uses **three tranches with
interacting state**, where a single implementation bug plausibly cascades
across most of the schedule rather than costing a few isolated dollar
fields. Two design choices specifically target this:

1. **A waterfall with a PIK-vs-cash toggle and a conversion gate that
   depends on two different tranches' state simultaneously** (Tranche C
   only converts once *both* A and B are zero, not A alone) — this is a
   materially harder tracking problem than any single-tranche rule tested
   so far, because getting it wrong doesn't just shift one number, it
   changes which tranche receives interest, PIK accrual, and sweep
   proceeds for a stretch of months.
2. **A single covenant trigger that produces two effects of deliberately
   different duration** — Tranche A's rate step-up is permanent, but
   Tranche B's forced PIK lasts exactly one month. This is the closest
   analogue to the previous tasks' single-rule timing traps, but stacked
   on top of the waterfall complexity rather than tested in isolation.

## Construction mechanism

1. Prototyped the simulation logic directly (not the final numbers) to
   choose tranche sizes, rates, and a cash-flow series that would
   naturally exercise every interesting transition within 24 months:
   Tranche A payoff, Tranche B payoff, Tranche C's conversion, and Tranche
   C's own payoff — rather than picking a story upfront and forcing the
   numbers to match it.
2. Iterated the `monthly_cash_flow.csv` series until a single prototype
   run produced all four transitions cleanly (Tranche A payoff month 12,
   Tranche B payoff month 15, Tranche C conversion month 16, Tranche C
   payoff month 18) — confirmed with real script output, not by
   construction from the answer backward.
3. `solution/solve.py` deterministically simulates all 24 months from the
   final `loan_terms.md` and `monthly_cash_flow.csv`; nothing in
   `solution/answer.json` or `solution/report.md` was hand-typed.
4. Constructed the two most plausible rule misreadings (forced-PIK treated
   as permanent instead of one-month; Tranche C conversion gated on
   Tranche A alone instead of both A and B) during authoring and confirmed
   both produce large, well-separated divergence from golden — see
   "Verification performed" below.

## Eligibility

Not paper-sourced, so the paper-recency requirement doesn't apply.
Eligibility rests on internal validity and fairness: every rule (the
waterfall priority, the PIK toggle, the conversion gate, the asymmetric
covenant durations, the sweep's single-recipient-per-month behavior) is
stated in full and unambiguously in `loan_terms.md` — nothing is withheld
or requires outside domain knowledge. The difficulty is in correctly
implementing several interacting, precisely-specified rules across three
tranches simultaneously, not in guessing an unstated rule.

## Verification performed during authoring

- **Programmatic correctness:** `solution/solve.py` computes every
  `answer.json` field from `loan_terms.md`'s fixed constants and
  `monthly_cash_flow.csv`; rerunning it reproduces `answer.json`
  byte-for-byte.
- **Bug construction and detection, stress-tested before finalizing the
  checker:** built both plausible rule misreadings —
  (a) treating the Mezzanine forced-PIK as permanent rather than
  one-month, and (b) gating the Subordinated tranche's conversion on
  Tranche A alone instead of both A and B — and confirmed each produces
  substantial, well-separated divergence from golden: Bug (a) shifts two
  integer month fields (`tranche_b_payoff_month`, `tranche_c_conversion_month`)
  and diverges on 7 of 10 dollar fields, the smallest affected delta being
  $215.60; Bug (b) shifts one integer month field and diverges on 5 of 10
  dollar fields, several by tens of thousands of dollars. Against the
  `check_programmatic.py` checker (flat $25 tolerance, reused from the two
  predecessor loan tasks and re-justified here against these larger
  effect sizes), golden scores 1.0, Bug (a) scores 0.4375, and Bug (b)
  scores 0.5 — both bugs caught substantially, not marginally. Also
  re-verified: missing agent directory and malformed JSON both score 0.0
  without crashing.
- **A third, smaller effect surfaced naturally (not by design) and was
  documented rather than engineered away:** in Month 15, the raw computed
  sweep ($231,652.52) slightly exceeds Tranche B's remaining balance
  ($231,199.53); per the stated "no same-month cascade" rule, the $452.99
  excess is not redirected to Tranche C that month. This is a real,
  if minor, additional discriminator between a solver that implements the
  cap-and-hold rule literally and one that assumes the more common
  real-world convention of cascading leftover sweep proceeds to the next
  tranche in the same month.
- **Orchestration (`tests/test.sh`):** run end-to-end against the golden
  solution. `check_programmatic.py` correctly scored 1.0. The LLM judge
  step was run with no API key configured (deliberately, to avoid
  spending a shared credential not provisioned for this purpose) and
  correctly degraded to 0.0 with a clear note; combined reward came out
  to 0.30, matching `0.30*1.0 + 0.70*0.0` exactly.
- **Judge scoring logic (`tests/llm_judge.py`):** verified with the model
  call mocked (no live API spend): an all-PASS mock yields exactly 1.0;
  a mock that fails exactly one criterion (the highest-weight one,
  `forced-pik-duration-correct`, weight 5 of 68 total) yields the exact
  expected reduced score (0.9559); a malformed (non-PASS/FAIL) mock
  response is caught as a graceful error rather than crashing.
- **Not live-verified:** an actual LLM call grading the golden report
  end-to-end, and a live `docker build` of `environment/Dockerfile` — same
  caveats as the three predecessor tasks in this repo, for the same
  reasons.

## Calibration results (real run, 2026-09-08)

Ran the same real calibration process used for the three predecessor
tasks: Haiku, Sonnet, and Opus each solved the task blind, from
`instruction.md` + the two `environment/data/` files only, using code
execution to run the actual three-tranche simulation. Opus hit the same
"subagents can't write a file literally named report.md" guardrail seen
in prior rounds, correctly reported it, and returned full file content as
text instead of working around it.

**All three tiers got `answer.json` numerically exact — all 16 fields,
across all three tiers, with zero exceptions.** None misapplied the
forced-PIK duration (all correctly showed Month 8 only, reverting to the
normal cash-sufficiency test from Month 9). None gated Tranche C's
conversion on Tranche A alone — all three correctly kept Tranche C on PIK
through Months 12-15 despite Tranche A already being retired, converting
only in Month 16 once Tranche B also cleared. Opus additionally
identified, unprompted, the exact same subtle edge case flagged in this
README's construction notes (Month 15's $452.99 sweep excess not
cascading to Tranche C) and correctly justified the "sweep capped at
recipient's balance, no cascade" reading directly from `loan_terms.md`.

Programmatic score was 1.0 for all three. Rubric scores, graded by hand
criterion-by-criterion against `tests/rubric.json` (in lieu of a live LLM
judge call, per this project's policy against spending shared credentials
on unauthorized side calls):

| Model | Programmatic | Rubric | Reward (0.30×prog + 0.70×rubric) |
|---|---|---|---|
| Haiku | 1.0 | 64/68 = 0.941 | **0.959** |
| Sonnet | 1.0 | 66/68 = 0.971 | **0.979** |
| Opus | 1.0 | 68/68 = 1.000 | **1.000** |

Notably, **every score here is higher than this task's simpler
predecessor** (`loan-daycount-accrual-01`, Haiku 0.831). Haiku's only
gaps: no assumptions section anywhere in its report (a recurring pattern
across every task in this repo so far), and a genuine internal
inconsistency it never caught — it states the Senior rate step-up costs
"approximately $1,667 per month" in one paragraph and "approximately
$833 per month" for the identical effect two paragraphs later, never
reconciled. Sonnet's only gap was the same "no explicit internal
validation" pattern seen in earlier tasks. Opus passed every criterion,
including a genuine reconciliation table (cash + PIK interest by tranche
summing to a stated facility total) inside the report itself.

## Calibration verdict

**FAIL (too easy) — and the added complexity made this task *easier* to
score well on, not harder.** This is the fourth independent difficulty
mechanism tested for real in this repo (after a hidden cross-file ratio
mismatch, multi-rule sequencing/timing, and a named-but-substitutable
wrong day-count convention), and the fourth to fail to clear the 0.5
ceiling. Unlike the previous three tasks, this one does not even show the
widest-tier-spread pattern that gave some hope of a future task clearing
the bar — Haiku's worst showing here (0.959) is actually its *best*
showing across all four tasks in this repo.

**Diagnosis.** The working hypothesis going into this task was that
compounding interacting state across three tranches — rather than one or
two rules on a single loan — would create enough surface area for a
single implementation bug to cascade and meaningfully depress a weaker
tier's score. That hypothesis is refuted by this result. All three tiers,
including Haiku, correctly tracked three simultaneous tranche balances,
a PIK-vs-cash toggle, an asymmetric-duration covenant, and a
two-tranche-dependent conversion gate — on a single blind attempt, via
code execution — with zero numeric errors. The amount of *state* a model
has to track does not appear to be the bottleneck at all, as long as
every rule governing that state is stated precisely and completely.

**Recommendation, updated after four negative results.** All four
mechanisms tested in this repo so far share the same underlying shape: a
fully-specified, deterministic rule set that a model with code-execution
tools can translate into a correct simulation once it reads the rules
carefully — whether that rule set is small (one loan, one covenant) or
large (three tranches, a waterfall, two covenant effects). Making the
rule set bigger does not change that shape, and this result suggests it
will not clear the ceiling no matter how large it gets. A task that
actually clears calibration for this class of model most likely needs a
*different* shape of difficulty entirely: real ambiguity where competent
experts could reasonably disagree (not a hidden-but-resolvable
inconsistency), a domain-knowledge gap that is not spelled out anywhere
in the provided materials and cannot be derived from them, or unstructured
/ messy real-world source data (e.g. actual filings or documents) where
extraction and judgment — not simulation — is the hard part. Continuing
to build bigger deterministic simulate-and-report tasks in this family is
not likely to be a good use of further effort based on this evidence.
