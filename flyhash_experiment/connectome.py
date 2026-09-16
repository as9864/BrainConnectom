"""PN -> Kenyon cell connectivity for FlyHash, in three flavors:

  idealized        - the model used in Dasgupta et al. 2017 (Science): each KC
                      samples exactly `claws` PNs uniformly at random, weight 1.
  biased_synthetic - a offline stand-in for real anatomy when no neuPrint token
                      is configured: KC in-degree ~ Poisson(mean claws), and PNs
                      are NOT sampled uniformly (some PN types are wired to KCs
                      far more often than others, as reported in EM reconstructions).
  real (neuprint)  - actual PN->KC synapse counts fetched from the hemibrain
                      dataset via neuprint-python. Requires a free API token,
                      see README.md for how to get one.

Every mode returns an (n_KC, n_PN) numpy array of non-negative weights.
"""
import os

import numpy as np

N_PN_DEFAULT = 50
N_KC_DEFAULT = 2000
MEAN_CLAWS_DEFAULT = 6


def idealized_connectivity(n_kc=N_KC_DEFAULT, n_pn=N_PN_DEFAULT, claws=MEAN_CLAWS_DEFAULT, seed=0):
    rng = np.random.default_rng(seed)
    W = np.zeros((n_kc, n_pn))
    for k in range(n_kc):
        chosen = rng.choice(n_pn, size=claws, replace=False)
        W[k, chosen] = 1.0
    return W


def biased_synthetic_connectivity(n_kc=N_KC_DEFAULT, n_pn=N_PN_DEFAULT, mean_claws=MEAN_CLAWS_DEFAULT, seed=0):
    """Degree varies (Poisson) and PN sampling is skewed (Zipf-like popularity),
    which is qualitatively closer to what EM reconstructions of the mushroom
    body calyx report than the uniform idealized model.
    """
    rng = np.random.default_rng(seed)
    # Zipf-like popularity: a few PNs are wired to many more KCs than others.
    ranks = np.arange(1, n_pn + 1)
    popularity = 1.0 / ranks
    popularity = popularity / popularity.sum()
    rng.shuffle(popularity)  # which specific PN is "popular" is arbitrary

    W = np.zeros((n_kc, n_pn))
    for k in range(n_kc):
        degree = max(1, rng.poisson(mean_claws))
        chosen = rng.choice(n_pn, size=min(degree, n_pn), replace=False, p=popularity)
        synapse_counts = rng.integers(1, 5, size=len(chosen))  # a "claw" is several synapses
        W[k, chosen] = synapse_counts
    return W


def try_fetch_real_connectivity(n_pn_max=None):
    """Fetch real PN->KC synapse counts from the hemibrain dataset via neuprint.
    Returns None (and prints why) if no token is configured or the request fails,
    so callers can fall back to `biased_synthetic_connectivity`.
    """
    token = os.environ.get("NEUPRINT_TOKEN")
    if not token:
        print("[connectome] NEUPRINT_TOKEN not set - skipping real hemibrain fetch. "
              "See README.md to get a free token.")
        return None
    try:
        from neuprint import Client, NeuronCriteria as NC, fetch_adjacencies
    except ImportError:
        print("[connectome] neuprint-python not installed - skipping real fetch.")
        return None

    try:
        Client("neuprint.janelia.org", dataset="hemibrain:v1.2.1", token=token)
        pn_crit = NC(type=".*PN.*", regex=True, status="Traced")
        kc_crit = NC(type="^KC.*", regex=True, status="Traced")
        neuron_df, conn_df = fetch_adjacencies(pn_crit, kc_crit)
        if conn_df.empty:
            print("[connectome] neuprint query returned no PN->KC connections.")
            return None

        pn_ids = sorted(conn_df["bodyId_pre"].unique())
        kc_ids = sorted(conn_df["bodyId_post"].unique())
        if n_pn_max:
            pn_ids = pn_ids[:n_pn_max]
        pn_index = {b: i for i, b in enumerate(pn_ids)}
        kc_index = {b: i for i, b in enumerate(kc_ids)}

        W = np.zeros((len(kc_ids), len(pn_ids)))
        for _, row in conn_df.iterrows():
            if row["bodyId_pre"] not in pn_index:
                continue
            W[kc_index[row["bodyId_post"]], pn_index[row["bodyId_pre"]]] += row["weight"]
        print(f"[connectome] fetched real hemibrain PN->KC matrix: {W.shape}")
        return W
    except Exception as exc:  # noqa: BLE001 - any network/auth error should just trigger fallback
        print(f"[connectome] real hemibrain fetch failed ({exc}); falling back to synthetic data.")
        return None
