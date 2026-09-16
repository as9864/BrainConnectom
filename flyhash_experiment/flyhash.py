"""FlyHash: the fruit-fly olfactory circuit as a locality-sensitive hash.

Dasgupta, Stevens & Navlakha (2017), "A neural algorithm for a fundamental
computing problem", Science. Pipeline: sensory input -> (random projection to)
PN activations -> sparse random expansion to Kenyon cells -> winner-take-all
sparsification -> sparse binary hash code.
"""
import numpy as np


class FlyHash:
    def __init__(self, pn_kc_weights, wta_sparsity=0.05, seed=0):
        """pn_kc_weights: (n_kc, n_pn) connectivity matrix (any of the three
        modes in connectome.py)."""
        self.W = pn_kc_weights
        self.n_kc, self.n_pn = pn_kc_weights.shape
        self.wta_sparsity = wta_sparsity
        self._rng = np.random.default_rng(seed)
        self._input_projection = None

    def _project_to_pn_space(self, X):
        """Random projection from raw feature space to PN activations, mirroring
        how real odors are transduced into a fixed-size PN population."""
        n_features = X.shape[1]
        if self._input_projection is None or self._input_projection.shape[0] != n_features:
            self._input_projection = self._rng.normal(0, 1 / np.sqrt(n_features), size=(n_features, self.n_pn))
        pn = X @ self._input_projection
        return np.maximum(pn, 0)  # PNs are firing rates, non-negative

    def hash(self, X):
        """X: (n_samples, n_features) -> binary sparse codes (n_samples, n_kc)."""
        pn = self._project_to_pn_space(X)
        kc = pn @ self.W.T  # (n_samples, n_kc)
        k = max(1, int(self.wta_sparsity * self.n_kc))
        codes = np.zeros_like(kc, dtype=np.uint8)
        top_k_idx = np.argpartition(-kc, k - 1, axis=1)[:, :k]
        rows = np.arange(kc.shape[0])[:, None]
        codes[rows, top_k_idx] = 1
        return codes


class SimHash:
    """Classical random-hyperplane LSH baseline (dense, low-dimensional codes)."""

    def __init__(self, n_bits, seed=0):
        self.n_bits = n_bits
        self._rng = np.random.default_rng(seed)
        self._planes = None

    def hash(self, X):
        n_features = X.shape[1]
        if self._planes is None:
            self._planes = self._rng.normal(size=(n_features, self.n_bits))
        return (X @ self._planes > 0).astype(np.uint8)


def hamming_neighbors(codes, query_idx, k):
    dists = np.count_nonzero(codes != codes[query_idx], axis=1)
    dists[query_idx] = np.iinfo(dists.dtype).max
    return np.argsort(dists)[:k]
