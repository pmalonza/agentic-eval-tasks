# Gauss–Legendre Quadrature and the Complete Elliptic Integral of the First Kind

## Scientific background

Gauss–Legendre quadrature is a numerical integration rule that evaluates
a function at a specially chosen set of `n` points ("nodes") on `[-1, 1]`
and forms a weighted sum. Unlike Newton–Cotes rules (trapezoid, Simpson),
which use evenly spaced nodes, Gauss–Legendre quadrature chooses both the
node locations and the weights so that the rule integrates every
polynomial of degree up to `2n - 1` **exactly**. This makes it
dramatically more accurate than evenly-spaced rules for smooth
integrands, using far fewer function evaluations.

The nodes turn out to be the `n` roots of the degree-`n` Legendre
polynomial `P_n(x)`, and the weights have a closed form in terms of
`P_n'(x)` evaluated at each root. This problem builds a Gauss–Legendre
quadrature rule entirely from scratch — no library quadrature routines —
and applies it to a classical special function that has no elementary
closed form: the **complete elliptic integral of the first kind**,

```
K(k) = ∫_0^(π/2) dθ / sqrt(1 - k² sin²θ),      0 ≤ k < 1
```

which arises in the exact period of a pendulum, in electromagnetism, and
in the arc length of an ellipse.

## Main problem

Implement `complete_elliptic_K(k: float, n: int) -> float`, which
computes `K(k)` using an `n`-point Gauss–Legendre quadrature rule that
you construct yourself (via Sub-problems 1–3 below — do not use any
library's built-in Gauss–Legendre or elliptic-integral routine anywhere
in your solution). Your answer must agree with an independent
high-precision reference computation of `K(k)` (via the
arithmetic–geometric mean method, described in the test suite) to within
`1e-6` for `n ≥ 20` and `k ≤ 0.9`.

## Sub-problem 1 — Legendre polynomial evaluation

Implement `legendre_p(n: int, x: float) -> tuple[float, float]`,
returning `(P_n(x), P_{n-1}(x))` (both values, since the derivative
formula in Sub-problem 2 needs both).

Use the three-term recurrence relation (do not use a closed-form
Rodrigues formula or a symbolic/library polynomial evaluator):

```
P_0(x) = 1
P_1(x) = x
(k+1) P_{k+1}(x) = (2k+1) x P_k(x) - k P_{k-1}(x),   for k ≥ 1
```

For `n = 0`, return `(1.0, None)` (there is no `P_{-1}`).

## Sub-problem 2 — Root-finding via Newton's method

Implement `legendre_roots(n: int) -> list[float]`, returning all `n`
roots of `P_n(x)`, sorted in increasing order. All roots of `P_n` are
real, distinct, and lie strictly inside `(-1, 1)`.

Find each root with Newton's method,
`x_{k+1} = x_k - P_n(x_k) / P_n'(x_k)`, using your `legendre_p` function
from Sub-problem 1 (and the derivative identity from Sub-problem 3's
description below) at each step. For the initial guess for the `i`-th
root (`i = 1, ..., n`), use the standard asymptotic approximation

```
x_i^(0) = cos(π (i - 0.25) / (n + 0.5))
```

Iterate to convergence (successive updates differing by less than
`1e-14`, or a reasonable fixed iteration cap such as 100).

## Sub-problem 3 — Quadrature weights

Implement `legendre_weights(n: int, roots: list[float]) -> list[float]`,
returning the Gauss–Legendre quadrature weight for each given root, using
the formula

```
w_i = 2 / ((1 - x_i²) [P_n'(x_i)]²)
```

where the derivative is computed via the identity

```
P_n'(x) = n / (x² - 1) * (x P_n(x) - P_{n-1}(x))
```

(valid for `x ≠ ±1`, which is guaranteed here since all roots lie
strictly inside `(-1, 1)`), using your `legendre_p` function from
Sub-problem 1.

A correct implementation of this sub-problem has two testable
mathematical properties, independent of any reference table: the weights
are always positive, and they always sum to exactly `2` (the length of
the interval `[-1, 1]`, since `∫_{-1}^{1} 1 dx = 2 = Σ w_i`).

## Putting it together

Use Sub-problems 1–3 to build a general-purpose quadrature function
`gauss_legendre_quadrature(f: Callable[[float], float], a: float, b:
float, n: int) -> float` that approximates `∫_a^b f(x) dx` by mapping
the `n` nodes and weights on `[-1, 1]` onto `[a, b]` via the standard
affine change of variables, then apply it to the elliptic integral's
integrand over `[0, π/2]` to implement the main problem's
`complete_elliptic_K`.
