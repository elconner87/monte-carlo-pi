"""
Monte Carlo estimation of pi: how fast does the error shrink?

Question: If we estimate pi by throwing N random points at a square,
how does the error of the estimate shrink as N grows? Theory says the
typical error should shrink like 1 / sqrt(N). This program measures it.

Method:
  1. Throw N random points (x, y) into the unit square [0, 1) x [0, 1).
  2. Count how many land inside the quarter circle x^2 + y^2 <= 1.
  3. The quarter circle covers pi/4 of the square, so
         pi is approximately 4 * (points inside) / N.
  4. Repeat many times (trials) for each N and measure how much the
     estimates scatter around the true value of pi.
  5. Fit a straight line to log(error) vs log(N). A slope of -0.5
     means the error shrinks like 1 / sqrt(N).

Outputs (written to the results/ folder):
  results/convergence.csv    one row per sample size
  results/summary.txt        fitted slope and key numbers
  results/convergence.png    log-log plot of error vs N

AI assistance: Code drafted with Claude (Anthropic), November 2026.
Reviewed, tested, and run on Great Lakes by the author. See README.md.
"""

import csv          # standard library: writes CSV files
import os           # standard library: makes folders, builds file paths
import time         # standard library: measures how long the run takes

import numpy as np  # third-party: random numbers and fast array math

import matplotlib
matplotlib.use("Agg")            # draw plots to files; no screen needed
import matplotlib.pyplot as plt  # third-party: plotting


# ---------------------------------------------------------------------
# Settings for the full run on Great Lakes
# ---------------------------------------------------------------------
SAMPLE_SIZES = [10**2, 10**3, 10**4, 10**5, 10**6, 10**7, 10**8, 10**9]
N_TRIALS = 30       # repeated estimates for each sample size
SEED = 2026         # fixed seed, so every run gives identical results
OUTDIR = "results"  # folder where output files are written


def count_inside(x, y):
    """Return how many points (x[i], y[i]) lie inside the unit circle.

    A point is inside (or on the edge) when x^2 + y^2 <= 1.
    """
    inside = (x**2 + y**2) <= 1.0   # array of True/False, one per point
    return int(np.sum(inside))      # True counts as 1, False as 0


def estimate_pi(n_samples, rng, chunk_size=1_000_000):
    """Estimate pi from n_samples random points.

    Points are generated in chunks so that very large n_samples
    (e.g. 100 million) never needs a huge array in memory at once.
    """
    if n_samples <= 0:
        raise ValueError("n_samples must be a positive integer")

    total_inside = 0
    remaining = n_samples
    while remaining > 0:
        this_chunk = min(chunk_size, remaining)   # last chunk may be smaller
        points = rng.random((this_chunk, 2))      # each row is one (x, y) point
        total_inside += count_inside(points[:, 0], points[:, 1])
        remaining -= this_chunk

    # The fraction inside approximates pi/4, so multiply by 4.
    return 4.0 * total_inside / n_samples


def run_trials(n_samples, n_trials, rng):
    """Return a NumPy array of n_trials independent estimates of pi."""
    estimates = [estimate_pi(n_samples, rng) for _ in range(n_trials)]
    return np.array(estimates)


def summarize(estimates):
    """Summarize repeated estimates of pi.

    Returns a dictionary with:
      mean            average of the estimates
      std             sample standard deviation (spread of the estimates)
      mean_abs_error  average of |estimate - pi|
    """
    estimates = np.asarray(estimates, dtype=float)
    return {
        "mean": float(np.mean(estimates)),
        "std": float(np.std(estimates, ddof=1)),   # ddof=1: sample std
        "mean_abs_error": float(np.mean(np.abs(estimates - np.pi))),
    }


def theoretical_std(n_samples):
    """Standard deviation predicted by probability theory.

    Each point is inside with probability p = pi/4, and each point
    contributes 4 * (0 or 1) to the estimate. The variance of one such
    value is 16 * p * (1 - p) = pi * (4 - pi). Averaging N independent
    values divides the variance by N, so the standard deviation is
        sqrt(pi * (4 - pi) / N)  which is about 1.642 / sqrt(N).
    """
    return float(np.sqrt(np.pi * (4.0 - np.pi) / n_samples))


def fit_power_law(sample_sizes, errors):
    """Fit errors = C * N^slope by a straight line in log-log space.

    Taking log10 of both sides gives
        log10(error) = slope * log10(N) + log10(C),
    which is a straight line. np.polyfit(..., 1) fits that line.
    Returns (slope, C).
    """
    log_n = np.log10(sample_sizes)
    log_err = np.log10(errors)
    slope, intercept = np.polyfit(log_n, log_err, 1)
    return float(slope), float(10**intercept)


def run_experiment(sample_sizes, n_trials, seed, outdir):
    """Run the full convergence study and write all output files.

    Returns the list of result rows (one dictionary per sample size).
    """
    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(seed)   # one seeded generator for the whole run
    start = time.perf_counter()

    rows = []
    for n in sample_sizes:
        estimates = run_trials(n, n_trials, rng)
        stats = summarize(estimates)
        row = {
            "n_samples": n,
            "mean_estimate": stats["mean"],
            "std": stats["std"],
            "theoretical_std": theoretical_std(n),
            "mean_abs_error": stats["mean_abs_error"],
        }
        rows.append(row)
        print(f"N = {n:>11,d}   mean = {row['mean_estimate']:.6f}   "
              f"std = {row['std']:.2e}   theory = {row['theoretical_std']:.2e}")

    elapsed = time.perf_counter() - start

    # --- fit the convergence rate ---
    ns = [r["n_samples"] for r in rows]
    slope, constant = fit_power_law(ns, [r["std"] for r in rows])

    # --- write the CSV table ---
    csv_path = os.path.join(outdir, "convergence.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # --- write the text summary ---
    best = rows[-1]   # the largest sample size
    lines = [
        "Monte Carlo estimation of pi - convergence study",
        f"Sample sizes:            {ns[0]:,} to {ns[-1]:,}",
        f"Trials per sample size:  {n_trials}",
        f"Random seed:             {seed}",
        f"Fitted slope (std vs N): {slope:.3f}   (theory: -0.500)",
        f"Fitted constant C:       {constant:.3f}   (theory: {np.sqrt(np.pi * (4 - np.pi)):.3f})",
        f"Best mean estimate:      {best['mean_estimate']:.7f}  (N = {best['n_samples']:,})",
        f"True value of pi:        {np.pi:.7f}",
        f"Run time:                {elapsed:.1f} s",
    ]
    with open(os.path.join(outdir, "summary.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print()
    print("\n".join(lines))

    # --- make the plot ---
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(ns, [r["std"] for r in rows], "o", label="Measured spread (std)")
    ax.loglog(ns, [r["theoretical_std"] for r in rows], "--",
              label="Theory: sqrt(pi*(4-pi)/N)")
    ax.set_xlabel("Number of random points N")
    ax.set_ylabel("Standard deviation of the estimate")
    ax.set_title(f"Monte Carlo pi: error shrinks like N^{slope:.2f}")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "convergence.png"), dpi=150)
    plt.close(fig)

    return rows


if __name__ == "__main__":
    print("Monte Carlo estimation of pi")
    print("Measuring how the error of the estimate shrinks as the number")
    print("of random points N grows (theory predicts 1/sqrt(N)).")
    print()
    run_experiment(SAMPLE_SIZES, N_TRIALS, SEED, OUTDIR)
    print(f"\nOutputs written to {OUTDIR}/")
