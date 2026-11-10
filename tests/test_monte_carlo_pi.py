# Tests for monte_carlo_pi.py
# I wrote these tests with help from Claude (AI) for the structure.
# I calculated the expected values by hand.

import math
import numpy as np
from monte_carlo_pi import count_inside, estimate_pi, summarize, theoretical_std


def test_count_inside():
    # (0,0) is inside, (0.6,0.8) is on the circle, (0.9,0.9) is outside
    x = np.array([0.0, 0.6, 0.9])
    y = np.array([0.0, 0.8, 0.9])
    assert count_inside(x, y) == 2


def test_estimate_pi_is_close():
    rng = np.random.default_rng(0)
    estimate = estimate_pi(1_000_000, rng)
    assert abs(estimate - math.pi) < 0.01


def test_same_seed_same_answer():
    a = estimate_pi(10_000, np.random.default_rng(42))
    b = estimate_pi(10_000, np.random.default_rng(42))
    assert a == b


def test_chunks_give_same_answer():
    a = estimate_pi(10_000, np.random.default_rng(7), chunk_size=10_000)
    b = estimate_pi(10_000, np.random.default_rng(7), chunk_size=500)
    assert a == b


def test_summarize_mean():
    result = summarize([3.0, 3.2, 3.4])
    assert abs(result["mean"] - 3.2) < 1e-9


def test_theoretical_std():
    # sqrt(pi * (4 - pi)) for N = 1
    assert abs(theoretical_std(1) - 1.642) < 0.001
