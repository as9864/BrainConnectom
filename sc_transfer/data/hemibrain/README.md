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
python -m sctransfer.hemibrain --build
```

## Files

| File | Contents | Used by |
| --- | --- | --- |
| `circuits/<name>.npz` | Directed neuron-level subgraph of one circuit: synapses located inside the listed ROIs, summed per neuron pair, connections with **≥ 3 synapses** only. Arrays: `pre_idx`, `post_idx`, `weight`, `body_ids`, `types`, `rois`. | `sctransfer` (fly side of the cross-species comparison) |

| Circuit | ROIs (right hemisphere) | Neurons | Connections |
| --- | --- | --- | --- |
| `mushroom_body` | CA, PED, aL, a'L, bL, b'L, gL | 2,803 | 152,245 |
| `central_complex` | FB, EB, PB, NO, AB | 2,847 | 206,594 |
| `lateral_horn` | LH | 2,383 | 34,771 |
| `antennal_lobe` | AL | 648 | 32,050 |
| `lateral_complex` | LAL, CRE | 3,080 | 69,832 |

Notes:
- The hemibrain covers mostly the right hemisphere; neurons are included if they have a
  qualifying connection inside the circuit's ROIs, so a circuit also contains input/output
  neurons whose somata lie elsewhere.
- Per-ROI counts come from `traced-roi-connections.csv`, which only covers "primary" ROIs;
  synapses outside any primary ROI are not counted.
- The antennal lobe is only partially contained in the hemibrain volume.
