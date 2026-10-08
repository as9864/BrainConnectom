"""FC -> SC decoders: a supervised baseline, and a prior-regularized variant
that nudges the baseline's prediction toward the cross-species topological
prior built in invertebrate_prior.py.
"""
import numpy as np
from sklearn.linear_model import Ridge


def upper_tri_indices(n):
    return np.triu_indices(n, k=1)


def vectorize(M):
    return M[upper_tri_indices(M.shape[0])]


def devectorize(vec, n):
    M = np.zeros((n, n))
    M[upper_tri_indices(n)] = vec
    return M + M.T


def train_baseline_decoder(train_pairs, alpha=5.0):
    """train_pairs: list of {"sc":.., "fc":..}. Fits Ridge regression mapping
    vectorized FC (upper triangle) -> vectorized SC (upper triangle).
    """
    X = np.array([vectorize(p["fc"]) for p in train_pairs])
    Y = np.array([vectorize(p["sc"]) for p in train_pairs])
    model = Ridge(alpha=alpha)
    model.fit(X, Y)
    return model


def predict_sc(model, fc, n_regions):
    vec = model.predict(vectorize(fc)[None, :])[0]
    vec = np.clip(vec, 0, None)  # structural edge weights are non-negative
    return devectorize(vec, n_regions)


def _reshape_toward_target_hubness(SC, target_cv, blend=1.0):
    """Reshape (not just rescale) the predicted connectome's hub structure so
    the *inequality* of node strengths (coefficient of variation = std/mean)
    moves toward the prior's target. CV is scale-invariant, so this is safe
    to compare across data sources measured in completely different raw
    units (invertebrate synapse counts vs. arbitrary synthetic SC weights) -
    a naive absolute-scale match does not survive that unit mismatch (see
    docs/ARCHITECTURE.md). Concretely: nodes whose strength should grow
    become more hub-like, others shrink toward the mean, and each edge is
    rescaled by the geometric mean of its two endpoints' adjustment - i.e.
    this is a hub-strength operationalization of the "rich-club organization
    is conserved across species" prior, not an arbitrary transform.
    """
    strength = SC.sum(axis=0) + SC.sum(axis=1)
    strength = np.maximum(strength, 1e-8)
    mean_s = strength.mean()
    cur_cv = strength.std() / mean_s if mean_s > 0 else 0.0
    if cur_cv < 1e-8:
        return SC.copy()
    stretch = 1.0 + blend * (target_cv / cur_cv - 1.0)
    target_strength = np.clip(mean_s + (strength - mean_s) * stretch, 1e-8, None)
    node_scale = target_strength / strength
    edge_scale = np.sqrt(np.outer(node_scale, node_scale))
    return np.clip(SC * edge_scale, 0, None)


def prior_regularized_predict(model, fc, n_regions, prior_stats, alpha_blend=0.5):
    """Baseline prediction, then reshaped toward the prior's target hub
    inequality (coefficient of variation of node strength). alpha_blend in
    [0, 1]: 0 = pure baseline, 1 = fully reshaped toward the prior's CV.
    """
    baseline = predict_sc(model, fc, n_regions)
    mean_s = prior_stats["strength_mean"]["mean"]
    std_s = prior_stats["strength_std"]["mean"]
    target_cv = std_s / mean_s if mean_s > 0 else 0.0
    return _reshape_toward_target_hubness(baseline, target_cv, blend=alpha_blend)
