"""Does the real C. elegans connectome make a better reservoir than random graphs
of matched size, density and spectral radius?

Compares four reservoir topologies on two classic benchmarks (memory capacity,
NARMA-10 prediction):
  1. real        - actual C. elegans chemical-synapse connectome (weighted, directed)
  2. degree_null - same in/out-degree sequence, rewired connections, real weights
  3. er_null     - same number of edges, uniformly random positions, real weights
  4. dense_esn   - classic unstructured Gaussian reservoir (same density), the
                   textbook echo-state-network baseline unrelated to any real graph

Usage:
    python -m reservoir_experiment.run_experiment --n-trials 20
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from reservoir_experiment import connectome, tasks
from reservoir_experiment.reservoir import LeakyESN

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def build_variants(target_rho, seed):
    W_real_raw = connectome.build_weight_matrix(layers=(2, 3))
    n = W_real_raw.shape[0]
    density = np.count_nonzero(W_real_raw) / (n * n - n)

    variants = {
        "real": connectome.rescale_spectral_radius(W_real_raw, target_rho),
        "degree_null": connectome.rescale_spectral_radius(
            connectome.null_model_degree_preserving(W_real_raw, seed=seed), target_rho
        ),
        "er_null": connectome.rescale_spectral_radius(
            connectome.null_model_erdos_renyi(W_real_raw, seed=seed), target_rho
        ),
        "dense_esn": connectome.rescale_spectral_radius(
            connectome.null_model_dense_gaussian(n, density, seed=seed), target_rho
        ),
    }
    return variants


def run_trial(seed, target_rho, leak, max_delay, washout):
    variants = build_variants(target_rho, seed)
    row = {"seed": seed}

    mc_input = tasks.generate_memory_capacity_input(T=2000, seed=seed)
    narma_u, narma_y = tasks.generate_narma10(T=2000, seed=seed)

    for name, W in variants.items():
        esn = LeakyESN(W, leak=leak, input_scale=1.0, seed=seed)

        states_mc = esn.run(mc_input)
        mc_total, _ = tasks.evaluate_memory_capacity(states_mc, mc_input, max_delay=max_delay, washout=washout)

        esn_narma = LeakyESN(W, leak=leak, input_scale=1.0, seed=seed)
        states_narma = esn_narma.run(narma_u)
        nrmse = tasks.evaluate_narma10(states_narma, narma_y, washout=washout)

        row[f"{name}_memory_capacity"] = mc_total
        row[f"{name}_narma10_nrmse"] = nrmse

    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-trials", type=int, default=20)
    parser.add_argument("--rho", type=float, default=0.9, help="target spectral radius")
    parser.add_argument("--leak", type=float, default=0.3)
    parser.add_argument("--max-delay", type=int, default=30)
    parser.add_argument("--washout", type=int, default=100)
    parser.add_argument("--output", type=str, default="reservoir_results.csv")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    rows = []
    for seed in range(args.n_trials):
        print(f"trial {seed + 1}/{args.n_trials}")
        rows.append(run_trial(seed, args.rho, args.leak, args.max_delay, args.washout))

    df = pd.DataFrame(rows)
    out_path = RESULTS_DIR / args.output
    df.to_csv(out_path, index=False)

    print("\n=== Summary (mean +/- std over trials) ===")
    variants = ["real", "degree_null", "er_null", "dense_esn"]
    for metric in ["memory_capacity", "narma10_nrmse"]:
        print(f"\n{metric}:")
        for v in variants:
            col = f"{v}_{metric}"
            print(f"  {v:12s}: {df[col].mean():.4f} +/- {df[col].std():.4f}")

    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for ax, metric, ylabel in zip(
            axes, ["memory_capacity", "narma10_nrmse"], ["Memory capacity", "NARMA-10 NRMSE (lower=better)"]
        ):
            means = [df[f"{v}_{metric}"].mean() for v in variants]
            stds = [df[f"{v}_{metric}"].std() for v in variants]
            ax.bar(variants, means, yerr=stds, capsize=4)
            ax.set_ylabel(ylabel)
            ax.tick_params(axis="x", rotation=20)
        fig.suptitle("C. elegans connectome vs null models as a reservoir")
        fig.tight_layout()
        fig_path = RESULTS_DIR / "reservoir_comparison.png"
        fig.savefig(fig_path, dpi=150)
        print(f"\nSaved plot to {fig_path}")
    except ImportError:
        pass

    print(f"Saved raw results to {out_path}")


if __name__ == "__main__":
    main()
