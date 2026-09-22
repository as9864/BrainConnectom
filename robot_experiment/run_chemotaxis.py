"""Odor-tracking with a fixed reservoir + ES-trained readout.

Same recipe as robot_experiment.evolve (real C. elegans connectome vs density-matched
random reservoir, only Wout trained), but on the 2D two-antenna chemotaxis task, where
"success" (reaching the food) is directly measurable. Two hand-written references frame
the numbers: random actions (floor) and a Braitenberg-style controller that turns toward
the stronger antenna (a simple hand-coded ceiling).

Usage:
    python -m robot_experiment.run_chemotaxis --n-seeds 3
"""
import argparse
from pathlib import Path

import gymnasium as gym
import numpy as np

import robot_experiment.chemotaxis  # noqa: F401  (registers Chemotaxis-v0)
from reservoir_experiment import connectome
from robot_experiment.evolve import evolve_readout
from robot_experiment.policy import ReservoirPolicy

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def braitenberg_act(obs):
    left, right = obs
    return np.array([1.0, np.clip(8.0 * (left - right) / (left + right + 1e-9), -1, 1)])


def run_episode(env, act_fn, seed, max_steps=200):
    obs, _ = env.reset(seed=seed)
    path = [env.unwrapped.pos.copy()]
    info = {"success": False, "distance": float(env.unwrapped._dist)}
    for _ in range(max_steps):
        obs, _, term, trunc, info = env.step(act_fn(obs))
        path.append(env.unwrapped.pos.copy())
        if term or trunc:
            break
    return np.array(path), env.unwrapped.food.copy(), info


def score(env, act_fn, seeds):
    infos = [run_episode(env, act_fn, s)[2] for s in seeds]
    return np.mean([i["success"] for i in infos]), np.mean([i["distance"] for i in infos])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-id", default="Chemotaxis-v0", choices=["Chemotaxis-v0", "ChemotaxisContrast-v0"])
    parser.add_argument("--rho", type=float, default=0.9)
    parser.add_argument("--leak", type=float, default=0.3)
    parser.add_argument("--generations", type=int, default=100)
    parser.add_argument("--population", type=int, default=32)
    parser.add_argument("--sigma", type=float, default=0.02)
    parser.add_argument("--lr", type=float, default=0.02)
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--n-eval-seeds", type=int, default=8)
    parser.add_argument("--n-seeds", type=int, default=3, help="independent training runs per variant")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    eval_seeds = np.arange(args.n_eval_seeds) + 1000
    test_seeds = list(range(5000, 5050))

    W_real_raw = connectome.build_weight_matrix(layers=(2, 3))
    n = W_real_raw.shape[0]
    density = np.count_nonzero(W_real_raw) / (n * n - n)
    W_real = connectome.rescale_spectral_radius(W_real_raw, args.rho)

    env = gym.make(args.env_id)
    ref_env = gym.make("Chemotaxis-v0")  # Braitenberg reference always reads raw antenna values
    rng = np.random.default_rng(0)
    refs = {
        "random_actions": score(ref_env, lambda o: rng.uniform(-1, 1, 2), test_seeds),
        "braitenberg": score(ref_env, braitenberg_act, test_seeds),
    }

    results = {"real_connectome": [], "random_reservoir": []}
    histories = {"real_connectome": [], "random_reservoir": []}
    trained = {}
    for seed in range(args.n_seeds):
        variants = {
            "real_connectome": W_real,
            "random_reservoir": connectome.rescale_spectral_radius(
                connectome.null_model_dense_gaussian(n, density, seed=seed), args.rho
            ),
        }
        for name, W in variants.items():
            print(f"\n=== {name}, seed {seed} ===")
            theta, history = evolve_readout(
                W, args.env_id, 2, seed, args.leak, args.generations, args.population,
                args.sigma, args.lr, args.max_steps, eval_seeds, log_every=25,
            )
            policy = ReservoirPolicy(W, 2, leak=args.leak, seed=seed)
            policy.Wout = theta

            succ, dists = [], []
            for s in test_seeds:
                policy.reset()
                info = run_episode(env, policy.act, s)[2]
                succ.append(info["success"])
                dists.append(info["distance"])
            results[name].append((np.mean(succ), np.mean(dists)))
            histories[name].append(history)
            trained[(name, seed)] = policy
            print(f"  test success={np.mean(succ):.2f}  final distance={np.mean(dists):.2f}")

    print("\n=== summary (50 unseen test episodes) ===")
    for name, (rate, dist) in refs.items():
        print(f"{name:17s}: success={rate:.2f}  final_dist={dist:.2f}")
    for name, runs in results.items():
        rates = [r[0] for r in runs]
        dists = [r[1] for r in runs]
        print(f"{name:17s}: success={np.mean(rates):.2f} +/- {np.std(rates):.2f}  "
              f"final_dist={np.mean(dists):.2f} +/- {np.std(dists):.2f}   (per-seed success: {np.round(rates, 2).tolist()})")

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for name, hs in histories.items():
        arr = np.array(hs)
        axes[0].plot(arr.mean(axis=0), label=name)
        axes[0].fill_between(range(arr.shape[1]), arr.min(axis=0), arr.max(axis=0), alpha=0.2)
    axes[0].set_xlabel("generation")
    axes[0].set_ylabel("mean population fitness")
    axes[0].set_title("learning curves (band = min/max over seeds)")
    axes[0].legend()

    colors = {"real_connectome": "tab:blue", "random_reservoir": "tab:orange"}
    for k, s in enumerate(test_seeds[:4]):
        _, food, _ = run_episode(ref_env, braitenberg_act, s)
        axes[1].scatter(*food, marker="*", s=200, color=f"C{k+2}", zorder=3)
        for name in colors:
            policy = trained[(name, 0)]
            policy.reset()
            path, _, _ = run_episode(env, policy.act, s)
            axes[1].plot(path[:, 0], path[:, 1], color=colors[name], alpha=0.8,
                         label=name if k == 0 else None)
        axes[1].plot(0, 0, "ko", ms=4)
    axes[1].set_aspect("equal")
    axes[1].set_title("trained trajectories from origin (stars = food, 4 unseen episodes)")
    axes[1].legend()
    fig.tight_layout()
    fig_path = RESULTS_DIR / f"chemotaxis_results_{args.env_id}.png"
    fig.savefig(fig_path, dpi=150)
    print(f"\nSaved plot to {fig_path}")


if __name__ == "__main__":
    main()
