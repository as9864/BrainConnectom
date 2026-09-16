"""Does real (or realistically biased) PN->KC wiring change how well FlyHash
preserves nearest neighbors, compared to the idealized uniform-random model
from Dasgupta et al. 2017 -- and compared to classical random-hyperplane LSH?

Usage:
    python -m flyhash_experiment.run_experiment
"""
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.datasets import load_digits
from sklearn.metrics import pairwise_distances

load_dotenv()

from flyhash_experiment import connectome
from flyhash_experiment.flyhash import FlyHash, SimHash, hamming_neighbors

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
K_VALUES = [1, 5, 10, 20]
N_QUERIES = 200


def true_neighbors(X, k_max):
    dists = pairwise_distances(X)
    np.fill_diagonal(dists, np.inf)
    return np.argsort(dists, axis=1)[:, :k_max]


def recall_at_k(hash_codes, true_nn, query_indices, k):
    hits = []
    for q in query_indices:
        predicted = hamming_neighbors(hash_codes, q, k)
        true_set = set(true_nn[q, :k].tolist())
        hits.append(len(true_set.intersection(predicted.tolist())) / k)
    return float(np.mean(hits))


def build_methods(n_features, seed):
    n_pn = connectome.N_PN_DEFAULT
    real_W = connectome.try_fetch_real_connectivity()

    methods = {
        "flyhash_idealized": FlyHash(connectome.idealized_connectivity(n_pn=n_pn, seed=seed), seed=seed),
        "flyhash_biased_synthetic": FlyHash(connectome.biased_synthetic_connectivity(n_pn=n_pn, seed=seed), seed=seed),
        "simhash_baseline": SimHash(n_bits=100, seed=seed),
    }
    if real_W is not None:
        methods["flyhash_real_hemibrain"] = FlyHash(real_W, seed=seed)
    return methods


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    digits = load_digits()
    X = digits.data.astype(float)
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

    rng = np.random.default_rng(0)
    query_indices = rng.choice(len(X), size=N_QUERIES, replace=False)
    true_nn = true_neighbors(X, max(K_VALUES))

    methods = build_methods(n_features=X.shape[1], seed=0)

    rows = []
    for name, method in methods.items():
        codes = method.hash(X)
        row = {"method": name, "code_dim": codes.shape[1], "avg_sparsity": codes.mean()}
        for k in K_VALUES:
            row[f"recall@{k}"] = recall_at_k(codes, true_nn, query_indices, k)
        rows.append(row)
        print(f"{name}: " + ", ".join(f"recall@{k}={row[f'recall@{k}']:.3f}" for k in K_VALUES))

    df = pd.DataFrame(rows)
    out_path = RESULTS_DIR / "flyhash_results.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved results to {out_path}")

    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 4))
        for _, row in df.iterrows():
            ax.plot(K_VALUES, [row[f"recall@{k}"] for k in K_VALUES], marker="o", label=row["method"])
        ax.set_xlabel("k")
        ax.set_ylabel("recall@k (vs true Euclidean neighbors)")
        ax.set_title("FlyHash: idealized vs biased/real connectivity vs SimHash")
        ax.legend()
        fig.tight_layout()
        fig_path = RESULTS_DIR / "flyhash_comparison.png"
        fig.savefig(fig_path, dpi=150)
        print(f"Saved plot to {fig_path}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
