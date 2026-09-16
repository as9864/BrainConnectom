"""Graph-level topological statistics used as the cross-species "biological prior".

Every function here operates on a plain weighted adjacency matrix (numpy array,
square, zero diagonal) and returns either a scalar or a small dict of scalars.
We deliberately stay at the *graph* level (never touch individual node identity)
because C. elegans/fly neurons and human macro-scale ROIs have no natural
correspondence - see docs/ARCHITECTURE.md for why that rules out node-level
transfer.
"""
import networkx as nx
import numpy as np

# Reuse the degree-preserving null model from the reservoir experiment instead
# of reimplementing it - same rewiring logic applies to any weighted directed
# or undirected matrix.
from reservoir_experiment.connectome import null_model_degree_preserving, null_model_erdos_renyi


def _to_undirected_graph(W):
    """Binarized, undirected view used for community/rich-club statistics."""
    A = (np.abs(W) > 0).astype(int)
    A = np.maximum(A, A.T)  # symmetrize: an edge either direction counts
    np.fill_diagonal(A, 0)
    return nx.from_numpy_array(A)


def node_strength_stats(W):
    """Mean/std of node strength (sum of incident edge weights) - the
    weighted, degree-distribution analogue used across all three species.
    """
    strength = np.abs(W).sum(axis=0) + np.abs(W).sum(axis=1)
    return {"strength_mean": float(strength.mean()), "strength_std": float(strength.std())}


def weighted_clustering(W):
    """Average Onnela et al. (2005) weighted clustering coefficient.
    Note: for a *bipartite* graph (e.g. raw PN->KC connectivity) this is
    always exactly 0 by construction (no triangles possible), so callers
    embedding a bipartite matrix into a square one should treat this
    statistic as not meaningful for that source and exclude it - see
    invertebrate_prior.py.
    """
    G = _to_undirected_graph(W)
    weights = {(i, j): abs(W[i, j]) + abs(W[j, i]) for i, j in G.edges()}
    nx.set_edge_attributes(G, weights, "weight")
    if G.number_of_edges() == 0:
        return 0.0
    return float(nx.average_clustering(G, weight="weight"))


def modularity(W):
    """Greedy-modularity community score on the binarized undirected graph."""
    G = _to_undirected_graph(W)
    if G.number_of_edges() == 0:
        return 0.0
    communities = nx.algorithms.community.greedy_modularity_communities(G)
    return float(nx.algorithms.community.modularity(G, communities))


def rich_club_coefficient(W, k_frac=0.2):
    """Simple (non-normalized) rich-club coefficient: among the top `k_frac`
    highest-degree nodes, what fraction of all possible edges among them
    actually exist? A high value means hubs preferentially connect to
    other hubs, a property repeatedly reported as conserved across species.
    """
    G = _to_undirected_graph(W)
    n = G.number_of_nodes()
    if n < 4:
        return 0.0
    degrees = dict(G.degree())
    k = max(2, int(round(k_frac * n)))
    hubs = [node for node, _ in sorted(degrees.items(), key=lambda kv: -kv[1])[:k]]
    sub = G.subgraph(hubs)
    possible = k * (k - 1) / 2
    return float(sub.number_of_edges() / possible) if possible else 0.0


def topology_signature(W, include_clustering=True):
    """Bundle of graph-level statistics that make up one "sample" of the
    cross-species topological prior.
    """
    sig = {
        "modularity": modularity(W),
        "rich_club": rich_club_coefficient(W),
        **node_strength_stats(W),
    }
    if include_clustering:
        sig["clustering"] = weighted_clustering(W)
    return sig


def subsample_subgraph(W, frac_nodes=0.8, seed=0):
    """Random node-induced subgraph, keeping only real edges among the kept
    nodes. Unlike a null model this does NOT scramble the wiring - it is a
    legitimate way to get more than one correlated sample of "real biological
    topology" out of a single connectome for prior estimation.
    """
    rng = np.random.default_rng(seed)
    n = W.shape[0]
    k = max(4, int(round(frac_nodes * n)))
    keep = rng.choice(n, size=k, replace=False)
    return W[np.ix_(keep, keep)]


def degree_preserving_null(W, seed=0):
    """Thin re-export so callers only need to import this module."""
    return null_model_degree_preserving(W, seed=seed)


def erdos_renyi_null(W, seed=0):
    """Thin re-export. Unlike degree_preserving_null, this does NOT keep the
    node strength/degree distribution intact, which makes it the meaningful
    negative control for a strength/hub-based regularizer: a
    degree-preserving null is, by construction, nearly indistinguishable
    from the real graph on strength statistics (only *who* connects to whom
    changes, not the degree sequence itself), so it can't serve as a null
    control for exactly the statistic (see decoder.py's
    _reshape_toward_target_hubness) this prior is built around.
    """
    return null_model_erdos_renyi(W, seed=seed)
