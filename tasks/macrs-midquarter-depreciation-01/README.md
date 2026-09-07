# macrs-midquarter-depreciation-01 — reviewer notes

Not shown to the agent. Sourcing, eligibility, construction, and what was
and wasn't live-verified during authoring.

## Source

**Type:** expert-designed, but unlike every other task in this repo, the
governing rule itself is a real, external, codified body of law — the
MACRS mid-quarter convention under IRC §168(d)(3) and IRS Publication 946,
Appendix A. The company, asset descriptions, and dollar figures are
synthetic; the depreciation rule and percentage tables are not — they are
the actual IRS-published rates for 5-year GDS property.

## Why this task exists, and how it's different from the other four

The four prior tasks in this repo (`fpa-variance-analysis-01`,
`debt-covenant-runoff-01`, `loan-daycount-accrual-01`,
`tranche-waterfall-runoff-01`) were all built on the same eligibility
principle: every rule needed to solve the task is stated in full,
somewhere in the provided materials, and the difficulty comes from reading
and implementing those rules correctly. All four were calibrated for real
against three model tiers and all four failed to clear the 0.5 difficulty
ceiling — the working theory that emerged is that a fully-specified,
deterministic rule set, however large or complex, is within reach of a
model with code-execution tools, because it can just translate the stated
rules into code.

This task tests the opposite eligibility principle on purpose: the
governing rule — that IRS rules require the mid-quarter convention instead
of the default half-year convention whenever more than 40% of a year's
aggregate depreciable basis is placed in service in the fourth quarter,
and that this changes which percentage table every asset placed in
service that year uses for its *entire* recovery period, not just its
first year — is **not stated anywhere** in `environment/data/`. The agent
must know this rule, or correctly derive it, the way a real corporate tax
preparer is expected to. This is real, standard, professional tax
knowledge (a well-known "gotcha" in corporate tax preparation, precisely
because the trigger is easy to overlook when reviewing assets
one-at-a-time rather than in aggregate) — not obscure trivia and not
something invented for this task.

## Construction mechanism

1. Chose 5-year MACRS property (avoiding any need for the agent to also
   determine which recovery-period class an asset belongs to — that's a
   separate skill from the one this task targets) and designed a
   five-asset acquisition schedule where Q4 acquisitions ($130,000 of
   $250,000 total, 52%) clearly exceed the 40% threshold, without being a
   boundary case close enough to 40% to raise a legitimate dispute about
   whether the test is met.
2. Verified the actual IRS percentage tables (Publication 946, Appendix A,
   Tables A-1 through A-5, for 5-year property) via live web search and
   fetch during authoring — see "Verification performed" below for the
   exact sources and cross-checks used, since the entire validity of this
   task's golden answer depends on these external, real-world numbers
   being transcribed correctly (unlike the other four tasks, where the
   golden answer is fully self-contained and derivable from
   `environment/data/` alone).
3. `solution/solve.py` hardcodes the verified tables and applies them
   according to the actual IRS convention-selection and per-asset-table
   rules; nothing in `solution/answer.json` or `solution/report.md` was
   hand-typed.
4. Constructed the two most plausible domain-knowledge failure modes
   (ignoring the mid-quarter trigger entirely; applying it only to Year 1
   and reverting to half-year for Year 2+) and confirmed both produce
   large, well-separated divergence from golden — see "Verification
   performed" below.

## Eligibility (departs from this repo's usual standard — see task.toml)

This is the one task in this repo where "no external knowledge required"
does **not** hold, and that is deliberate. Eligibility instead rests on:
the rule being real, current, and standard professional knowledge (not
an invented or obscure convention); the numbers used in the golden
solution being independently verified against multiple sources rather
than taken from memory alone; and the trigger being unambiguous (52% is
comfortably clear of the 40% line, so there's no genuine dispute about
which convention applies once the rule is known).

## Verification performed during authoring

