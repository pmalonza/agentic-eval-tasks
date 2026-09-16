"""Unit tests for gauss-legendre-quadrature-01.

Each sub-problem is tested against a reference independent of the
solution's own logic:
  - Sub-problem 1 (legendre_p): numpy.polynomial.legendre.legval, a
    completely separate implementation.
  - Sub-problem 2 (legendre_roots): numpy.polynomial.legendre.leggauss's
    node locations, plus the residual check P_n(root) ~ 0, plus the
    symmetry property of Legendre roots.
  - Sub-problem 3 (legendre_weights): the two model-independent
    mathematical properties (weights sum to 2, weights are positive),
    plus numpy.polynomial.legendre.leggauss's weight values, plus the
    Gauss quadrature exactness property (a degree-n rule integrates
    every polynomial of degree <= 2n-1 exactly), tested directly by
    integrating x**k for k = 0 .. 2n-1 and comparing to the closed-form
    exact value.
  - Main problem (complete_elliptic_K): the arithmetic-geometric mean
    (AGM) algorithm, a numerical method with no relationship at all to
    Gauss-Legendre quadrature, computed independently in this file.

Run with: python -m pytest test_solution.py -v
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from numpy.polynomial import legendre as np_legendre

from solution import (
    complete_elliptic_K,
    gauss_legendre_quadrature,
    legendre_p,
    legendre_roots,
    legendre_weights,
)


# ---------------------------------------------------------------------------
# Sub-problem 1: legendre_p
# ---------------------------------------------------------------------------


class TestLegendreP:
    def test_p0_is_constant_one(self):
        for x in (-0.9, -0.3, 0.0, 0.4, 0.7, 0.99):
            pn, pn1 = legendre_p(0, x)
            assert pn == pytest.approx(1.0)
            assert pn1 is None

    def test_p1_is_identity(self):
        for x in (-0.9, -0.3, 0.0, 0.4, 0.7, 0.99):
            pn, pn1 = legendre_p(1, x)
            assert pn == pytest.approx(x)
            assert pn1 == pytest.approx(1.0)

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 8, 12])
    @pytest.mark.parametrize("x", [-0.9, -0.3, 0.0, 0.4, 0.7, 0.99])
    def test_matches_numpy_legendre(self, n, x):
        coeffs = [0] * n + [1]
        reference = np_legendre.legval(x, coeffs)
        pn, _ = legendre_p(n, x)
        assert pn == pytest.approx(reference, abs=1e-10)

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 8])
    def test_parity_symmetry(self, n):
        """P_n(-x) = (-1)^n P_n(x) is a defining property of Legendre polynomials."""
        for x in (0.2, 0.5, 0.8):
            pn_pos, _ = legendre_p(n, x)
            pn_neg, _ = legendre_p(n, -x)
            expected_sign = 1 if n % 2 == 0 else -1
            assert pn_neg == pytest.approx(expected_sign * pn_pos, abs=1e-10)

    def test_returns_previous_degree_too(self):
        """P_{n-1}(x) must also be correct, not just P_n(x) -- downstream
        derivative and weight formulas depend on both."""
        pn, pn1 = legendre_p(3, 0.6)
        coeffs_n1 = [0, 0, 1]
        reference_pn1 = np_legendre.legval(0.6, coeffs_n1)
        assert pn1 == pytest.approx(reference_pn1, abs=1e-10)


# ---------------------------------------------------------------------------
# Sub-problem 2: legendre_roots
# ---------------------------------------------------------------------------


class TestLegendreRoots:
    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 8, 12])
    def test_correct_count(self, n):
        assert len(legendre_roots(n)) == n

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 8, 12])
    def test_all_roots_in_open_interval(self, n):
        for r in legendre_roots(n):
            assert -1.0 < r < 1.0

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 8, 12])
    def test_sorted_increasing(self, n):
        roots = legendre_roots(n)
        assert roots == sorted(roots)

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 8, 12])
    def test_residual_near_zero(self, n):
        """Each returned root must actually be a root: P_n(root) ~ 0."""
        for r in legendre_roots(n):
            pn, _ = legendre_p(n, r)
            assert pn == pytest.approx(0.0, abs=1e-10)

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 8, 12])
    def test_matches_numpy_leggauss_nodes(self, n):
        mine = legendre_roots(n)
        reference, _ = np_legendre.leggauss(n)
        reference = sorted(reference)
        for a, b in zip(mine, reference):
            assert a == pytest.approx(b, abs=1e-9)

    @pytest.mark.parametrize("n", [8, 12, 20, 30])
    def test_converges_within_tight_iteration_budget(self, n):
        """A correct initial guess (the standard asymptotic cosine formula)
        converges via Newton's method to near machine precision within just
        3 iterations for these well-separated roots. A poor initial guess
        (e.g. omitting the -0.25 offset) is still off by 1e-4 to 1e-5 at
        that same budget -- this is the only test in this file that can
        distinguish a correct initial-guess formula from an incorrect one,
        since with a generous iteration budget (the function's default of
        100) both converge to the same final answer and are otherwise
        indistinguishable."""
        roots = legendre_roots(n, max_iter=3)
        reference, _ = np_legendre.leggauss(n)
        reference = sorted(reference)
        for a, b in zip(sorted(roots), reference):
            assert a == pytest.approx(b, abs=1e-8)

    def test_odd_n_includes_zero_root(self):
        """Odd-degree Legendre polynomials always have x=0 as a root, by symmetry."""
        roots = legendre_roots(5)
        assert any(abs(r) < 1e-9 for r in roots)

    @pytest.mark.parametrize("n", [4, 6, 8])
    def test_roots_symmetric_about_zero(self, n):
        roots = sorted(legendre_roots(n))
        for a, b in zip(roots, reversed(roots)):
            assert a == pytest.approx(-b, abs=1e-9)


# ---------------------------------------------------------------------------
# Sub-problem 3: legendre_weights
# ---------------------------------------------------------------------------


class TestLegendreWeights:
    @pytest.mark.parametrize("n", [2, 3, 4, 5, 8, 12])
    def test_weights_sum_to_two(self, n):
        """Independent of any reference table: sum of weights = length of [-1, 1]."""
        roots = legendre_roots(n)
        weights = legendre_weights(n, roots)
        assert sum(weights) == pytest.approx(2.0, abs=1e-9)

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 8, 12])
    def test_weights_all_positive(self, n):
        roots = legendre_roots(n)
        weights = legendre_weights(n, roots)
        assert all(w > 0 for w in weights)

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 8, 12])
    def test_matches_numpy_leggauss_weights(self, n):
        roots = legendre_roots(n)
        mine = legendre_weights(n, roots)
        ref_nodes, ref_weights = np_legendre.leggauss(n)
        order = np.argsort(ref_nodes)
        ref_weights_sorted = np.array(ref_weights)[order]
        for a, b in zip(mine, ref_weights_sorted):
            assert a == pytest.approx(b, abs=1e-9)

    @pytest.mark.parametrize("n", [3, 5, 8])
    def test_exactness_property_on_m11(self, n):
        """An n-point Gauss-Legendre rule integrates every polynomial of
        degree <= 2n-1 EXACTLY. This is the defining property of the
        method and is independent of any tabulated reference."""
        for power in range(0, 2 * n):
            approx = gauss_legendre_quadrature(lambda x, p=power: x**p, -1.0, 1.0, n)
            exact = 0.0 if power % 2 == 1 else 2.0 / (power + 1)
            assert approx == pytest.approx(exact, abs=1e-9)

    @pytest.mark.parametrize("n", [3, 5, 8])
    def test_exactness_property_on_shifted_interval(self, n):
        """Same exactness property, but on a non-symmetric interval [0, 2],
        exercising the affine change-of-variables in the quadrature map."""
        for power in range(0, 2 * n):
            approx = gauss_legendre_quadrature(lambda x, p=power: x**p, 0.0, 2.0, n)
            exact = (2.0 ** (power + 1)) / (power + 1)
            assert approx == pytest.approx(exact, abs=1e-7)


# ---------------------------------------------------------------------------
# Main problem: complete_elliptic_K
# ---------------------------------------------------------------------------


def _K_via_agm(k: float, tol: float = 1e-15) -> float:
    """Reference computation of K(k) via the arithmetic-geometric mean --
    a numerical method with no relationship to Gauss-Legendre quadrature,
    used here purely as an independent cross-check."""
    a, b = 1.0, math.sqrt(1 - k**2)
    while abs(a - b) > tol:
        a, b = (a + b) / 2, math.sqrt(a * b)
    return math.pi / (2 * a)


class TestCompleteEllipticK:
    @pytest.mark.parametrize("k", [0.1, 0.3, 0.5, 0.7, 0.9])
    def test_matches_agm_reference_n20(self, k):
        approx = complete_elliptic_K(k, n=20)
        reference = _K_via_agm(k)
        assert approx == pytest.approx(reference, abs=1e-6)

    def test_k_zero_reduces_to_pi_over_2(self):
        """K(0) = integral of 1 over [0, pi/2] = pi/2, exactly."""
        approx = complete_elliptic_K(0.0, n=10)
        assert approx == pytest.approx(math.pi / 2, abs=1e-9)

    def test_increasing_in_k(self):
        """K(k) is a strictly increasing function of k on [0, 1) -- a basic
        qualitative property any correct implementation must reproduce."""
        ks = [0.1, 0.3, 0.5, 0.7, 0.9]
        values = [complete_elliptic_K(k, n=25) for k in ks]
        assert values == sorted(values)

    def test_convergence_improves_with_n(self):
        """For a fixed, moderately challenging k, increasing n should
        strictly reduce the error against the AGM reference."""
        k = 0.9
        reference = _K_via_agm(k)
        err_n10 = abs(complete_elliptic_K(k, n=10) - reference)
        err_n20 = abs(complete_elliptic_K(k, n=20) - reference)
        err_n40 = abs(complete_elliptic_K(k, n=40) - reference)
        assert err_n20 < err_n10
        assert err_n40 < err_n20
        assert err_n40 < 1e-10


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
