"""2D odor-tracking (chemotaxis) toy environment: a point agent with two antennae.

Odor concentration decays exponentially with distance from a hidden food source.
The agent only senses the concentration at its left and right antenna -- it never
sees the food position. Actions: [forward drive, turn rate], both in [-1, 1].
"""
import gymnasium as gym
import numpy as np
from gymnasium import spaces


class ChemotaxisEnv(gym.Env):
    def __init__(self, decay_length=2.0, antenna_forward=0.3, antenna_lateral=0.4,
                 max_speed=0.15, max_turn=0.3, success_radius=0.4, sensor_noise=0.01,
                 encoding="raw", contrast_gain=4.0):
        assert encoding in ("raw", "contrast")
        self.encoding = encoding
        self.contrast_gain = contrast_gain
        self.decay_length = decay_length
        self.antenna_forward = antenna_forward
        self.antenna_lateral = antenna_lateral
        self.max_speed = max_speed
        self.max_turn = max_turn
        self.success_radius = success_radius
        self.sensor_noise = sensor_noise
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(2,), dtype=np.float64)
        self.action_space = spaces.Box(-1.0, 1.0, shape=(2,), dtype=np.float64)

    def _concentration(self, point):
        return np.exp(-np.linalg.norm(point - self.food) / self.decay_length)

    def _obs(self):
        c, s = np.cos(self.heading), np.sin(self.heading)
        fwd, lat = np.array([c, s]), np.array([-s, c])  # lat = agent's left
        left = self.pos + self.antenna_forward * fwd + self.antenna_lateral * lat
        right = self.pos + self.antenna_forward * fwd - self.antenna_lateral * lat
        obs = np.array([self._concentration(left), self._concentration(right)])
        obs = obs * (1.0 + self.sensor_noise * self.np_random.standard_normal(2))
        if self.encoding == "contrast":
            # divisive normalization: [left-right contrast, mean intensity]
            l, r = obs
            return np.array([self.contrast_gain * (l - r) / (l + r + 1e-9), (l + r) / 2.0])
        return obs

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.pos = np.zeros(2)
        self.heading = self.np_random.uniform(-np.pi, np.pi)
        bearing = self.np_random.uniform(-np.pi, np.pi)
        dist = self.np_random.uniform(2.0, 5.0)
        self.food = dist * np.array([np.cos(bearing), np.sin(bearing)])
        self._dist = float(np.linalg.norm(self.food))
        return self._obs(), {}

    def step(self, action):
        a = np.clip(np.asarray(action, dtype=float), -1.0, 1.0)
        self.heading += self.max_turn * a[1]
        speed = self.max_speed * (a[0] + 1.0) / 2.0
        self.pos = self.pos + speed * np.array([np.cos(self.heading), np.sin(self.heading)])
        new_dist = float(np.linalg.norm(self.pos - self.food))
        reward = self._dist - new_dist
        self._dist = new_dist
        success = new_dist < self.success_radius
        if success:
            reward += 5.0
        return self._obs(), reward, success, False, {"success": success, "distance": new_dist}


gym.register(id="Chemotaxis-v0", entry_point="robot_experiment.chemotaxis:ChemotaxisEnv", max_episode_steps=200)
gym.register(id="ChemotaxisContrast-v0", entry_point="robot_experiment.chemotaxis:ChemotaxisEnv",
             max_episode_steps=200, kwargs={"encoding": "contrast"})
