# gauss-legendre-quadrature-01 — reviewer notes

Not shown to the model being evaluated. Sourcing, construction, and what
was verified during authoring.

## Source

**Type:** expert-designed (classical numerical analysis, not sourced
from a single paper). Gauss–Legendre quadrature and the AGM algorithm
for the complete elliptic integral are both standard, well-established
methods (going back to Gauss and Lagrange respectively); the specific
decomposition into sub-problems and the choice of cross-validation
methods are original to this task.

## Format note

This task uses a different internal structure than the finance tasks
elsewhere in this repo (`instruction.md` / `tests/rubric.json` /
`tests/check_programmatic.py`). It follows the SciCode-style
sub-problem-decomposition format instead: a `problem.md` specification
(main problem + progressively-building sub-problems, each a function
signature with a natural-language description), a golden `solution.py`,
and a `test_solution.py` unit test suite that grades each sub-problem
independently via `pytest`. There is no LLM-judge rubric — correctness
is fully determined by the unit tests, since every claim in this domain
(a polynomial recurrence, a root, a quadrature weight, a special-function
value) has an objectively checkable answer.

## Why this decomposition

- **Sub-problem 1 (Legendre polynomial evaluation)** is the
  foundational primitive every later step depends on.
- **Sub-problem 2 (root-finding)** depends on Sub-problem 1 and
  introduces the one place a plausible small error (a wrong initial
  guess formula) can silently produce a working-but-technically-wrong
  implementation — see "A real gap found during authoring" below.
- **Sub-problem 3 (quadrature weights)** depends on both prior steps and
  has two properties checkable independently of any reference table
  (weights sum to exactly 2; weights are positive), which is deliberate:
  a solver should be able to partially self-verify Sub-problem 3 without
  needing to already trust Sub-problem 2's roots.
- **The main problem** composes all three into a general quadrature
  routine and applies it to a special function with no elementary closed
  form, so the final answer cannot be checked by simple substitution —
  it requires an independently-computed reference.

## Verification performed during authoring

- **Cross-validation against numpy (Sub-problems 1–3):**
  `legendre_p` was checked against `numpy.polynomial.legendre.legval`,
  and `legendre_roots`/`legendre_weights` were checked against
  `numpy.polynomial.legendre.leggauss` (numpy's own independent
  Gauss–Legendre implementation), for `n = 1, 2, 3, 4, 5, 8, 12` — all
  agree to at least `1e-9`, and the well-known tabulated `n=5` roots
  (`±0.906180`, `±0.538469`, `0`) were reproduced exactly, matching
  standard numerical-analysis references.
- **Cross-validation against an independent method (main problem):** the
  complete elliptic integral `K(k)` was independently computed via the
  arithmetic–geometric mean (AGM) algorithm — a numerical method
  unrelated to quadrature of any kind — for `k = 0.1, ..., 0.99`. The
  Gauss–Legendre-based `complete_elliptic_K` agrees with the AGM
  reference to machine precision (`~1e-15`) once `n ≥ 20` for
  `k ≤ 0.9`, and the expected slower convergence as `k → 1` (where the
  integrand develops a near-singularity) was observed and is exactly the
  behavior a correct implementation should show — this was treated as a
  positive confirmation of correctness, not a bug, and is reflected in
  the test suite's choice of `k ≤ 0.9` for the tight `1e-6` tolerance
  bound stated in `problem.md`.
- **Exactness property (Sub-problem 3):** independently of any reference
  table, an `n`-point Gauss–Legendre rule must integrate every
  polynomial of degree `≤ 2n-1` exactly. This was verified directly by
  integrating `x**k` for `k = 0` to `2n-1` over both `[-1, 1]` and a
  non-symmetric interval `[0, 2]` (exercising the affine
  change-of-variables) and comparing to the closed-form exact value —
  this is a mathematical certainty, not an approximation, so the test
  tolerance (`1e-9`) is a floating-point-precision bound, not a
  numerical-method bound.
- **Full test suite run against the golden solution:** 115 tests, all
  passing (`python -m pytest test_solution.py -v`).

## A real gap found during authoring, and how it was fixed

The first version of the test suite (107 tests) did not actually verify
that `legendre_roots` uses the specific initial-guess formula stated in
`problem.md`. A deliberately constructed buggy implementation that
replaced the correct initial guess `cos(π(i - 0.25)/(n + 0.5))` with the
incorrect `cos(πi/(n + 0.5))` (a plausible off-by-a-quarter error) passed
**all** existing tests. On inspection, this makes sense: Newton's method
has a wide basin of attraction for the simple, well-separated roots of a
Legendre polynomial, so with the function's default 100-iteration
budget, both the correct and incorrect initial guesses converge to the
identical final answer — the initial-guess formula only affects
*convergence speed*, and speed alone was not being tested.

This was fixed, not papered over: a new test
(`test_converges_within_tight_iteration_budget`) calls `legendre_roots`
with a deliberately tight `max_iter=3` budget and checks the result
against the numpy reference. Verified directly: at this budget, the
correct initial guess converges to within `~1e-16` of the reference for
`n = 8, 12, 20, 30`, while the incorrect initial guess is still off by
`1e-4` to `1e-5` at the same budget — a robust, multi-order-of-magnitude
gap across every tested `n`. This is now the only test in the suite that
can distinguish a correct initial-guess formula from an incorrect one,
and it does so reliably.

## Discriminative test-case verification

Four plausible bugs, one per pipeline component, were constructed and
run against the full test suite to confirm the suite actually
discriminates correct from incorrect implementations (not merely that it
passes on the golden solution):

| Constructed bug | Component | Tests failed / 115 |
|---|---|---:|
| Off-by-one recurrence coefficient (`2k` instead of `2k+1`) | Sub-problem 1 | 72 |
| Missing `(1 - x²)` factor in the weight formula | Sub-problem 3 | 25 |
| Wrong Newton initial guess (`i` instead of `i - 0.25`) | Sub-problem 2 | 4 |
| Missing Jacobian factor `(b-a)/2` in the quadrature sum | Main assembly | 7 |

Every constructed bug is caught by at least 4 tests, and the two
"upstream" bugs (Sub-problem 1's recurrence; Sub-problem 3's weight
formula) cascade into failures throughout the rest of the suite, exactly
as intended by the progressive-dependency structure — a wrong
foundational step should not be locally graded as "correct" just because
it happens to be self-consistent.

## Running the suite

```bash
cd tasks/gauss-legendre-quadrature-01
python -m pytest test_solution.py -v
```

Expect `115 passed` against `solution.py` as provided. A model being
evaluated on this task would be given `problem.md` and asked to produce
its own `solution.py`, implementing the four required functions;
`test_solution.py` (or an equivalent held-out variant) then grades it.

## QC across multiple LLM judges

Not performed as part of this authoring session — this repo's evaluation
infrastructure runs Claude-family models (Haiku/Sonnet/Opus) via
subagent calibration, not GPT/Gemini/Nemotron directly. If this task is
used in a pipeline with access to those judges, the unit tests above are
designed to be judge-agnostic (they check code correctness directly via
`pytest`, not via an LLM's subjective assessment of a report), so no
additional judge-specific tuning should be required — but that
independence has not itself been verified against those specific
external systems.
