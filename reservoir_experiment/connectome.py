"""Load the C. elegans multiplex connectome and build reservoir weight matrices.

Data source: CoMuNeLab/C-elegans-Multiplex-Connectome
https://github.com/CoMuNeLab/C-elegans-Multiplex-Connectome
Layers: 1 = electrical (gap junction), 2 = monadic chemical synapse,
        3 = polyadic chemical synapse. 279 neurons.
"""
from pathlib import Path

import networkx as nx
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data_sources" / "celegans_multiplex" / "Dataset"
EDGES_FILE = DATA_DIR / "celegans_connectome_multiplex.edges"
N_NEURONS = 279


def load_edges(layers=(2, 3)):
    """Return a dict {(i, j): summed_weight} for the requested layers (1-indexed node ids)."""
    weights = {}
    with open(EDGES_FILE) as f:
        for line in f:
            layer, i, j, w = line.split()
            layer, i, j, w = int(layer), int(i), int(j), float(w)
            if layer not in layers:
                continue
            key = (i - 1, j - 1)  # zero-index
            weights[key] = weights.get(key, 0.0) + w
    return weights


def build_weight_matrix(layers=(2, 3), n_nodes=N_NEURONS):
    """Directed weighted adjacency matrix built from real synapse counts."""
    edges = load_edges(layers)
    W = np.zeros((n_nodes, n_nodes))
    for (i, j), w in edges.items():
        W[i, j] = w
    return W


def spectral_radius(W):
    eigvals = np.linalg.eigvals(W)
    return np.max(np.abs(eigvals))


def rescale_spectral_radius(W, target_rho):
    rho = spectral_radius(W)
    if rho == 0:
        raise ValueError("Matrix has spectral radius 0, cannot rescale.")
    return W * (target_rho / rho)


def null_model_degree_preserving(W, seed=0, n_swaps_factor=10):
    """Randomize topology while preserving each node's in/out-degree sequence,
    then reassign the original (real) synapse-weight values to the new edges.
    This isolates the effect of *wiring pattern* from *weight distribution*.
    """
    rng = np.random.default_rng(seed)
    n = W.shape[0]
    binary = (W != 0).astype(int)
    G = nx.from_numpy_array(binary, create_using=nx.DiGraph)
    n_edges = G.number_of_edges()
    try:
        nx.directed_edge_swap(
            G, nswap=n_edges * n_swaps_factor, max_tries=n_edges * n_swaps_factor * 50,
            seed=int(rng.integers(0, 2**31 - 1)),
        )
    except nx.NetworkXException:
        pass  # fall back silently if the graph is too small/dense to swap further
    weight_pool = W[W != 0].copy()
    rng.shuffle(weight_pool)
    W_null = np.zeros((n, n))
    for idx, (i, j) in enumerate(G.edges()):
        W_null[i, j] = weight_pool[idx % len(weight_pool)]
    return W_null


def null_model_erdos_renyi(W, seed=0):
    """Same number of edges, random positions, weights resampled from the real pool."""
    rng = np.random.default_rng(seed)
    n = W.shape[0]
    n_edges = int(np.count_nonzero(W))
    weight_pool = W[W != 0].copy()
    all_positions = [(i, j) for i in range(n) for j in range(n) if i != j]
    chosen_idx = rng.choice(len(all_positions), size=n_edges, replace=False)
    W_null = np.zeros((n, n))
    sampled_weights = rng.choice(weight_pool, size=n_edges, replace=True)
    for k, idx in enumerate(chosen_idx):
        i, j = all_positions[idx]
        W_null[i, j] = sampled_weights[k]
    return W_null


def null_model_dense_gaussian(n_nodes, density, seed=0):
    """Classic 'vanilla' echo-state-network reservoir: unstructured random weights,
    matched density, no relation to any biological graph.
    """
    rng = np.random.default_rng(seed)
    mask = rng.random((n_nodes, n_nodes)) < density
    np.fill_diagonal(mask, False)
    W = rng.normal(0, 1, size=(n_nodes, n_nodes)) * mask
    return W
