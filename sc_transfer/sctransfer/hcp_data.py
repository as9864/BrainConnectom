"""Real human (HCP) structural/functional connectomes, two ways.

1. Group-level, no account needed: the ENIGMA Toolbox (Lariviere et al. 2021,
   Nat Methods; BSD-3) ships normative HCP connectivity matrices - SC from
   MRtrix3 + SIFT2 tractography, group-averaged with distance-dependent
   consensus thresholding and log-transformed; FC as the group mean of
   z-transformed resting-state correlations, negatives set to 0 - for six
   cortical parcellations. `load_group_connectome()` downloads them into the
   gitignored data/hcp_enigma/ cache on first use. One matrix per
   parcellation, so these support descriptive comparisons, not per-subject
   FC->SC decoding.

2. Individual subjects, bring your own: HCP requires every user to register
   on ConnectomeDB and accept its Open Access Data Use Terms, so per-subject
   matrices are never downloaded or committed here. Process or obtain them
   yourself and point `load_individual_cohort()` at them (formats below).

Both return SC with non-negative weights (log-transformed inputs are mapped
back with exp so that ranking edges by strength - e.g. for density
thresholding - stays correct).
"""
import urllib.request
from pathlib import Path

import numpy as np

ENIGMA_URL = ("https://raw.githubusercontent.com/MICA-MNI/ENIGMA/master/"
              "enigmatoolbox/datasets/matrices/hcp_connectivity/")
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "hcp_enigma" / "raw"
PARCELLATIONS = {  # name -> ENIGMA file suffix
    "aparc": "",  # Desikan-Killiany, 68 cortical regions
    "schaefer_100": "_schaefer_100",
    "schaefer_200": "_schaefer_200",
    "schaefer_300": "_schaefer_300",
    "schaefer_400": "_schaefer_400",
    "glasser_360": "_glasser_360",
}
MATRIX_EXTS = (".npy", ".csv", ".txt")


def _fetch(name):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / name
    if not path.exists():
        urllib.request.urlretrieve(ENIGMA_URL + name, path)
    return path


def _sc_from_log(sc_log):
    """ENIGMA SC is log(fiber density); zeros mean 'no edge'. Undo the log so
    weights are positive and order-preserving."""
    sc = np.where(sc_log != 0, np.exp(sc_log), 0.0)
    np.fill_diagonal(sc, 0)
    return sc


def load_group_connectome(parcellation="aparc"):
    """Group-average HCP (SC, FC, labels) for one parcellation, or None if the
    files can't be downloaded (offline / host not allowed)."""
    suffix = PARCELLATIONS[parcellation]
    try:
        sc_log = np.loadtxt(_fetch(f"strucMatrix_ctx{suffix}.csv"), delimiter=",")
        fc = np.loadtxt(_fetch(f"funcMatrix_ctx{suffix}.csv"), delimiter=",")
        labels = np.loadtxt(_fetch(f"strucLabels_ctx{suffix}.csv"), delimiter=",", dtype=str)
    except Exception as exc:  # noqa: BLE001 - any network error means "not available"
        print(f"[hcp_data] could not load ENIGMA HCP matrices for {parcellation} ({exc})")
        return None
    np.fill_diagonal(fc, 0)
    return _sc_from_log(sc_log), fc, np.atleast_1d(labels)


def _read_matrix(path):
    if path.suffix == ".npy":
        return np.load(path)
    return np.loadtxt(path, delimiter="," if path.suffix == ".csv" else None)


def _find(subject_dir, stem):
    for ext in MATRIX_EXTS:
        p = subject_dir / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def load_individual_cohort(path, sc_is_log=False):
    """Per-subject SC/FC pairs you provide. Two accepted layouts:

      cohort.npz              arrays `sc` and `fc`, each (n_subjects, n, n);
                              optional `subject_ids`
      <dir>/<subject>/sc.{npy,csv,txt} and fc.{npy,csv,txt}

    Returns the same [{"sc", "fc", "subject"}] list as human_data.make_cohort().
    Matrices are symmetrized, diagonals zeroed, SC made non-negative.
    """
    path = Path(path)
    pairs = []
    if path.suffix == ".npz":
        d = np.load(path, allow_pickle=False)
        ids = d["subject_ids"] if "subject_ids" in d.files else np.arange(len(d["sc"]))
        pairs = [(str(s), sc, fc) for s, sc, fc in zip(ids, d["sc"], d["fc"])]
    elif path.is_dir():
        for sub in sorted(p for p in path.iterdir() if p.is_dir()):
            sc_p, fc_p = _find(sub, "sc"), _find(sub, "fc")
            if sc_p and fc_p:
                pairs.append((sub.name, _read_matrix(sc_p), _read_matrix(fc_p)))
    else:
        raise FileNotFoundError(f"{path}: expected a .npz file or a directory of subject folders")
    if not pairs:
        raise ValueError(f"{path}: no subjects with both sc and fc found")

    n = pairs[0][1].shape[0]
    cohort = []
    for subject, sc, fc in pairs:
        if sc.shape != (n, n) or fc.shape != (n, n):
            raise ValueError(f"subject {subject}: expected {n}x{n} SC and FC, got {sc.shape} and {fc.shape}")
        sc = _sc_from_log(sc) if sc_is_log else np.clip(sc, 0, None)
        sc = (sc + sc.T) / 2
        fc = (fc + fc.T) / 2
        np.fill_diagonal(sc, 0)
        np.fill_diagonal(fc, 0)
        cohort.append({"sc": sc, "fc": fc, "subject": subject})
    print(f"[hcp_data] loaded {len(cohort)} subjects x {n} regions from {path}")
    return cohort
