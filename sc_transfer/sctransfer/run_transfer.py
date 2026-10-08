"""How far do wiring principles conserved across species transfer, quantitatively?

Direction A of the project (docs/methodology_transferability.md). Instead of
asking "does an invertebrate prior improve FC->SC reconstruction?" in
isolation, place the invertebrate prior on a ladder of prior sources, all
expressed in the same null-normalized statistics (normalized.py):

  null          ER-randomized invertebrate graphs        - lower bound
  invertebrate  C. elegans + fly hemibrain circuits       - the question
  human         the training cohort's own SCs              - practical upper bound
  oracle        the held-out subject's true SC             - theoretical upper bound

Part 1 (descriptive): where do the invertebrate statistics fall relative to
the human distribution? z = (mean_invertebrate - mean_human) / std_human.

Part 2 (utility): from the baseline FC->SC prediction, build a small family
of candidate reconstructions (edge density x hub strength). Each prior
source picks the candidate whose normalized statistics are closest to it;
we then score the pick against the true SC. Transfer index
    TI = (M_invertebrate - M_null) / (M_oracle - M_null)
is the fraction of the oracle's gain over the null the invertebrate prior
recovers (1 = as good as knowing the answer, 0 = no better than random).

Usage:
    python -m sctransfer.run_transfer --n-subjects 60
    python -m sctransfer.run_transfer --density 0.04   # density-matched sensitivity run
    python -m sctransfer.run_transfer --human hcp_group   # real HCP group SC, Part 1 only
    python -m sctransfer.run_transfer --human hcp_cohort --hcp-cohort path/to/cohort.npz
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from sctransfer import hemibrain
from sctransfer.celegans import build_weight_matrix as celegans_weight_matrix
from sctransfer import decoder, hcp_data, human_data
from sctransfer import normalized as N
from sctransfer.invertebrate_prior import FLY_SUBGRAPH_NODES, N_SUBSAMPLES_PER_GRAPH, SUBSAMPLE_FRAC
from sctransfer.run_pilot import edge_correlation
from sctransfer.topology import erdos_renyi_null, subsample_subgraph

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
CANDIDATE_DENSITIES = [0.06, 0.08, 0.10, 0.12, 0.15]
CANDIDATE_HUB_MULTIPLIERS = [0.75, 1.0, 1.33, 1.75, 2.5]
SOURCES = ["null", "invertebrate", "human", "oracle"]


def _usable(W, density):
    """Density-matched runs only keep graphs dense enough to be thresholded down."""
    return density is None or N.density_of(N.binarize(W)) >= 0.95 * density


def invertebrate_samples(density, n_nulls):
    """Returns ({group_name: [signature, ...]}, {group_name: [null signature, ...]})."""
    graphs = {"celegans": []}
    W = celegans_weight_matrix()
    graphs["celegans"].append(W)
    for i in range(N_SUBSAMPLES_PER_GRAPH):
        graphs["celegans"].append(subsample_subgraph(W, frac_nodes=SUBSAMPLE_FRAC, seed=100 + i))
    for c, name in enumerate(hemibrain.available_circuits()):
        Wc = hemibrain.load_circuit(name)
        frac = min(1.0, FLY_SUBGRAPH_NODES / Wc.shape[0])
        graphs[f"fly_{name}"] = [subsample_subgraph(Wc, frac_nodes=frac, seed=(200 + c) * 100 + i)
                                 for i in range(N_SUBSAMPLES_PER_GRAPH + 1)]

    bio, null = {}, {}
    for group, Ws in graphs.items():
        Ws = [W for W in Ws if _usable(W, density)]
        if not Ws:
            print(f"[transfer] {group}: excluded (sparser than target density {density})")
            continue
        bio[group] = [N.normalized_signature(W, density, n_nulls, seed=i) for i, W in enumerate(Ws)]
        null[group] = [N.normalized_signature(erdos_renyi_null(W, seed=i), density, n_nulls, seed=i)
                       for i, W in enumerate(Ws)]
        print(f"[transfer] {group}: {len(Ws)} graphs, native density "
              f"{np.mean([s['density'] for s in bio[group]]):.3f}")
    return bio, null


def threshold_weighted(W, density):
    A = N.binarize(W, density)
    return W * A


def candidate_family(P):
    s = P.sum(0) + P.sum(1)
    cv = s.std() / s.mean() if s.mean() > 0 else 0.0
    for m in CANDIDATE_HUB_MULTIPLIERS:
        R = decoder._reshape_toward_target_hubness(P, cv * m, blend=1.0)
        for d in CANDIDATE_DENSITIES:
            yield {"hub_mult": m, "density": d, "W": threshold_weighted(R, d)}


def _print_ti(df, metric, by, sources, label=None):
    """Transfer index, reported only when the oracle reliably beats the null
    (paired t-statistic over subjects > 2) by a non-negligible margin (gap at
    least a quarter of the null's across-subject std); otherwise the
    denominator is noise or tiny and the ratio meaningless."""
    piv = df.pivot_table(index="subject", columns=by, values=metric)
    diff = piv["oracle"] - piv["null"]
    t = diff.mean() / (diff.std(ddof=1) / np.sqrt(len(diff)) + 1e-12)
    name = label or metric
    gap = diff.mean()
    if abs(t) < 2:
        print(f"  {name:16s} TI undefined (oracle vs null not distinguishable, t={t:+.1f})")
        return
    if abs(gap) < 0.25 * piv["null"].std(ddof=1):
        print(f"  {name:16s} TI undefined (oracle-null gap {gap:+.4f} is practically negligible, "
              f"< 0.25 x null std)")
        return
    parts = [f"{src} {(piv[src] - piv['null']).mean() / gap:+.2f}" for src in sources]
    print(f"  {name:16s} TI: " + ", ".join(parts) + f"   (oracle vs null t={t:+.1f})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-subjects", type=int, default=60)
    parser.add_argument("--n-regions", type=int, default=90)
    parser.add_argument("--train-frac", type=float, default=0.7)
    parser.add_argument("--density", type=float, default=None,
                        help="threshold every graph to this density before computing statistics "
                             "(default: each graph's native density)")
    parser.add_argument("--n-nulls", type=int, default=N.N_NULLS_DEFAULT)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--human", choices=["synthetic", "hcp_group", "hcp_cohort"], default="synthetic",
                        help="synthetic cohort; real HCP group-average SC from the ENIGMA Toolbox "
                             "(descriptive Part 1 only); or your own per-subject HCP SC/FC pairs")
    parser.add_argument("--hcp-cohort", help="--human hcp_cohort: .npz or directory, see hcp_data.py")
    parser.add_argument("--sc-is-log", action="store_true", help="--human hcp_cohort: SC weights are log-transformed")
    parser.add_argument("--parcellations", nargs="+", default=list(hcp_data.PARCELLATIONS),
                        help="--human hcp_group: which parcellations to use")
    args = parser.parse_args()
    RESULTS_DIR.mkdir(exist_ok=True)
    tag = f"{args.human}_" + ("native" if args.density is None else f"d{args.density:g}")

    print("=== Invertebrate and null signatures ===")
    bio, null = invertebrate_samples(args.density, args.n_nulls)

    print("\n=== Human connectomes ===")
    human_groups = {}
    if args.human == "hcp_group":
        train = test = None
        for parc in args.parcellations:
            loaded = hcp_data.load_group_connectome(parc)
            if loaded is None:
                continue
            sc = loaded[0]
            # one group matrix per parcellation: add node subsamples, as for the invertebrates
            graphs = [sc] + [subsample_subgraph(sc, frac_nodes=SUBSAMPLE_FRAC, seed=300 + i)
                             for i in range(N_SUBSAMPLES_PER_GRAPH)]
            graphs = [W for W in graphs if _usable(W, args.density)]
            if not graphs:
                print(f"[transfer] human_{parc}: excluded (sparser than target density {args.density})")
                continue
            human_groups[f"human_{parc}"] = [N.normalized_signature(W, args.density, args.n_nulls, seed=i)
                                             for i, W in enumerate(graphs)]
            print(f"[transfer] human_{parc}: {sc.shape[0]} regions (HCP group average, ENIGMA), "
                  f"native density {N.density_of(N.binarize(sc)):.3f}")
        if not human_groups:
            raise SystemExit("No HCP group matrices available (see hcp_data.py).")
        human_sigs = sum(human_groups.values(), [])
    else:
        if args.human == "hcp_cohort":
            if not args.hcp_cohort:
                raise SystemExit("--human hcp_cohort needs --hcp-cohort PATH")
            cohort = hcp_data.load_individual_cohort(args.hcp_cohort, sc_is_log=args.sc_is_log)
        else:
            cohort = human_data.make_cohort(n_subjects=args.n_subjects, n_regions=args.n_regions, seed=args.seed)
        split = int(len(cohort) * args.train_frac)
        train, test = cohort[:split], cohort[split:]
        human_sigs = [N.normalized_signature(p["sc"], args.density, args.n_nulls, seed=i)
                      for i, p in enumerate(train)]
    n_regions = None if train is None else train[0]["sc"].shape[0]

    priors = {
        "null": N.aggregate_species([sum((v for k, v in null.items() if k == "celegans"), []),
                                     sum((v for k, v in null.items() if k.startswith("fly_")), [])]),
        "invertebrate": N.aggregate_species([bio.get("celegans", []),
                                             sum((v for k, v in bio.items() if k.startswith("fly_")), [])]),
        "human": N.aggregate(human_sigs),
    }

    # ---- Part 1: descriptive ----
    rows = []
    groups = {**{k: v for k, v in bio.items()}, **human_groups, "human": human_sigs,
              "null (ER of invertebrates)": sum(null.values(), [])}
    for group, sigs in groups.items():
        agg = N.aggregate(sigs)
        rows.append({"group": group, "n": len(sigs), "density": np.mean([s["density"] for s in sigs]),
                     **{f"{k}_mean": agg[k]["mean"] for k in N.STATS},
                     **{f"{k}_std": agg[k]["std"] for k in N.STATS}})
    desc = pd.DataFrame(rows)
    desc.to_csv(RESULTS_DIR / f"transfer_descriptive_{tag}.csv", index=False)

    print("\n=== Part 1: null-normalized statistics (1 = random) ===")
    print(desc[["group", "n", "density"] + [f"{k}_mean" for k in N.STATS]].round(3).to_string(index=False))
    print("\nInvertebrate vs human, z = (invertebrate - human) / human std:")
    for k in N.STATS:
        z = (priors["invertebrate"][k]["mean"] - priors["human"][k]["mean"]) / priors["human"][k]["std"]
        same_side = np.sign(priors["invertebrate"][k]["mean"] - 1) == np.sign(priors["human"][k]["mean"] - 1)
        print(f"  {k:16s} invertebrate={priors['invertebrate'][k]['mean']:.3f}  "
              f"human={priors['human'][k]['mean']:.3f}  z={z:+.1f}  "
              f"same direction vs random: {'yes' if same_side else 'no'}")

    if train is None:
        print("\nPart 2 (FC->SC utility) skipped: group-average data has no per-subject SC/FC pairs. "
              "Use --human hcp_cohort with your own HCP subjects.")
        print(f"Saved results/transfer_descriptive_{tag}.csv")
        return

    # ---- Part 2: utility ----
    print(f"\n=== Part 2: prior utility on {len(test)} held-out subjects ===")
    model = decoder.train_baseline_decoder(train)
    util_rows, stat_rows = [], []
    for i, subj in enumerate(test):
        true_sig = N.normalized_signature(subj["sc"], args.density, args.n_nulls, seed=i)
        oracle = {k: {"mean": true_sig[k], "std": priors["human"][k]["std"]} for k in N.STATS}
        P = decoder.predict_sc(model, subj["fc"], n_regions)
        cands = list(candidate_family(P))
        for c in cands:
            c["sig"] = N.normalized_signature(c["W"], args.density, max(2, args.n_nulls // 2), seed=i)

        def score(label, W, sig, extra=None):
            util_rows.append({"subject": i, "condition": label,
                              "edge_corr": edge_correlation(W, subj["sc"]),
                              "norm_stat_dist": N.prior_distance(sig, oracle, scale=priors["human"]),
                              **(extra or {})})

        for k in N.STATS:  # which individual principles transfer?
            for src, prior in [*priors.items(), ("oracle", oracle)]:
                best = min(cands, key=lambda c: N.prior_distance(c["sig"], prior, scale=priors["human"], keys=[k]))
                err = abs(best["sig"][k] - true_sig[k]) / priors["human"][k]["std"]
                stat_rows.append({"subject": i, "stat": k, "source": src, "abs_err_in_human_std": err})

        score("baseline", P, N.normalized_signature(P, args.density, max(2, args.n_nulls // 2), seed=i))
        for src, prior in [*priors.items(), ("oracle", oracle)]:
            best = min(cands, key=lambda c: N.prior_distance(c["sig"], prior, scale=priors["human"]))
            score(src, best["W"], best["sig"], {"picked_density": best["density"], "picked_hub_mult": best["hub_mult"]})
        print(f"  subject {i + 1}/{len(test)}")

    util = pd.DataFrame(util_rows)
    util.to_csv(RESULTS_DIR / f"transfer_utility_{tag}.csv", index=False)
    summary = util.groupby("condition")[["edge_corr", "norm_stat_dist"]].agg(["mean", "std"])
    summary = summary.reindex(["baseline"] + SOURCES)
    print("\n" + summary.round(4).to_string())
    picks = util[util.condition != "baseline"].groupby("condition")[["picked_density", "picked_hub_mult"]].mean()
    print("\nAverage picked candidate:\n" + picks.reindex(SOURCES).round(3).to_string())

    print("\nTransfer index TI = (source - null) / (oracle - null), "
          "only where oracle beats null (paired t > 2):")
    for metric in ["edge_corr", "norm_stat_dist"]:
        _print_ti(util, metric, "condition", ["invertebrate", "human"])

    stats_df = pd.DataFrame(stat_rows)
    stats_df.to_csv(RESULTS_DIR / f"transfer_per_stat_{tag}.csv", index=False)
    print("\n=== Which principles transfer? One statistic at a time ===")
    print("(error of the picked candidate on that statistic, in units of the human cohort's std)")
    table = stats_df.groupby(["stat", "source"])["abs_err_in_human_std"].mean().unstack()[SOURCES]
    print(table.round(2).to_string())
    for k in N.STATS:
        _print_ti(stats_df[stats_df.stat == k], "abs_err_in_human_std", "source", ["invertebrate", "human"], label=k)
    print(f"\nSaved results/transfer_{{descriptive,utility,per_stat}}_{tag}.csv")


if __name__ == "__main__":
    main()
