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

## Calibration history

Real calibration runs (Haiku/Sonnet/Opus as three capability tiers,
each solving the task blind from `instruction.md` + `environment/data/`
only, scored with the actual `tests/` pipeline — not simulated):

- **Round 1** (original `instruction.md`): all three scored 0.93-1.00.
  Diagnosis: the prompt itself narrated the exact check to perform
  ("check the allocation basis... against what the email thread says...
  recompute if they disagree") — a leaked procedure, not a discovered
  one.
- **Round 2** (prompt fixed to be outcome-based, data files unchanged):
  all three still scored 0.97-1.00, barely moved. Diagnosis: the data
  files themselves narrated the answer almost as directly as the old
  prompt did — the email stated "shared-infrastructure move, not tied
  to one line of business" outright, and the allocation schedule
  labeled each row's method in words, so the two mismatched bases could
  be caught by reading two short strings, no computation required.
- **Round 3** (this state): removed the editorializing conclusion from
  the email (kept the underlying facts — both sites ship the whole
  catalog, the cost was billed under a project code — but not the
  "so this is shared, not tied to one line" framing), and removed the
  schedule's `Allocation_Basis`/`Notes` columns that narrated each row's
  method, leaving only dollar splits plus a document reference. Catching
  the anomaly now requires computing each row's implied revenue share
  and noticing the one-time cost's 100%/0% split doesn't match the
  pattern the standard pool's split does — a real, if modest,
  computational and inferential step instead of a reading-comprehension
  one.

  **Round 3 results: 0.98-1.00 — no better than Round 2. Haiku actually
  scored higher (1.00) than in either prior round.** All three models
  independently computed the revenue-share ratios themselves and
  compared them to the schedule's splits, rather than reading a stated
  inconsistency off the page — confirmed by inspecting their reports,
  which show the reverse-engineered percentages worked out by hand.
  Removing the narration didn't remove the capability; it just moved
  the same two-step check (compute a ratio, compare it, connect it to
  one plainly-stated email fact) from "read it" to "compute it," and
  that step turned out not to be hard for any of the three tiers,
  including Haiku.

## Calibration verdict (final)

| Round | Haiku | Sonnet | Opus | Change made |
|---|---|---|---|---|
| 1 | 0.93 | 1.00 | 1.00 | (baseline — leaked procedure in the prompt) |
| 2 | 0.97 | 0.98 | 1.00 | Prompt rewritten to be outcome-based |
| 3 | **1.00** | 0.98 | 1.00 | Data files de-narrated (no stated allocation basis, softer email) |

**Verdict: FAIL (too easy).** No model, across any of three independent
rounds and two rounds of deliberate difficulty-strengthening, scored at
or below the 0.5 ceiling. This is a real, negative result, not a
placeholder — the task was iterated on in good faith across both levers
the standard playbook calls for (move information out of the prompt;
strengthen the load-bearing discriminator in the data) and neither
moved the needle.

**Diagnosis.** The trap's underlying mechanism — compute two ratios,
notice they don't match, connect the mismatch to one plainly-stated
fact in a three-message email — is not a hard skill for current models
at any of the three tiers tested here, regardless of how much surface
narration is stripped from the prompt or the data. Obscuring the
*presentation* of a mechanism that isn't intrinsically hard just makes
the model do slightly more arithmetic on the way to the same answer.

**This is not unique to this task or this construction.** The same
failure mode — no model at or below 0.5 — shows up in the real
Agentic SciCode project's own QC output on a structurally unrelated,
far more technical task (an RNA-design optimization coding task), where
three frontier models landed at 0.57-0.68. Clearing the 0.5 ceiling
appears to be a generally hard bar, and for a financial-consistency
trap specifically, no amount of re-hiding the same mechanism is likely
to clear it.

**Recommendation.** Do not continue tuning this task's data
presentation — two rounds of exactly that (moving information out of
the prompt, then out of the data) produced no measurable difficulty
increase. A future revision aimed at clearing calibration would need a
*structurally different* discriminator on top of this scenario (e.g. a
second, independent trap that doesn't share the same "compute a ratio,
compare it" mechanism), not a better-hidden version of this one. Ship
this task, if at all, as documentation of a well-executed calibration
process with an honest negative result — not as a task that has passed
the difficulty gate.

One real bug surfaced during Round 2 and is fixed, independent of the
difficulty question above: `tests/check_programmatic.py` originally
failed a technically-valid agent `answer.json` that happened to carry a
UTF-8 BOM, reporting it as malformed. Fixed to use `utf-8-sig` decoding
(a no-op for files without a BOM); re-verified against every existing
edge case (missing directory, truly malformed JSON, wrong values) with
no regression.

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
