"""Golden solution for gauss-legendre-quadrature-01.

Builds Gauss-Legendre quadrature from scratch (Legendre polynomial
evaluation -> Newton-method root-finding -> quadrature weights) and
applies it to the complete elliptic integral of the first kind, K(k).

Every function here was cross-validated during authoring against an
independent implementation (numpy.polynomial.legendre for Sub-problems
1-3; the arithmetic-geometric mean algorithm, a completely different
numerical method, for the main problem) -- see README.md for the
verification transcript. No library quadrature or elliptic-integral
routine is used anywhere below.
"""

from __future__ import annotations

import math
from typing import Callable


def legendre_p(n: int, x: float) -> tuple[float, float | None]:
    """Return (P_n(x), P_{n-1}(x)) via the three-term recurrence."""
    if n == 0:
        return 1.0, None
    p_prev, p_curr = 1.0, float(x)
    if n == 1:
        return p_curr, p_prev
    for k in range(1, n):
        p_next = ((2 * k + 1) * x * p_curr - k * p_prev) / (k + 1)
        p_prev, p_curr = p_curr, p_next
    return p_curr, p_prev


def _legendre_dp(n: int, x: float) -> float:
    """P_n'(x) via the identity P_n'(x) = n/(x^2-1) * (x P_n(x) - P_{n-1}(x))."""
    pn, pn1 = legendre_p(n, x)
    return n / (x**2 - 1) * (x * pn - pn1)


def legendre_roots(n: int, tol: float = 1e-14, max_iter: int = 100) -> list[float]:
    """All n roots of P_n(x), sorted increasing, via Newton's method."""
    roots = []
    for i in range(1, n + 1):
        x = math.cos(math.pi * (i - 0.25) / (n + 0.5))
        for _ in range(max_iter):
            pn, pn1 = legendre_p(n, x)
            dpn = n / (x**2 - 1) * (x * pn - pn1)
            dx = pn / dpn
            x -= dx
            if abs(dx) < tol:
                break
        roots.append(x)
    return sorted(roots)


def legendre_weights(n: int, roots: list[float]) -> list[float]:
    """Gauss-Legendre weight for each given root."""
    weights = []
    for x in roots:
        dpn = _legendre_dp(n, x)
        w = 2.0 / ((1 - x**2) * dpn**2)
        weights.append(w)
    return weights


def gauss_legendre_quadrature(f: Callable[[float], float], a: float, b: float, n: int) -> float:
    """Approximate the integral of f over [a, b] with n-point Gauss-Legendre quadrature."""
    roots = legendre_roots(n)
    weights = legendre_weights(n, roots)
    total = 0.0
    for x, w in zip(roots, weights):
        x_mapped = (b - a) / 2 * x + (a + b) / 2
        total += w * f(x_mapped)
    return (b - a) / 2 * total


def complete_elliptic_K(k: float, n: int) -> float:
    """Complete elliptic integral of the first kind, K(k), via n-point
    Gauss-Legendre quadrature over theta in [0, pi/2]."""

    def integrand(theta: float) -> float:
        return 1.0 / math.sqrt(1 - k**2 * math.sin(theta) ** 2)

    return gauss_legendre_quadrature(integrand, 0.0, math.pi / 2, n)
