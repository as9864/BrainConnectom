"""Vision-driven (optic-flow) drone navigation with a fixed reservoir + ES-trained readout.

Same recipe as run_chemotaxis.py: real C. elegans connectome vs density-matched random
reservoir, only the linear readout is trained. Two hand-written references frame the
numbers: random actions (floor) and a simple potential-field controller (goal bearing
pulls it forward, ray proximity pushes it away -- a hand-coded ceiling).

Usage:
    python -m robot_experiment.run_dronenav --n-seeds 3
"""
import argparse
from pathlib import Path

import gymnasium as gym
import numpy as np

import robot_experiment.drone_nav  # noqa: F401  (registers DroneNav-v0)
from reservoir_experiment import connectome
from robot_experiment.evolve import evolve_readout
from robot_experiment.policy import ReservoirPolicy

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
ENV_ID = "DroneNav-v0"
N_RAYS = 5


def potential_field_act(obs, ray_angles, turn_gain=1.5, avoid_gain=2.5, brake_gain=1.5):
    prox = obs[:N_RAYS]
    sin_b, cos_b = obs[2 * N_RAYS:]
    turn = turn_gain * sin_b - avoid_gain * np.sum(prox * np.sign(ray_angles))
    thrust = 1.0 - brake_gain * prox.max()
    return np.array([np.clip(thrust, -1, 1), np.clip(turn, -1, 1)])


def run_episode(env, act_fn, seed, max_steps=150):
    obs, _ = env.reset(seed=seed)
    path = [env.unwrapped.pos.copy()]
    info = {"success": False, "collided": False, "distance": float(env.unwrapped._dist)}
    for _ in range(max_steps):
        obs, _, term, trunc, info = env.step(act_fn(obs))
        path.append(env.unwrapped.pos.copy())
        if term or trunc:
            break
    return np.array(path), env.unwrapped.goal.copy(), env.unwrapped.obstacles.copy(), info


def score(env, act_fn, seeds):
    infos = [run_episode(env, act_fn, s)[3] for s in seeds]
    return (np.mean([i["success"] for i in infos]), np.mean([i["collided"] for i in infos]),
            np.mean([i["distance"] for i in infos]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rho", type=float, default=0.9)
    parser.add_argument("--leak", type=float, default=0.3)
    parser.add_argument("--generations", type=int, default=150)
    parser.add_argument("--population", type=int, default=32)
    parser.add_argument("--sigma", type=float, default=0.02)
    parser.add_argument("--lr", type=float, default=0.02)
    parser.add_argument("--max-steps", type=int, default=150)
    parser.add_argument("--n-eval-seeds", type=int, default=8)
    parser.add_argument("--n-seeds", type=int, default=3)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    eval_seeds = np.arange(args.n_eval_seeds) + 1000
    test_seeds = list(range(5000, 5050))

    W_real_raw = connectome.build_weight_matrix(layers=(2, 3))
    n = W_real_raw.shape[0]
    density = np.count_nonzero(W_real_raw) / (n * n - n)
    W_real = connectome.rescale_spectral_radius(W_real_raw, args.rho)

    env = gym.make(ENV_ID)
    ray_angles = env.unwrapped.ray_angles
    rng = np.random.default_rng(0)
    refs = {
        "random_actions": score(env, lambda o: rng.uniform(-1, 1, 2), test_seeds),
        "potential_field": score(env, lambda o: potential_field_act(o, ray_angles), test_seeds),
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
                W, ENV_ID, 2, seed, args.leak, args.generations, args.population,
                args.sigma, args.lr, args.max_steps, eval_seeds, log_every=25,
            )
            policy = ReservoirPolicy(W, 2, leak=args.leak, seed=seed)
            policy.Wout = theta

            succ, coll, dists = [], [], []
            for s in test_seeds:
                policy.reset()
                info = run_episode(env, policy.act, s)[3]
                succ.append(info["success"])
                coll.append(info["collided"])
                dists.append(info["distance"])
            results[name].append((np.mean(succ), np.mean(coll), np.mean(dists)))
            histories[name].append(history)
            trained[(name, seed)] = policy
            print(f"  test success={np.mean(succ):.2f}  collision={np.mean(coll):.2f}  final_dist={np.mean(dists):.2f}")

    print("\n=== summary (50 unseen test episodes) ===")
    for name, (rate, coll, dist) in refs.items():
        print(f"{name:17s}: success={rate:.2f}  collision={coll:.2f}  final_dist={dist:.2f}")
    for name, runs in results.items():
        rates = [r[0] for r in runs]
        colls = [r[1] for r in runs]
        dists = [r[2] for r in runs]
        print(f"{name:17s}: success={np.mean(rates):.2f} +/- {np.std(rates):.2f}  "
              f"collision={np.mean(colls):.2f} +/- {np.std(colls):.2f}  "
              f"final_dist={np.mean(dists):.2f} +/- {np.std(dists):.2f}   (per-seed success: {np.round(rates, 2).tolist()})")

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for name, hs in histories.items():
        arr = np.array(hs)
        axes[0].plot(arr.mean(axis=0), label=name)
        axes[0].fill_between(range(arr.shape[1]), arr.min(axis=0), arr.max(axis=0), alpha=0.2)
    axes[0].set_xlabel("generation")
    axes[0].set_ylabel("mean population fitness")
    axes[0].set_title("learning curves (band = min/max over seeds)")
    axes[0].legend()

    colors = {"real_connectome": "tab:blue", "random_reservoir": "tab:orange"}
    s = test_seeds[0]
    _, goal, obstacles, _ = run_episode(env, lambda o: potential_field_act(o, ray_angles), s)
    for o in obstacles:
        axes[1].add_patch(plt.Circle(o, env.unwrapped.obstacle_radius, color="gray", alpha=0.5))
    axes[1].scatter(*goal, marker="*", s=250, color="green", zorder=3, label="goal")
    for name in colors:
        policy = trained[(name, 0)]
        policy.reset()
        path, _, _, info = run_episode(env, policy.act, s)
        axes[1].plot(path[:, 0], path[:, 1], color=colors[name], label=f"{name} ({'success' if info['success'] else 'fail'})")
    axes[1].plot(0, 0, "ko", ms=6, label="start")
    axes[1].set_xlim(-env.unwrapped.world_size, env.unwrapped.world_size)
    axes[1].set_ylim(-env.unwrapped.world_size, env.unwrapped.world_size)
    axes[1].set_aspect("equal")
    axes[1].set_title(f"trained trajectories, one unseen episode (seed {s})")
    axes[1].legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig_path = RESULTS_DIR / "dronenav_results.png"
    fig.savefig(fig_path, dpi=150)
    print(f"\nSaved plot to {fig_path}")


if __name__ == "__main__":
    main()
