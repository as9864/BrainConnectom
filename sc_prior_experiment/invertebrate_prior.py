"""Build the cross-species "topological prior": a distribution over
biologically-plausible graph statistics, estimated from the two real
structural connectomes already used elsewhere in this repo (C. elegans,
fly mushroom body). Also builds a matched "null prior" from Erdos-Renyi
randomized versions of the same graphs, used later as a negative control -
if regularizing with the null prior helps just as much as the biological
one, the improvement isn't really about biology.
"""
import numpy as np

from reservoir_experiment.connectome import build_weight_matrix as celegans_weight_matrix
from flyhash_experiment.connectome import biased_synthetic_connectivity, try_fetch_real_connectivity
from sc_prior_experiment.topology import (
    topology_signature,
    subsample_subgraph,
    erdos_renyi_null,
)

N_SUBSAMPLES_PER_GRAPH = 8
SUBSAMPLE_FRAC = 0.8


def _embed_bipartite(W_kc_pn):
    """Embed a (n_kc, n_pn) PN->KC matrix into a square adjacency so the
    generic topology functions can operate on it. Clustering is excluded
    downstream for this source since a bipartite graph has zero triangles
    by construction - that's a property of the graph type, not a bug.
    """
    n_kc, n_pn = W_kc_pn.shape
    n = n_kc + n_pn
    square = np.zeros((n, n))
    square[n_pn:, :n_pn] = W_kc_pn  # KC rows, PN cols
    return square


def _fly_base_graph():
    real = try_fetch_real_connectivity()
    if real is not None:
        return real, "real_hemibrain"
    return biased_synthetic_connectivity(seed=0), "biased_synthetic"


def _corpus_from_base(W, seed_offset, include_clustering):
    """Real graph + N random node-induced subgraphs (biological corpus) and
    matching Erdos-Renyi nulls (negative-control corpus). We use the ER null
    here rather than the degree-preserving null used elsewhere in this repo,
    because the regularizer this prior feeds (decoder.py's strength/hub-CV
    reshaping) is itself a strength-distribution statistic - a
    degree-preserving null keeps that exact statistic by construction and so
    would be a meaningless negative control for it. See topology.py's
    erdos_renyi_null docstring.
    """
    bio_sigs, null_sigs = [], []
    bio_sigs.append(topology_signature(W, include_clustering))
    null_sigs.append(topology_signature(erdos_renyi_null(W, seed=seed_offset), include_clustering))
    for i in range(N_SUBSAMPLES_PER_GRAPH):
        seed = seed_offset * 100 + i
        sub = subsample_subgraph(W, frac_nodes=SUBSAMPLE_FRAC, seed=seed)
        bio_sigs.append(topology_signature(sub, include_clustering))
        null_sigs.append(topology_signature(erdos_renyi_null(sub, seed=seed), include_clustering))
    return bio_sigs, null_sigs


def _aggregate(signatures):
    """List[dict] -> {stat_name: {"mean":..., "std":...}}"""
    keys = signatures[0].keys()
    out = {}
    for k in keys:
        vals = np.array([s[k] for s in signatures if k in s])
        out[k] = {"mean": float(vals.mean()), "std": float(vals.std() + 1e-8)}
    return out


def build_prior(seed=0):
    """Returns (bio_prior, null_prior), each {stat_name: {mean, std}}.

    C. elegans contributes triangle-based statistics (clustering, modularity,
    rich-club) since it's a genuine non-bipartite wiring diagram; the fly
    PN->KC circuit is bipartite by construction, so it only contributes
    degree/strength and rich-club-style statistics, not clustering.
    """
    celegans_W = celegans_weight_matrix()
    fly_W_raw, fly_source = _fly_base_graph()
    fly_W = _embed_bipartite(fly_W_raw)
    print(f"[invertebrate_prior] C. elegans: {celegans_W.shape[0]} neurons (real chemical synapse connectome)")
    print(f"[invertebrate_prior] fly: {fly_W_raw.shape} PN->KC ({fly_source})")

    celegans_bio, celegans_null = _corpus_from_base(celegans_W, seed_offset=1, include_clustering=True)
    fly_bio, fly_null = _corpus_from_base(fly_W, seed_offset=2, include_clustering=False)

    bio_prior = _aggregate(celegans_bio + fly_bio)
    null_prior = _aggregate(celegans_null + fly_null)
    print(f"[invertebrate_prior] biological corpus: {len(celegans_bio) + len(fly_bio)} graph samples")
    print(f"[invertebrate_prior] prior stats: {list(bio_prior.keys())}")
    return bio_prior, null_prior
