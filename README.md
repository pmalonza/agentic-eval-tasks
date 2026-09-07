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
