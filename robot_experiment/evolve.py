"""Train the reservoir readout (Wout) with a simple evolution strategy (ES),
keeping the reservoir itself (real connectome or random) completely fixed.

This mirrors the "fixed reservoir + trained linear readout" split used
throughout this repo's reservoir_experiment: the connectome supplies fixed
nonlinear dynamics, and the only thing ever optimized is the linear map from
reservoir state to action.

Algorithm: OpenAI-ES (Salimans et al. 2017) -- antithetic sampling + a
centered-rank fitness transform, no gradients through the MuJoCo simulator
required, so any black-box reward works.

Usage:
    python -m robot_experiment.evolve --generations 80 --population 32
"""
import argparse
from pathlib import Path

import gymnasium as gym
import numpy as np

from reservoir_experiment import connectome
from robot_experiment.policy import ReservoirPolicy

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def rollout_reward(env, policy, Wout, max_steps, seed):
    policy.Wout = Wout
    policy.reset()
    obs, info = env.reset(seed=seed)
    total = 0.0
    for _ in range(max_steps):
        action = policy.act(obs)
        obs, r, term, trunc, info = env.step(action)
        total += r
        if not np.isfinite(policy.reservoir.x).all():
            total -= 100.0  # penalize diverging dynamics, then stop
            break
        if term or trunc:
            break
    return total


def rank_shape(fitness):
    """Centered rank transform -- robust to reward scale/outliers (Wierstra et al. 2014)."""
    order = np.argsort(fitness)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(len(fitness))
    return ranks / (len(fitness) - 1) - 0.5


def evolve_readout(W, env_name, n_actions, seed, leak, generations, population,
                    sigma, lr, max_steps, eval_seeds, log_every=5):
    env = gym.make(env_name)
    policy = ReservoirPolicy(W, n_actions, leak=leak, seed=seed)
    shape = policy.Wout.shape
    theta = policy.Wout.flatten()
    n_params = theta.size

    rng = np.random.default_rng(seed + 1000)
    history = []
    for gen in range(generations):
        half = population // 2
        eps = rng.standard_normal((half, n_params))
        eps = np.concatenate([eps, -eps], axis=0)  # antithetic pairs
        fitness = np.zeros(population)
        for i in range(population):
            candidate = (theta + sigma * eps[i]).reshape(shape)
            episode_seed = int(eval_seeds[gen % len(eval_seeds)])
            fitness[i] = rollout_reward(env, policy, candidate, max_steps, episode_seed)

        shaped = rank_shape(fitness)
        grad = eps.T @ shaped / population
        theta = theta + lr * grad

        history.append(fitness.mean())
        if gen % log_every == 0 or gen == generations - 1:
            print(f"  gen {gen:3d}/{generations}: mean_fitness={fitness.mean():8.2f}  best={fitness.max():8.2f}")

    env.close()
    return theta.reshape(shape), history


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="Ant-v5")
    parser.add_argument("--rho", type=float, default=0.9, help="target spectral radius")
    parser.add_argument("--leak", type=float, default=0.3)
    parser.add_argument("--generations", type=int, default=80)
    parser.add_argument("--population", type=int, default=32)
    parser.add_argument("--sigma", type=float, default=0.02, help="ES perturbation std")
    parser.add_argument("--lr", type=float, default=0.02, help="ES step size")
    parser.add_argument("--max-steps", type=int, default=200, help="training rollout length")
    parser.add_argument("--n-eval-seeds", type=int, default=4, help="episode seeds cycled through during training")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)

    probe_env = gym.make(args.env)
    n_actions = probe_env.action_space.shape[0]
    probe_env.close()

    W_real_raw = connectome.build_weight_matrix(layers=(2, 3))
    n = W_real_raw.shape[0]
    density = np.count_nonzero(W_real_raw) / (n * n - n)
    variants = {
        "real_connectome": connectome.rescale_spectral_radius(W_real_raw, args.rho),
        "random_reservoir": connectome.rescale_spectral_radius(
            connectome.null_model_dense_gaussian(n, density, seed=args.seed), args.rho
        ),
    }

    eval_seeds = np.arange(args.n_eval_seeds) + 1000

    histories = {}
    final_theta = {}
    for name, W in variants.items():
        print(f"\n=== evolving Wout for {name} ===")
        theta, history = evolve_readout(
            W, args.env, n_actions, args.seed, args.leak,
            args.generations, args.population, args.sigma, args.lr,
            args.max_steps, eval_seeds,
        )
        histories[name] = history
        final_theta[name] = theta

    for name, theta in final_theta.items():
        np.save(RESULTS_DIR / f"robot_wout_{name}.npy", theta)

    print("\n=== final evaluation (trained Wout, longer rollout, unseen seeds) ===")
    env = gym.make(args.env)
    final_rewards = {}
    for name, W in variants.items():
        policy = ReservoirPolicy(W, n_actions, leak=args.leak, seed=args.seed)
        rewards = [
            rollout_reward(env, policy, final_theta[name], args.max_steps * 2, seed=s)
            for s in range(5000, 5005)
        ]
        final_rewards[name] = rewards
        print(f"{name:16s}: mean_reward={np.mean(rewards):8.2f} +/- {np.std(rewards):.2f}")
    env.close()

    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 5))
        for name, history in histories.items():
            ax.plot(history, label=name)
        ax.set_xlabel("generation")
        ax.set_ylabel("mean population fitness (episode reward)")
        ax.set_title(f"{args.env}: ES-trained readout, real connectome vs random reservoir")
        ax.legend()
        fig.tight_layout()
        fig_path = RESULTS_DIR / "robot_evolve_learning_curve.png"
        fig.savefig(fig_path, dpi=150)
        print(f"\nSaved plot to {fig_path}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
