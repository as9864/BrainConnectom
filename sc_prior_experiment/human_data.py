"""Human SC/FC cohort - synthetic placeholder for the 2-week pilot.

Real HCP S1200 structural (DTI tractography) + functional (resting-state
fMRI) connectome pairs need an account on ConnectomeDB and a preprocessing
pipeline neither of which fit in a 2-week sprint. Instead this module
generates a synthetic cohort with a modular, brain-like structural template
and simulates functional connectivity from simple constrained dynamics on
top of it, so the rest of the pipeline (decoder.py, run_experiment.py) can
be built and validated end to end today.

`make_cohort()` is the only function the rest of the pipeline depends on -
swap it for `load_hcp_cohort()` (stubbed below) once real data is available;
the (SC, FC) pair interface stays identical.
"""
import numpy as np

SPECTRAL_RADIUS_TARGET = 0.9


def make_group_template_sc(n_regions=90, n_communities=6, within_p=0.35, between_p=0.03, seed=0):
    """A weighted, symmetric, modular structural connectome template - a
    deliberately simplified stand-in for the community structure real
    cortical parcellations show (e.g. Schaefer atlas + resting-state
    networks), not a claim about real anatomy.
    """
    rng = np.random.default_rng(seed)
    community = rng.integers(0, n_communities, size=n_regions)
    W = np.zeros((n_regions, n_regions))
    for i in range(n_regions):
        for j in range(i + 1, n_regions):
            p = within_p if community[i] == community[j] else between_p
            if rng.random() < p:
                w = rng.lognormal(mean=0.0, sigma=0.6)
                W[i, j] = W[j, i] = w
    return W


def perturb_individual_sc(group_sc, seed=0, edge_noise_sigma=0.25, drop_frac=0.03, add_frac=0.01):
    """Subject-level structural connectome: same template, edges reweighted
    with multiplicative log-normal noise plus a small number of dropped/added
    edges, to imitate inter-subject variability around a group template.
    """
    rng = np.random.default_rng(seed)
    n = group_sc.shape[0]
    W = group_sc * rng.lognormal(mean=0.0, sigma=edge_noise_sigma, size=group_sc.shape)
    W = np.triu(W, 1)
    W = W + W.T

    nonzero = np.argwhere(np.triu(group_sc, 1) > 0)
    n_drop = int(len(nonzero) * drop_frac)
    if n_drop:
        idx = rng.choice(len(nonzero), size=n_drop, replace=False)
        for i, j in nonzero[idx]:
            W[i, j] = W[j, i] = 0.0

    zero = np.argwhere(np.triu(group_sc, 1) == 0)
    n_add = int(len(zero) * add_frac)
    if n_add:
        idx = rng.choice(len(zero), size=n_add, replace=False)
        for i, j in zero[idx]:
            w = rng.lognormal(mean=0.0, sigma=0.6)
            W[i, j] = W[j, i] = w
    return W


def simulate_fc_from_sc(SC, seed=0, n_timepoints=300, leak=0.4, noise_std=0.6):
    """Toy generative model of functional connectivity: constrained linear
    dynamics driven by the structural graph plus noise, in the same spirit
    as the leaky-integrator reservoir used in reservoir_experiment/reservoir.py.
    This is a simplification of large-scale neural-mass models (e.g. linear
    models relating SC eigenmodes to BOLD covariance), good enough to give
    the pipeline a non-trivial, structurally-grounded SC->FC relationship to
    invert - not a claim of biophysical accuracy.
    """
    rng = np.random.default_rng(seed)
    n = SC.shape[0]
    eigvals = np.linalg.eigvals(SC)
    rho = np.max(np.abs(eigvals))
    SC_norm = SC * (SPECTRAL_RADIUS_TARGET / rho) if rho > 0 else SC

    x = np.zeros(n)
    states = np.zeros((n_timepoints, n))
    for t in range(n_timepoints):
        noise = rng.normal(0, noise_std, size=n)
        x = (1 - leak) * x + leak * np.tanh(SC_norm @ x + noise)
        states[t] = x
    return np.corrcoef(states.T)


def make_cohort(n_subjects=40, n_regions=90, seed=0):
    """Returns a list of {"sc": ndarray, "fc": ndarray} pairs."""
    template = make_group_template_sc(n_regions=n_regions, seed=seed)
    cohort = []
    rng = np.random.default_rng(seed)
    for s in range(n_subjects):
        subj_seed = int(rng.integers(0, 2**31 - 1))
        sc = perturb_individual_sc(template, seed=subj_seed)
        fc = simulate_fc_from_sc(sc, seed=subj_seed)
        cohort.append({"sc": sc, "fc": fc})
    print(f"[human_data] synthetic cohort: {n_subjects} subjects x {n_regions} regions "
          f"(placeholder for real HCP S1200 SC/FC pairs)")
    return cohort


def load_hcp_cohort(*args, **kwargs):
    """Real-data replacement for make_cohort() - not implemented in this
    pilot. To wire in real data: download HCP S1200 diffusion tractography
    (SC) and resting-state fMRI correlation matrices (FC) per subject from
    ConnectomeDB (free account, no long approval wait), parcellate both with
    the same atlas, and return the same [{"sc":..., "fc":...}, ...] list
    shape that make_cohort() produces so no other file needs to change.
    """
    raise NotImplementedError(
        "HCP integration is out of scope for the 2-week pilot - see docstring "
        "for the interface make_cohort() already provides."
    )
