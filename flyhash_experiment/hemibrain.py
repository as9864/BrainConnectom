"""Real Drosophila hemibrain connectivity, without a neuPrint token.

Janelia publishes a compact export of the hemibrain v1.2 connectome (all
traced neurons, neuron-to-neuron synapse counts, and the same counts split by
brain region) as a public file on Google Cloud Storage, licensed CC BY 4.0.
This module turns that export into two small derived datasets that live in
data_sources/hemibrain/ and are committed to the repo, so every experiment
keeps running offline:

  pn_kc.npz          - projection neuron -> Kenyon cell synapse counts
                        (flyhash_experiment's "real" PN->KC wiring)
  circuits/<name>.npz - neuron-level directed subgraphs of well-defined
                        neuropils (mushroom body, central complex, ...), used
                        by sc_prior_experiment as real fly wiring diagrams

Regenerate them from the public export with:
    python -m flyhash_experiment.hemibrain --build
"""
import argparse
import tarfile
import urllib.request
from pathlib import Path

import numpy as np

EXPORT_URL = "https://storage.googleapis.com/hemibrain/v1.2/exported-traced-adjacencies-v1.2.tar.gz"
DATA_DIR = Path(__file__).resolve().parent.parent / "data_sources" / "hemibrain"
RAW_DIR = DATA_DIR / "raw"  # gitignored download cache
PN_KC_FILE = DATA_DIR / "pn_kc.npz"
CIRCUIT_DIR = DATA_DIR / "circuits"

# Right-hemisphere primary ROIs (the hemibrain is mostly the right half).
# Kept to compact, well-defined circuits: larger neuropils (SMP/SLP, AVLP/PVLP)
# are 8k+ neurons, too big for the dense-matrix statistics in topology.py.
CIRCUITS = {
    "mushroom_body": ["CA(R)", "PED(R)", "aL(R)", "a'L(R)", "bL(R)", "b'L(R)", "gL(R)"],
    "central_complex": ["FB", "EB", "PB", "NO", "AB(R)"],
    "lateral_horn": ["LH(R)"],
    "antennal_lobe": ["AL(R)"],
    "lateral_complex": ["LAL(R)", "CRE(R)"],
}
# Connections with fewer synapses than this are dropped: 1-2 synapse contacts
# are the ones most affected by reconstruction noise in EM connectomes.
MIN_WEIGHT_DEFAULT = 3

PN_TYPE_REGEX = r".*PN.*"  # same criteria the neuPrint query used
KC_TYPE_REGEX = r"^KC.*"


def _download_export(raw_dir=RAW_DIR):
    raw_dir.mkdir(parents=True, exist_ok=True)
    tarball = raw_dir / "exported-traced-adjacencies-v1.2.tar.gz"
    if not tarball.exists():
        print(f"[hemibrain] downloading {EXPORT_URL} (~46 MB)")
        urllib.request.urlretrieve(EXPORT_URL, tarball)
    export_dir = raw_dir / "exported-traced-adjacencies-v1.2"
    if not export_dir.exists():
        with tarfile.open(tarball) as tf:
            tf.extractall(raw_dir, filter="data")
    return export_dir


