"""Does a cross-species topological prior (learned from C. elegans + fly
structural connectomes) improve reconstruction of a human structural
connectome from a human functional connectome, relative to a plain
supervised baseline?

Three conditions are compared on held-out synthetic subjects (see
human_data.py for why the human data is synthetic in this 2-week pilot):
  1. baseline   - Ridge regression FC -> SC, no prior
  2. null_prior - baseline blended toward a *degree-preserving-rewired*
                  version of the same invertebrate graphs (negative control:
                  regularization from a non-biological, degree-matched target)
  3. bio_prior  - baseline blended toward the real cross-species topological
                  prior

If bio_prior beats both baseline and null_prior, that is evidence the
improvement is really coming from conserved biological structure and not
just "any regularization toward a plausible-looking target".

Usage:
    python -m sc_prior_experiment.run_experiment --n-subjects 60
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from sc_prior_experiment import human_data, decoder
from sc_prior_experiment.invertebrate_prior import build_prior
from sc_prior_experiment.topology import topology_signature
from reservoir_experiment.connectome import rescale_spectral_radius
from reservoir_experiment.reservoir import LeakyESN
from reservoir_experiment import tasks

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
SHARED_STATS = ["modularity", "rich_club", "strength_mean", "strength_std", "clustering"]


def edge_correlation(pred, true):
    r, _ = pearsonr(decoder.vectorize(pred), decoder.vectorize(true))
    return float(r) if not np.isnan(r) else 0.0


def topology_distance(pred, true):
    """Sum of squared *relative* errors across shared graph statistics -
    relative (not absolute) so terms measured on very different natural
    scales (e.g. strength vs. modularity) don't dominate the sum."""
    sig_pred = topology_signature(pred)
    sig_true = topology_signature(true)
    diffs = [((sig_pred[k] - sig_true[k]) / (abs(sig_true[k]) + 1e-6)) ** 2 for k in SHARED_STATS]
    return float(np.sqrt(np.sum(diffs)))


def functional_validity_check(pred_sc, true_sc, target_rho=0.9, seed=0):
    """Cross-check: do reservoirs built from the *predicted* SC show similar
    computational properties (memory capacity, NARMA-10) to reservoirs built
    from the *true* SC? Reuses the reservoir_experiment benchmark suite
    unchanged.
    """
    results = {}
    for label, W in [("predicted", pred_sc), ("true", true_sc)]:
        W_scaled = rescale_spectral_radius(W, target_rho)
        mc_input = tasks.generate_memory_capacity_input(T=1500, seed=seed)
        narma_u, narma_y = tasks.generate_narma10(T=1500, seed=seed)

        esn_mc = LeakyESN(W_scaled, leak=0.3, seed=seed)
        mc_total, _ = tasks.evaluate_memory_capacity(esn_mc.run(mc_input), mc_input, washout=100)

        esn_narma = LeakyESN(W_scaled, leak=0.3, seed=seed)
        nrmse = tasks.evaluate_narma10(esn_narma.run(narma_u), narma_y, washout=100)

        results[label] = {"memory_capacity": mc_total, "narma10_nrmse": nrmse}
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-subjects", type=int, default=60)
    parser.add_argument("--n-regions", type=int, default=90)
    parser.add_argument("--train-frac", type=float, default=0.7)
    parser.add_argument("--alpha-blend", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)

    print("=== Building cross-species topological prior ===")
    bio_prior, null_prior = build_prior(seed=args.seed)

    print("\n=== Building synthetic human SC/FC cohort ===")
    cohort = human_data.make_cohort(n_subjects=args.n_subjects, n_regions=args.n_regions, seed=args.seed)
    split = int(len(cohort) * args.train_frac)
    train, test = cohort[:split], cohort[split:]

    print(f"\n=== Training baseline FC->SC decoder on {len(train)} subjects ===")
    model = decoder.train_baseline_decoder(train)

    rows = []
    for i, subj in enumerate(test):
        true_sc = subj["sc"]
        pred_baseline = decoder.predict_sc(model, subj["fc"], args.n_regions)
        pred_null = decoder.prior_regularized_predict(model, subj["fc"], args.n_regions, null_prior, args.alpha_blend)
        pred_bio = decoder.prior_regularized_predict(model, subj["fc"], args.n_regions, bio_prior, args.alpha_blend)

        rows.append({
            "test_subject": i,
            "baseline_edge_corr": edge_correlation(pred_baseline, true_sc),
            "null_prior_edge_corr": edge_correlation(pred_null, true_sc),
            "bio_prior_edge_corr": edge_correlation(pred_bio, true_sc),
            "baseline_topo_dist": topology_distance(pred_baseline, true_sc),
            "null_prior_topo_dist": topology_distance(pred_null, true_sc),
            "bio_prior_topo_dist": topology_distance(pred_bio, true_sc),
        })

    df = pd.DataFrame(rows)
    out_path = RESULTS_DIR / "sc_prior_results.csv"
    df.to_csv(out_path, index=False)

    print("\n=== Summary (mean +/- std over held-out subjects) ===")
    conditions = ["baseline", "null_prior", "bio_prior"]
    for metric in ["edge_corr", "topo_dist"]:
        print(f"\n{metric}:")
        for c in conditions:
            col = f"{c}_{metric}"
            print(f"  {c:12s}: {df[col].mean():.4f} +/- {df[col].std():.4f}")

    print("\n=== Functional validity check (reservoir task performance, first test subject) ===")
    first_true_sc = test[0]["sc"]
    first_pred_sc = decoder.prior_regularized_predict(model, test[0]["fc"], args.n_regions, bio_prior, args.alpha_blend)
    func_check = functional_validity_check(first_pred_sc, first_true_sc, seed=args.seed)
    for label, metrics in func_check.items():
        print(f"  {label:9s}: memory_capacity={metrics['memory_capacity']:.4f}, "
              f"narma10_nrmse={metrics['narma10_nrmse']:.4f}")
    pd.DataFrame(func_check).T.to_csv(RESULTS_DIR / "sc_prior_functional_check.csv")

    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for ax, metric, ylabel in zip(
            axes, ["edge_corr", "topo_dist"],
            ["Edge-wise correlation with true SC (higher=better)", "Topology distance to true SC (lower=better)"],
        ):
            means = [df[f"{c}_{metric}"].mean() for c in conditions]
            stds = [df[f"{c}_{metric}"].std() for c in conditions]
            ax.bar(conditions, means, yerr=stds, capsize=4)
            ax.set_ylabel(ylabel)
            ax.tick_params(axis="x", rotation=15)
        fig.suptitle("FC->SC reconstruction: baseline vs. null vs. cross-species biological prior")
        fig.tight_layout()
        fig_path = RESULTS_DIR / "sc_prior_comparison.png"
        fig.savefig(fig_path, dpi=150)
        print(f"\nSaved plot to {fig_path}")
    except ImportError:
        pass

    print(f"Saved raw results to {out_path}")


if __name__ == "__main__":
    main()