- **External fact verification (the load-bearing risk for this task):**
  Used live web search and page fetches to independently verify the MACRS
  percentage tables before hardcoding them into `solution/solve.py`:
  - Confirmed the half-year Table A-1 figures (20.00/32.00/19.20/11.52/
    11.52/5.76%) against two independent sources.
  - Confirmed the mid-quarter Q1 Table A-2 figures (35.00/26.00/15.60/
    11.01/11.01/1.38%) against two independent sources.
  - Obtained the Q2, Q3, and Q4 tables (A-3, A-4, A-5) from one detailed
    source and validated them with an internal consistency check: each
    table's six percentages must sum to exactly 100.00% (since MACRS
    fully depreciates the asset over its stub recovery period) — all four
    mid-quarter tables and the half-year table pass this check exactly,
    which is strong internal evidence the transcription is correct even
    where a second independent source wasn't found for every single
    table.
  - Direct IRS PDF fetches (irs.gov/pub/irs-pdf/p946.pdf) and two other
    candidate sources returned unparsable or incomplete content and were
    not usable as primary confirmation; this is disclosed rather than
    hidden, since it's a real limitation of the verification performed.
- **Programmatic correctness:** `solution/solve.py` computes every
  `answer.json` field from `asset_register.csv` and the verified tables;
  rerunning it reproduces `answer.json` byte-for-byte.
- **Bug construction and detection, stress-tested before finalizing the
  checker:** built both plausible domain-knowledge failure modes —
  (a) applying half-year convention throughout, ignoring the 40% test
  entirely, and (b) applying mid-quarter timing correctly for Year 1 but
  reverting to half-year percentages for Year 2. Against
  `check_programmatic.py` (flat $10 tolerance on dollar fields, 0.5
  percentage-point tolerance on the Q4 share), golden scores 1.0, bug (a)
  scores **0.133** (the mid-quarter/half-year gap is large enough that
  almost every field fails), and bug (b) scores **0.6** (Year 1 and the
  per-asset Year 1 figures are unaffected, but every Year 2 figure fails).
  Also re-verified: missing agent directory and malformed JSON both score
  0.0 without crashing.
- **Orchestration (`tests/test.sh`):** run end-to-end against the golden
  solution. `check_programmatic.py` correctly scored 1.0. The LLM judge
  step was run with no API key configured (deliberately, to avoid
  spending a shared credential not provisioned for this purpose) and
  correctly degraded to 0.0 with a clear note; combined reward came out
  to 0.30, matching `0.30*1.0 + 0.70*0.0` exactly.
- **Judge scoring logic (`tests/llm_judge.py`):** verified with the model
  call mocked (no live API spend): an all-PASS mock yields exactly 1.0; a
  mock that fails exactly one criterion (the highest-weight one,
  `mid-quarter-convention-correctly-identified`, weight 5 of 53 total)
  yields the exact expected reduced score (0.9057); a malformed
  (non-PASS/FAIL) mock response is caught as a graceful error rather than
  crashing.
- **Not live-verified:** an actual LLM call grading the golden report
  end-to-end, and a live `docker build` of `environment/Dockerfile` — same
  caveats as the four predecessor tasks in this repo, for the same
  reasons.

## Calibration status

Not yet run as of this writing. This is the fifth task in this repo and
the first to deliberately test a domain-knowledge gap rather than a
fully-specified rule set; its actual difficulty against real models is
unverified until the same three-tier (Haiku/Sonnet/Opus) blind evaluation
process is run and graded against `tests/`. Worth noting honestly going
in: the MACRS mid-quarter convention is a commonly-taught, heavily
documented topic (it appears in virtually every intermediate accounting
and CPA-exam-prep resource), so there is a real chance it fails to clear
the ceiling for the same underlying reason the previous four tasks did —
frontier models tend to already know well-documented professional
material cold. That is precisely the empirical question this task is
built to answer, not something to be assumed either way in advance.
