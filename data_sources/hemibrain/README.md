# Drosophila hemibrain v1.2 — derived connectivity

These files are **derived** from the public compact export of the FlyEM hemibrain v1.2
connectome (Janelia Research Campus), not the raw export itself:

- Source: <https://storage.googleapis.com/hemibrain/v1.2/exported-traced-adjacencies-v1.2.tar.gz>
  (all traced neurons, neuron-to-neuron synapse counts, and synapse counts per brain region)
- License: **CC BY 4.0** — see <https://www.janelia.org/project-team/flyem/hemibrain>
- Citation: Scheffer, L.K. et al. (2020). A connectome and analysis of the adult *Drosophila*
  central brain. *eLife* 9, e57443. doi:10.7554/eLife.57443

Regenerate everything (downloads ~46 MB into the gitignored `raw/` folder):

```bash
python -m flyhash_experiment.hemibrain --build
```

## Files

| File | Contents | Used by |
| --- | --- | --- |
| `pn_kc.npz` | Projection neuron → Kenyon cell synapse counts from the whole-neuron connection table. PNs = type matching `.*PN.*`, KCs = type matching `^KC.*`, keeping only neurons in at least one PN→KC connection (1802 KCs × 157 PNs, 12,426 connections). | `flyhash_experiment` (`flyhash_real_hemibrain`) |

The neuropil circuit subgraphs derived from the same export now live in `sc_transfer/data/hemibrain/`.

Note: the hemibrain covers mostly the right hemisphere of the central brain.