def build(export_dir=None, min_weight=MIN_WEIGHT_DEFAULT):
    """Derive pn_kc.npz and circuits/*.npz from the public export."""
    import pandas as pd

    export_dir = Path(export_dir) if export_dir else _download_export()
    neurons = pd.read_csv(export_dir / "traced-neurons.csv")
    types = neurons["type"].fillna("")
    type_of = dict(zip(neurons["bodyId"], types))

    total = pd.read_csv(export_dir / "traced-total-connections.csv")
    pn_ids = np.sort(neurons.loc[types.str.match(PN_TYPE_REGEX), "bodyId"].to_numpy())
    kc_ids = np.sort(neurons.loc[types.str.match(KC_TYPE_REGEX), "bodyId"].to_numpy())
    pk = total[total["bodyId_pre"].isin(pn_ids) & total["bodyId_post"].isin(kc_ids)]
    # Only keep PNs/KCs that take part in at least one PN->KC connection.
    pn_ids = np.sort(pk["bodyId_pre"].unique())
    kc_ids = np.sort(pk["bodyId_post"].unique())
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        PN_KC_FILE,
        kc_idx=np.searchsorted(kc_ids, pk["bodyId_post"].to_numpy()).astype(np.int32),
        pn_idx=np.searchsorted(pn_ids, pk["bodyId_pre"].to_numpy()).astype(np.int32),
        weight=pk["weight"].to_numpy().astype(np.uint16),
        kc_body_ids=kc_ids, pn_body_ids=pn_ids,
        kc_types=np.array([type_of[b] for b in kc_ids]),
        pn_types=np.array([type_of[b] for b in pn_ids]),
    )
    print(f"[hemibrain] PN->KC: {len(kc_ids)} KCs x {len(pn_ids)} PNs, {len(pk)} connections -> {PN_KC_FILE}")

    roi = pd.read_csv(export_dir / "traced-roi-connections.csv")
    CIRCUIT_DIR.mkdir(parents=True, exist_ok=True)
    for name, rois in CIRCUITS.items():
        edges = (roi[roi["roi"].isin(rois)]
                 .groupby(["bodyId_pre", "bodyId_post"])["weight"].sum().reset_index())
        edges = edges[(edges["weight"] >= min_weight) & (edges["bodyId_pre"] != edges["bodyId_post"])]
        body_ids = np.sort(pd.unique(pd.concat([edges["bodyId_pre"], edges["bodyId_post"]])))
        np.savez_compressed(
            CIRCUIT_DIR / f"{name}.npz",
            pre_idx=np.searchsorted(body_ids, edges["bodyId_pre"].to_numpy()).astype(np.int32),
            post_idx=np.searchsorted(body_ids, edges["bodyId_post"].to_numpy()).astype(np.int32),
            weight=edges["weight"].to_numpy().astype(np.uint16),
            body_ids=body_ids,
            types=np.array([type_of.get(b, "") for b in body_ids]),
            rois=np.array(rois),
            min_weight=np.int32(min_weight),
        )
        print(f"[hemibrain] circuit {name}: {len(body_ids)} neurons, {len(edges)} connections (>= {min_weight} synapses)")


def load_pn_kc():
    """(n_KC, n_PN) synapse-count matrix, or None if the derived file is missing."""
    if not PN_KC_FILE.exists():
        return None
    d = np.load(PN_KC_FILE)
    W = np.zeros((len(d["kc_body_ids"]), len(d["pn_body_ids"])))
    W[d["kc_idx"], d["pn_idx"]] = d["weight"]
    return W


def available_circuits():
    return sorted(p.stem for p in CIRCUIT_DIR.glob("*.npz"))


def load_circuit(name):
    """Directed neuron-level adjacency W[pre, post] = synapse count within the
    circuit's ROIs. Dense, so only use it on the compact circuits above.
    """
    d = np.load(CIRCUIT_DIR / f"{name}.npz")
    n = len(d["body_ids"])
    W = np.zeros((n, n))
    W[d["pre_idx"], d["post_idx"]] = d["weight"]
    return W


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--build", action="store_true", help="download the public export and rebuild derived files")
    parser.add_argument("--export-dir", help="use an already-extracted export directory instead of downloading")
    parser.add_argument("--min-weight", type=int, default=MIN_WEIGHT_DEFAULT)
    args = parser.parse_args()
    if args.build:
        build(args.export_dir, args.min_weight)
    else:
        W = load_pn_kc()
        print("PN->KC:", None if W is None else W.shape)
        for name in available_circuits():
            print(name, load_circuit(name).shape)


if __name__ == "__main__":
    main()
