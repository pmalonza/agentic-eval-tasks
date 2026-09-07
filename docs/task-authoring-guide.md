# Task authoring guide

The contract every task in this repo follows. This is a general pattern for
building agent-evaluation tasks that produce real signal — not something
specific to any one benchmark or client. If you're writing a new task,
read this first.

## Why this shape

A benchmark task is only useful if its score means something. Two failure
modes make a task worthless:

- **Too easy** — every model solves it, so it can't distinguish anything.
- **Too vague / leaky / broken** — the model fails for reasons that have
  nothing to do with the capability you're trying to measure (missing
  files, contradictory instructions, an answer the model can guess without
  doing the work).

The target is a task that's **hard because of the underlying problem**,
not hard because it's confusing — solvable by a careful expert working
from the prompt and the provided files, but one that a meaningful fraction
of strong models still get wrong in a specific, diagnosable way.

## The directory contract

```
tasks/<task_name>/
├── instruction.md             the ONLY file the agent sees
├── README.md                  reviewer-only: sources, eligibility, construction
├── task.toml                  metadata: domain, task type, labels
├── solution/
│   ├── solve.py                deterministic oracle -> answer.json (+ figures)
│   ├── solve.sh                canonical runner
│   ├── report.md                golden expert write-up
│   └── answer.json              reference answers, written by solve.py
├── tests/
│   ├── rubric.json               weighted binary criteria for the judge
│   ├── check_programmatic.py    numeric checks against answer.json
│   ├── judge_config.json        context given to the judge
│   ├── llm_judge.py             judge harness
│   └── test.sh                  orchestrator -> reward.txt
└── environment/
    ├── data/                     agent-visible inputs
    └── Dockerfile                the agent's runtime image
```

The split matters: everything the agent can see lives in `instruction.md`
and `environment/`. Everything used to *grade* it — the golden solution,
the rubric, the judge — is invisible to the agent. An agent that could see
its own rubric would be graded on rubric-matching, not on doing the work.

## Writing the prompt (`instruction.md`)

- **Outcome-based, not a recipe.** State what to produce, not the steps
  to produce it. If the prompt tells the agent how to solve the problem,
  the task stops measuring whether the agent can figure that out.
- **Name every path, schema, unit, and deliverable explicitly.** Ambiguity
  about *what to submit* is not the kind of difficulty this is for —
  reserve difficulty for the underlying problem.
- **No leaked answers or root causes.** If the prompt reveals the trap,
  there's no trap.
- **No harness boilerplate** (don't tell the agent to `mkdir` its own
  output directory or how to write JSON — that's not part of what's being
  measured).

## Writing the golden solution (`solution/`)

`solve.py` is a deterministic oracle: fixed seeds, no wall-clock
dependence, no network calls, reproducible byte-for-byte on rerun. Every
numeric value used anywhere in grading is baked from actually running this
script — never hand-typed into a checker or a rubric. If a number in
`answer.json` can't be traced to a `solve.py` computation, it doesn't
belong in the task.

`report.md` is the expert write-up: the reasoning that gets to the answer
(not a restatement of the prompt), the expected values and what they mean,
what was validated and how, and the assumptions/limitations. It must score
above 90% on the task's own rubric — if the golden answer doesn't clear
that bar, either the report or the rubric is wrong, and you fix it before
the task ships.

## Writing the rubric (`tests/rubric.json`)

- 15–25 weighted, binary (pass/fail) criteria — not a 1–10 scale per item.
- Integer weights, roughly 1–5, concentrated on the criteria that actually
  distinguish a correct answer from a plausible-looking wrong one.
- At least one **negative** criterion — something a wrong answer commonly
  does that a correct one must not (e.g. "does not attribute the
  root cause to the wrong entity").
- Span at least three distinct categories (e.g. correctness, reasoning
  process, communication quality) so the score isn't dominated by one
  dimension.
- Write it *after* the golden solution, against the golden solution — not
  the other way around.
- Don't duplicate what a programmatic check already covers. The rubric is
  for judgment calls a script can't make (is the reasoning sound, is the
  causal story right, is the write-up something you'd actually hand to a
  decision-maker) — not for re-checking arithmetic a script already
  verifies exactly.

## Scoring

```
reward = 0.30 x programmatic_score + 0.70 x rubric_score
```

`check_programmatic.py` verifies numbers against the golden `answer.json`
within a stated tolerance (this repo uses 5% unless a task states
otherwise) and should fail gracefully — a missing or malformed agent
output scores 0 on that check, it never crashes the harness. `test.sh`
must always write a `reward.txt`, even when a grading step errors out; a
crash is a score of 0, not an exception that takes down the whole
evaluation run.

## Task-type archetypes

Different tasks call for different shapes of "what counts as done." A
few recurring archetypes, borrowed loosely from the general literature on
agent-benchmark design (long-horizon tool use, precision-under-ambiguity,
repo-scale bug hunts, trap-laden domain reasoning, underspecified
requirements, irreversible tool chains):

| Archetype | Core test | Typical trap |
|---|---|---|
| Result Interpretation | Explain what existing results mean | A caption-level read that misses a domain-specific confound |
| Error Diagnosis | Find and fix a real bug, then verify | Patches the symptom, not the root cause |
| End-to-End Analysis | Raw data -> validated conclusion | A plausible pipeline that skips a required validation step |
| Hypothesis Validation | Design and run a bounded test of a stated claim | Asserts the conclusion without executed evidence |
| Tool Orchestration | Choose and sequence the right tools/APIs | Uses one tool correctly but never checks the combined result |

`fpa-variance-analysis-01` in this repo is a Result Interpretation task:
the agent is handed precomputed financial artifacts and has to correctly
diagnose *why* they say what they say, not generate them from scratch.

## Pre-submit checklist

- [ ] `instruction.md` is self-contained: no boilerplate, no leaked
      answer, every deliverable path/schema named
- [ ] `solve.py` is deterministic; running it reproduces `answer.json`
      exactly
- [ ] `solution/report.md` scores above 90% on `tests/rubric.json`
- [ ] `tests/rubric.json` has 15–25 items, integer weights, ≥3
      categories, ≥1 negative criterion, written after the golden solution
- [ ] `tests/check_programmatic.py` fails gracefully on missing/malformed
      agent output
- [ ] `tests/test.sh` always writes `reward.txt`, even on a grading crash
- [ ] Nothing under `environment/` leaks the answer, the root cause, or
      construction notes
