"""Render a trained (or untrained) reservoir policy to an MP4/GIF so you can watch it.

Usage:
    python -m robot_experiment.render --variant real_connectome
    python -m robot_experiment.render --variant random_reservoir
    python -m robot_experiment.render --variant real_connectome --untrained   # before-training baseline
"""
import argparse
from pathlib import Path

import gymnasium as gym
import imageio.v2 as imageio
import numpy as np

from reservoir_experiment import connectome
from robot_experiment.policy import ReservoirPolicy

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="Ant-v5")
    parser.add_argument("--variant", choices=["real_connectome", "random_reservoir"], default="real_connectome")
    parser.add_argument("--rho", type=float, default=0.9)
    parser.add_argument("--leak", type=float, default=0.3)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--episode-seed", type=int, default=5000)
    parser.add_argument("--untrained", action="store_true", help="use the initial random Wout")
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args()

    W_real_raw = connectome.build_weight_matrix(layers=(2, 3))
    n = W_real_raw.shape[0]
    density = np.count_nonzero(W_real_raw) / (n * n - n)
    if args.variant == "real_connectome":
        W = connectome.rescale_spectral_radius(W_real_raw, args.rho)
    else:
        W = connectome.rescale_spectral_radius(
            connectome.null_model_dense_gaussian(n, density, seed=args.seed), args.rho
        )

    env = gym.make(args.env, render_mode="rgb_array", width=640, height=480)
    n_actions = env.action_space.shape[0]
    policy = ReservoirPolicy(
        W, n_actions, leak=args.leak, seed=args.seed,
        action_low=env.action_space.low, action_high=env.action_space.high,
    )
    tag = "untrained"
    if not args.untrained:
        policy.Wout = np.load(RESULTS_DIR / f"robot_wout_{args.variant}.npy")
        tag = "trained"

    obs, _ = env.reset(seed=args.episode_seed)
    policy.reset()
    frames, total = [], 0.0
    for _ in range(args.steps):
        frames.append(env.render())
        obs, r, term, trunc, _ = env.step(policy.act(obs))
        total += r
        if term or trunc:
            break
    env.close()

    out = RESULTS_DIR / f"robot_{args.variant}_{tag}.mp4"
    imageio.mimsave(out, frames, fps=args.fps)
    print(f"{args.variant} ({tag}): {len(frames)} steps, total_reward={total:.1f}")
    print(f"Saved video to {out}")


if __name__ == "__main__":
    main()
