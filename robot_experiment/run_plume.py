"""Turbulent plume tracking with a fixed reservoir + ES-trained readout.

Three reservoir conditions (only the linear readout is ever trained):
  - real_connectome  -- actual C. elegans chemical-synapse connectome (recurrent, has memory)
  - random_reservoir -- density-matched random recurrent reservoir (has memory)
  - no_memory        -- W=0, leak=1: the same readout-training setup but with the recurrent
                         term killed, so the policy is a purely reactive (memoryless) map from
                         the current observation to an action. This isolates whether *having
                         any fixed recurrent dynamics at all* matters for this task, before
                         asking whether the specific connectome structure matters.

References: random actions (floor) and a hand-coded surge-and-cast controller (Kennedy 1983
moth model) as a ceiling.

Usage:
    python -m robot_experiment.run_plume --n-seeds 3
"""
import argparse
from pathlib import Path

import gymnasium as gym
import numpy as np

import robot_experiment.plume_tracking  # noqa: F401  (registers Plume-v0)
from reservoir_experiment import connectome
from robot_experiment.evolve import evolve_readout
from robot_experiment.policy import ReservoirPolicy

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
ENV_ID = "Plume-v0"


class SurgeCastController:
    """Kennedy (1983) moth surge-and-cast: fly upwind while in odor contact, cast
    crosswind in a widening search when contact is lost, resume surging on re-contact."""

    def __init__(self, surge_thresh=15, cast_period=25, turn_gain=1.5, cast_gain=1.0):
        self.surge_thresh = surge_thresh
        self.cast_period = cast_period
        self.turn_gain = turn_gain
        self.cast_gain = cast_gain
        self.reset()

    def reset(self):
        self.since_hit = 999

    def act(self, obs):
        hit, sin_rel, cos_rel, _ = obs
        self.since_hit = 0 if hit > 0 else self.since_hit + 1
        if self.since_hit < self.surge_thresh:
            turn = self.turn_gain * sin_rel
            thrust = 1.0
        else:
            phase = 2 * np.pi * (self.since_hit - self.surge_thresh) / self.cast_period
            turn = self.cast_gain * np.sin(phase) + 0.3 * sin_rel
            thrust = 0.15  # slow down while casting so the search stays local, not a drifting spiral
        return np.array([np.clip(thrust, -1, 1), np.clip(turn, -1, 1)])


def run_episode(env, act_fn, seed, max_steps=300):
    obs, _ = env.reset(seed=seed)
    path = [env.unwrapped.pos.copy()]
    hits = 0
    info = {"success": False, "distance": float(env.unwrapped._dist)}
    for _ in range(max_steps):
        obs, _, term, trunc, info = env.step(act_fn(obs))
        path.append(env.unwrapped.pos.copy())
        hits += int(info["hit"])
        if term or trunc:
            break
    return np.array(path), env.unwrapped.source.copy(), info, hits, len(path)


