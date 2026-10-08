"""Null-normalized, density-aware graph statistics for cross-species comparison.

Raw graph statistics (modularity, clustering, rich-club, degree spread) depend
strongly on how many nodes a graph has, how dense it is and how it was
measured (EM synapse counts vs. diffusion tractography), so raw values from a
300-neuron fly subgraph and a 90-region human connectome are not comparable
(see docs/methodology_transferability.md). The standard remedy in network
neuroscience is to express each statistic *relative to a null model* that
keeps the nuisance properties fixed:

  modularity_norm   Q / <Q_null>            null: degree-preserving rewiring
  clustering_norm   C / <C_null>            null: degree-preserving rewiring
  rich_club_norm    phi(k) / <phi_null(k)>  null: degree-preserving rewiring,
                                            k = 80th percentile degree
  degree_cv_norm    CV(deg) / <CV_ER(deg)>  null: Erdos-Renyi, same n and m
                                            (degree-preserving would keep CV
                                            fixed by construction)

A value of 1 means "no different from random"; "conserved" organization in
the comparative-connectomics sense means the ratio is consistently != 1.

All statistics are computed on the binarized, undirected graph: synapse
counts and streamline counts are not on a common scale, but presence/absence
of a connection is.
"""
import networkx as nx
import numpy as np

STATS = ["modularity_norm", "clustering_norm", "rich_club_norm", "degree_cv_norm"]
N_NULLS_DEFAULT = 5
RICH_CLUB_PERCENTILE = 80


def binarize(W, density=None):
    """Undirected 0/1 adjacency. If `density` is given, keep only the strongest
    edges so the graph has (at most) that density; graphs sparser than the
    target keep all their edges - callers check `density_of` to exclude them.
    """
    S = np.maximum(np.abs(W), np.abs(W).T)
    np.fill_diagonal(S, 0)
    if density is not None:
        n = S.shape[0]
        iu = np.triu_indices(n, 1)
        vals = S[iu]
        n_keep = int(round(density * len(vals)))
        if 0 < n_keep < np.count_nonzero(vals):
            cutoff = np.sort(vals)[::-1][n_keep - 1]
            S = np.where(S >= cutoff, S, 0)
    return (S > 0).astype(int)


def density_of(A):
    n = A.shape[0]
    return A[np.triu_indices(n, 1)].mean() if n > 1 else 0.0


def _modularity(G, seed):
    if G.number_of_edges() == 0:
        return 0.0
    comms = nx.algorithms.community.louvain_communities(G, seed=seed)
    return nx.algorithms.community.modularity(G, comms)


def _rich_club(G, k):
    """Fraction of possible edges present among nodes with degree > k."""
    rich = [v for v, d in G.degree() if d > k]
    r = len(rich)
    if r < 2:
        return np.nan
    return 2 * G.subgraph(rich).number_of_edges() / (r * (r - 1))


def _degree_cv(G):
    deg = np.array([d for _, d in G.degree()], dtype=float)
    return deg.std() / deg.mean() if deg.mean() > 0 else 0.0


def _degree_preserving(G, seed):
    H = G.copy()
    m = H.number_of_edges()
    if m >= 2 and H.number_of_nodes() >= 4:
        nx.double_edge_swap(H, nswap=10 * m, max_tries=100 * m, seed=seed)
    return H


def normalized_signature(W, density=None, n_nulls=N_NULLS_DEFAULT, seed=0):
    """Dict of null-normalized statistics (see module docstring), plus the raw
    values and the density they were computed at, for transparency.
    """
    A = binarize(W, density)
    G = nx.from_numpy_array(A)
    G.remove_edges_from(nx.selfloop_edges(G))
    degrees = np.array([d for _, d in G.degree()])
    k = np.percentile(degrees, RICH_CLUB_PERCENTILE) if len(degrees) else 0

    raw = {
        "modularity": _modularity(G, seed),
        "clustering": nx.average_clustering(G),
        "rich_club": _rich_club(G, k),
        "degree_cv": _degree_cv(G),
    }
    null = {key: [] for key in raw}
    n, m = G.number_of_nodes(), G.number_of_edges()
    for i in range(n_nulls):
        H = _degree_preserving(G, seed=seed * 1000 + i)
        null["modularity"].append(_modularity(H, seed))
        null["clustering"].append(nx.average_clustering(H))
        null["rich_club"].append(_rich_club(H, k))
        E = nx.gnm_random_graph(n, m, seed=seed * 1000 + i)
        null["degree_cv"].append(_degree_cv(E))

    def ratio(key):
        ref = np.nanmean(null[key]) if np.any(np.isfinite(null[key])) else np.nan
        return float(raw[key] / ref) if ref and np.isfinite(ref) and np.isfinite(raw[key]) else np.nan

    sig = {f"{key}_norm": ratio(key) for key in raw}
    sig.update({f"raw_{key}": float(v) for key, v in raw.items()})
    sig["density"] = float(density_of(A))
    sig["n_nodes"] = int(n)
    return sig


def aggregate(signatures, keys=STATS):
    """List[dict] -> {stat: {"mean", "std"}} ignoring NaNs."""
    out = {}
    for key in keys:
        vals = np.array([s[key] for s in signatures], dtype=float)
        vals = vals[np.isfinite(vals)]
        out[key] = {"mean": float(vals.mean()) if len(vals) else np.nan,
                    "std": float(vals.std() + 1e-8) if len(vals) else np.nan}
    return out


def aggregate_species(species_signatures, keys=STATS):
    """Equal weight per species, regardless of how many samples each has."""
    out = {}
    for key in keys:
        vals, weights = [], []
        for sigs in species_signatures:
            v = [s[key] for s in sigs if np.isfinite(s[key])]
            if v:
                vals += v
                weights += [1.0 / len(v)] * len(v)
        vals, weights = np.array(vals), np.array(weights)
        mean = np.average(vals, weights=weights)
        std = np.sqrt(np.average((vals - mean) ** 2, weights=weights))
        out[key] = {"mean": float(mean), "std": float(std + 1e-8)}
    return out


def prior_distance(sig, prior, scale=None, keys=STATS):
    """Standardized squared distance between a signature and a prior's mean.
    `scale` (defaults to the prior's own std) lets different prior sources be
    compared on one common yardstick.
    """
    scale = scale or prior
    d = 0.0
    for key in keys:
        if not np.isfinite(sig[key]) or not np.isfinite(prior[key]["mean"]):
            continue
        d += ((sig[key] - prior[key]["mean"]) / scale[key]["std"]) ** 2
    return float(d)
