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
