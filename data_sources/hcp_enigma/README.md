# Human Connectome Project — group-average connectomes (via ENIGMA Toolbox)

Nothing in this folder is committed except this README. `sc_prior_experiment/hcp_data.py`
downloads the matrices into the gitignored `raw/` subfolder on first use.

- **Source**: ENIGMA Toolbox, `enigmatoolbox/datasets/matrices/hcp_connectivity/` in
  <https://github.com/MICA-MNI/ENIGMA> (code and bundled data: BSD 3-Clause).
- **Underlying data**: WU-Minn Human Connectome Project, unrelated healthy adults. HCP Open Access
  data and data derived from it are governed by the
  [HCP Open Access Data Use Terms](https://www.humanconnectome.org/study/hcp-young-adult/data-use-terms):
  register on ConnectomeDB and accept them before using these matrices, and acknowledge HCP in any
  publication.
- **Cite**: Larivière, S. et al. (2021). The ENIGMA Toolbox: multiscale neural contextualization of
  multisite neuroimaging datasets. *Nat Methods* 18, 698–700. doi:10.1038/s41592-021-01186-4

## What the matrices are (from the ENIGMA documentation)

| | Structural (SC) | Functional (FC) |
| --- | --- | --- |
| Method | MRtrix3 anatomically constrained tractography, 40M streamlines, SIFT2 weighting | Pairwise correlation of resting-state time series |
| Group step | Distance-dependent consensus thresholding (keeps the edge-length distribution) | Subject matrices z-transformed and averaged |
| Values | log(fiber density); `hcp_data.py` maps back with exp so weights are positive | Unthresholded, negative correlations set to 0 |

Parcellations (cortex only): Desikan-Killiany (`aparc`, 68), Schaefer 100/200/300/400, Glasser 360.

**Limitation**: one group matrix per parcellation — enough for descriptive comparisons
(`run_transfer.py --human hcp_group`, Part 1), not for per-subject FC→SC decoding (Part 2).
For that, see `docs/hcp_data_guide.md`.