def score(env, act_fn, seeds, reset_fn=None):
    succ, steps, hitrate = [], [], []
    for s in seeds:
        if reset_fn:
            reset_fn()
        _, _, info, hits, n = run_episode(env, act_fn, s)
        succ.append(info["success"])
        steps.append(n)
        hitrate.append(hits / n)
    return np.mean(succ), np.mean(steps), np.mean(hitrate)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rho", type=float, default=0.9)
    parser.add_argument("--leak", type=float, default=0.3)
    parser.add_argument("--generations", type=int, default=200)
    parser.add_argument("--population", type=int, default=32)
    parser.add_argument("--sigma", type=float, default=0.02)
    parser.add_argument("--lr", type=float, default=0.02)
    parser.add_argument("--max-steps", type=int, default=300)
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
    W_zero = np.zeros((n, n))

    env = gym.make(ENV_ID)
    rng = np.random.default_rng(0)
    sc = SurgeCastController()
    refs = {
        "random_actions": score(env, lambda o: rng.uniform(-1, 1, 2), test_seeds),
        "surge_and_cast": score(env, sc.act, test_seeds, reset_fn=sc.reset),
    }

    variant_names = ["real_connectome", "random_reservoir", "no_memory"]
    results = {k: [] for k in variant_names}
    histories = {k: [] for k in variant_names}
    trained = {}
    for seed in range(args.n_seeds):
        variants = {
            "real_connectome": (W_real, args.leak),
            "random_reservoir": (
                connectome.rescale_spectral_radius(
                    connectome.null_model_dense_gaussian(n, density, seed=seed), args.rho
                ),
                args.leak,
            ),
            "no_memory": (W_zero, 1.0),
        }
        for name, (W, leak) in variants.items():
            print(f"\n=== {name}, seed {seed} ===")
            theta, history = evolve_readout(
                W, ENV_ID, 2, seed, leak, args.generations, args.population,
                args.sigma, args.lr, args.max_steps, eval_seeds, log_every=25,
            )
            policy = ReservoirPolicy(W, 2, leak=leak, seed=seed)
            policy.Wout = theta

            succ, steps, hitrate = [], [], []
            for s in test_seeds:
                policy.reset()
                _, _, info, hits, n_steps = run_episode(env, policy.act, s, max_steps=args.max_steps)
                succ.append(info["success"])
                steps.append(n_steps)
                hitrate.append(hits / n_steps)
            results[name].append((np.mean(succ), np.mean(steps), np.mean(hitrate)))
            histories[name].append(history)
            trained[(name, seed)] = policy
            print(f"  test success={np.mean(succ):.2f}  steps={np.mean(steps):.1f}  hit_rate={np.mean(hitrate):.2f}")

    print("\n=== summary (50 unseen test episodes) ===")
    for name, (rate, steps, hitrate) in refs.items():
        print(f"{name:17s}: success={rate:.2f}  steps={steps:.1f}  hit_rate={hitrate:.2f}")
    for name, runs in results.items():
        rates = [r[0] for r in runs]
        steps_ = [r[1] for r in runs]
        hits_ = [r[2] for r in runs]
        print(f"{name:17s}: success={np.mean(rates):.2f} +/- {np.std(rates):.2f}  "
              f"steps={np.mean(steps_):.1f} +/- {np.std(steps_):.1f}  "
              f"hit_rate={np.mean(hits_):.2f}   (per-seed success: {np.round(rates, 2).tolist()})")

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    colors = {"real_connectome": "tab:blue", "random_reservoir": "tab:orange", "no_memory": "tab:green"}
    for name, hs in histories.items():
        arr = np.array(hs)
        axes[0].plot(arr.mean(axis=0), label=name, color=colors[name])
        axes[0].fill_between(range(arr.shape[1]), arr.min(axis=0), arr.max(axis=0), alpha=0.15, color=colors[name])
    axes[0].set_xlabel("generation")
    axes[0].set_ylabel("mean population fitness")
    axes[0].set_title("learning curves (band = min/max over seeds)")
    axes[0].legend()

    s = test_seeds[0]
    _, source, _, _, _ = run_episode(env, sc.act, s, max_steps=args.max_steps)
    axes[1].scatter(*source, marker="*", s=250, color="black", zorder=3, label="source")
    for name in variant_names:
        policy = trained[(name, 0)]
        policy.reset()
        path, _, info, _, _ = run_episode(env, policy.act, s, max_steps=args.max_steps)
        axes[1].plot(path[:, 0], path[:, 1], color=colors[name],
                     label=f"{name} ({'success' if info['success'] else 'fail'})")
    axes[1].plot(0, 0, "ko", ms=6, label="start")
    axes[1].set_aspect("equal")
    axes[1].set_title(f"trained trajectories, one unseen episode (seed {s})")
    axes[1].legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig_path = RESULTS_DIR / "plume_results.png"
    fig.savefig(fig_path, dpi=150)
    print(f"\nSaved plot to {fig_path}")


if __name__ == "__main__":
    main()
