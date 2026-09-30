"""Build the cross-species "topological prior": a distribution over
biologically-plausible graph statistics, estimated from real structural
connectomes of two species: C. elegans (whole-animal chemical synapses) and
Drosophila (neuron-level subgraphs of several hemibrain circuits - mushroom
body, central complex, lateral horn, antennal lobe, lateral complex). Also
builds a matched "null prior" from Erdos-Renyi randomized versions of the same
graphs, used later as a negative control - if regularizing with the null prior
helps just as much as the biological one, the improvement isn't really about
biology.
"""
import numpy as np

from reservoir_experiment.connectome import build_weight_matrix as celegans_weight_matrix
from flyhash_experiment import hemibrain
from flyhash_experiment.connectome import biased_synthetic_connectivity, try_fetch_real_connectivity
from sc_prior_experiment.topology import (
    topology_signature,
    subsample_subgraph,
    erdos_renyi_null,
)

N_SUBSAMPLES_PER_GRAPH = 8
SUBSAMPLE_FRAC = 0.8
# Fly circuits are 650-3,100 neurons; full-size graph statistics take ~1 min
# each (greedy modularity), so each circuit is sampled as random node-induced
# subgraphs of about C. elegans' size instead.
FLY_SUBGRAPH_NODES = 300


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


def _fly_pn_kc_graph():
    """Legacy fly source: the bipartite PN->KC matrix. Only used when the
    hemibrain circuit files are missing."""
    real = try_fetch_real_connectivity()
    if real is not None:
        return real, "real_hemibrain_pn_kc"
    return biased_synthetic_connectivity(seed=0), "biased_synthetic_pn_kc"


def _fly_corpus(seed_offset):
    """Biological and null signatures for the fly. Prefers real hemibrain
    circuits (non-bipartite, so clustering is meaningful); falls back to the
    bipartite PN->KC matrix without clustering if the circuit files are absent.
    """
    circuits = hemibrain.available_circuits()
    if not circuits:
        W_raw, source = _fly_pn_kc_graph()
        print(f"[invertebrate_prior] fly: {W_raw.shape} PN->KC ({source}); "
              "hemibrain circuits not found, see flyhash_experiment/hemibrain.py")
        bio, null = _corpus_from_base(_embed_bipartite(W_raw), seed_offset, include_clustering=False)
        return bio, null

    bio, null = [], []
    for c, name in enumerate(circuits):
        W = hemibrain.load_circuit(name)
        n = W.shape[0]
        frac = min(1.0, FLY_SUBGRAPH_NODES / n)
        for i in range(N_SUBSAMPLES_PER_GRAPH + 1):  # +1 matches the real-graph sample C. elegans gets
            seed = (seed_offset * 100 + c) * 100 + i
            sub = subsample_subgraph(W, frac_nodes=frac, seed=seed)
            bio.append(topology_signature(sub, include_clustering=True))
            null.append(topology_signature(erdos_renyi_null(sub, seed=seed), include_clustering=True))
        print(f"[invertebrate_prior] fly: {name} ({n} neurons, real hemibrain v1.2) -> "
              f"{N_SUBSAMPLES_PER_GRAPH + 1} subgraphs of {sub.shape[0]} neurons")
    return bio, null


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


def _aggregate(species_signatures):
    """List (one entry per species) of List[dict] -> {stat_name: {"mean", "std"}}.
    Each species gets equal total weight regardless of how many graph samples
    it contributed, so the fly's several circuits don't drown out C. elegans.
    """
    keys = []
    for sigs in species_signatures:
        keys += [k for k in sigs[0] if k not in keys]
    out = {}
    for k in keys:
        vals, weights = [], []
        for sigs in species_signatures:
            v = [s[k] for s in sigs if k in s]
            if not v:  # e.g. no clustering from a bipartite fly graph
                continue
            vals += v
            weights += [1.0 / len(v)] * len(v)
        vals, weights = np.array(vals), np.array(weights)
        mean = np.average(vals, weights=weights)
        std = np.sqrt(np.average((vals - mean) ** 2, weights=weights))
        out[k] = {"mean": float(mean), "std": float(std + 1e-8)}
    return out


def build_prior(seed=0):
    """Returns (bio_prior, null_prior), each {stat_name: {mean, std}}.

    Species are weighted equally (see _aggregate). With the hemibrain circuit
    files present both species contribute every statistic; in the PN->KC
    fallback the fly contributes no clustering (bipartite, so no triangles).
    """
    celegans_W = celegans_weight_matrix()
    print(f"[invertebrate_prior] C. elegans: {celegans_W.shape[0]} neurons (real chemical synapse connectome)")
    celegans_bio, celegans_null = _corpus_from_base(celegans_W, seed_offset=1, include_clustering=True)
    fly_bio, fly_null = _fly_corpus(seed_offset=2)

    bio_prior = _aggregate([celegans_bio, fly_bio])
    null_prior = _aggregate([celegans_null, fly_null])
    print(f"[invertebrate_prior] biological corpus: {len(celegans_bio)} C. elegans + {len(fly_bio)} fly graph samples "
          "(species weighted equally)")
    print(f"[invertebrate_prior] prior stats: {list(bio_prior.keys())}")
    return bio_prior, null_prior
