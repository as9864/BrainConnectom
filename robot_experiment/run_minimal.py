"""Minimal wiring check: real-connectome reservoir -> MuJoCo robot body.

This is NOT reinforcement learning yet -- the readout (Wout) is a random fixed
linear map, untrained. The only question this script answers is plumbing:
does "connectome -> reservoir state -> action -> MuJoCo physics -> next
observation -> reservoir" run for a full episode without the reservoir state
blowing up (NaN/inf), and does swapping the real C. elegans connectome for a
density-matched random reservoir visibly change the resulting behavior?

Training the readout to actually make the robot walk is the next step.

Usage:
    python -m robot_experiment.run_minimal
"""
import argparse
from pathlib import Path

import gymnasium as gym
import numpy as np

from reservoir_experiment import connectome
from robot_experiment.policy import ReservoirPolicy

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def run_episode(env, policy, max_steps, seed):
    obs, info = env.reset(seed=seed)
    policy.reset()
    rewards = []
    actions = []
    for _ in range(max_steps):
        action = policy.act(obs)
        obs, r, term, trunc, info = env.step(action)
        rewards.append(r)
        actions.append(action)
        if not np.isfinite(policy.reservoir.x).all():
            print("  !! reservoir state diverged (non-finite) -- stopping early")
            break
        if term or trunc:
            break
    return np.array(rewards), np.array(actions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="Ant-v5")
    parser.add_argument("--rho", type=float, default=0.9, help="target spectral radius")
    parser.add_argument("--leak", type=float, default=0.3)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)

    env = gym.make(args.env)
    n_actions = env.action_space.shape[0]

    W_real_raw = connectome.build_weight_matrix(layers=(2, 3))
    n = W_real_raw.shape[0]
    density = np.count_nonzero(W_real_raw) / (n * n - n)
    variants = {
        "real_connectome": connectome.rescale_spectral_radius(W_real_raw, args.rho),
        "random_reservoir": connectome.rescale_spectral_radius(
            connectome.null_model_dense_gaussian(n, density, seed=args.seed), args.rho
        ),
    }

    results = {}
    for name, W in variants.items():
        policy = ReservoirPolicy(W, n_actions, leak=args.leak, seed=args.seed)
        rewards, actions = run_episode(env, policy, max_steps=args.steps, seed=args.seed)
        results[name] = (rewards, actions)
        print(
            f"{name:16s}: steps={len(rewards):4d}  total_reward={rewards.sum():8.2f}  "
            f"mean_reward={rewards.mean():.4f}  action_std={actions.std():.4f}"
        )

    env.close()

    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
        for name, (rewards, actions) in results.items():
            axes[0].plot(np.cumsum(rewards), label=name)
            axes[1].plot(actions[:, 0], label=name)
        axes[0].set_ylabel("cumulative reward")
        axes[0].legend()
        axes[1].set_ylabel("action[0] (leg 0 torque)")
        axes[1].set_xlabel("timestep")
        fig.suptitle(f"{args.env}: real connectome vs random reservoir (untrained readout)")
        fig.tight_layout()
        fig_path = RESULTS_DIR / "robot_minimal_wiring.png"
        fig.savefig(fig_path, dpi=150)
        print(f"\nSaved plot to {fig_path}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
