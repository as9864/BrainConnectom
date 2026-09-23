"""Turbulent odor-plume tracking: a much more realistic proxy for outdoor chemotaxis
than chemotaxis.py's smooth Gaussian gradient.

Real outdoor odor does not form a smooth gradient -- wind shreds it into intermittent
filaments/puffs (Farrell et al. 2002, "Filament-Based Atmospheric Dispersion Model").
An agent flying through the plume gets binary, patchy hits: "odor now" or "nothing for
a while", not a continuous concentration reading. This is why insects (and this
environment) use surge-and-cast (Kennedy 1983 moth model): surge upwind while
detecting odor, cast crosswind in a widening search when contact is lost, resume
surging when odor is re-detected.

Crucially, this task needs memory: whether to surge or cast depends on *time since
last detection*, not the instantaneous reading alone. chemotaxis.py's smooth-gradient
task was solvable by a purely reactive (memoryless) mapping; this one is not -- which
is the point of testing it with a recurrent reservoir instead of a feedforward net.
"""
import gymnasium as gym
import numpy as np
from gymnasium import spaces


class PlumeEnv(gym.Env):
    def __init__(self, wind_speed=0.6, wind_turbulence=0.35, puff_interval=3,
                 puff_lifetime=150, puff_radius0=0.3, puff_growth=0.006,
                 detect_radius=0.35, world_size=25.0, source_distance_range=(4.0, 8.0),
                 mass=1.0, drag=0.6, max_thrust=2.0, max_turn=2.5, dt=0.1,
                 source_radius=0.5, max_puffs=400):
        self.wind_speed = wind_speed
        self.wind_turbulence = wind_turbulence
        self.puff_interval = puff_interval
        self.puff_lifetime = puff_lifetime
        self.puff_radius0 = puff_radius0
        self.puff_growth = puff_growth
        self.detect_radius = detect_radius
        self.world_size = world_size
        self.source_distance_range = source_distance_range
        self.mass = mass
        self.drag = drag
        self.max_thrust = max_thrust
        self.max_turn = max_turn
        self.dt = dt
        self.source_radius = source_radius
        self.max_puffs = max_puffs
        # obs = [hit (0/1), wind_dir_sin, wind_dir_cos (relative to heading), airspeed]
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(4,), dtype=np.float64)
        self.action_space = spaces.Box(-1.0, 1.0, shape=(2,), dtype=np.float64)

    def _mean_wind(self):
        return self.wind_speed * np.array([np.cos(self.wind_base_dir), np.sin(self.wind_base_dir)])

    def _step_puffs(self):
        # advect existing puffs downwind with turbulent jitter, grow and age them out
        if self.puffs:
            wind = self._mean_wind()
            jitter = self.wind_turbulence * self.np_random.standard_normal((len(self.puffs), 2))
            for p in self.puffs:
                p["pos"] = p["pos"] + (wind + jitter[0]) * self.dt
                p["age"] += 1
                p["radius"] += self.puff_growth
            self.puffs = [p for p in self.puffs if p["age"] < self.puff_lifetime and
                          np.all(np.abs(p["pos"]) < self.world_size * 1.5)]
        self._puff_timer += 1
        if self._puff_timer >= self.puff_interval and len(self.puffs) < self.max_puffs:
            self._puff_timer = 0
            self.puffs.append({"pos": self.source.copy(), "age": 0, "radius": self.puff_radius0})

    def _sense(self):
        hit = 0.0
        for p in self.puffs:
            if np.linalg.norm(self.pos - p["pos"]) < max(p["radius"], self.detect_radius):
                hit = 1.0
                break
        wind = self._mean_wind()
        wind_dir_world = np.arctan2(wind[1], wind[0]) + np.pi  # direction odor *comes from*
        rel = wind_dir_world - self.heading
        airspeed = float(np.linalg.norm(self.vel))
        return np.array([hit, np.sin(rel), np.cos(rel), airspeed])

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.pos = np.zeros(2)
        self.vel = np.zeros(2)
        self.heading = self.np_random.uniform(-np.pi, np.pi)
        self.wind_base_dir = self.np_random.uniform(-np.pi, np.pi)
        bearing = self.wind_base_dir + np.pi + self.np_random.uniform(-0.4, 0.4)  # source roughly upwind
        dist = self.np_random.uniform(*self.source_distance_range)
        self.source = dist * np.array([np.cos(bearing), np.sin(bearing)])
        self._dist = float(np.linalg.norm(self.source - self.pos))
        self.puffs = []
        self._puff_timer = 0
        self._steps_since_hit = 999
        for _ in range(self.puff_lifetime):  # pre-fill plume so it's not empty at t=0
            self._step_puffs()
        return self._sense(), {}

    def step(self, action):
        a = np.clip(np.asarray(action, dtype=float), -1.0, 1.0)
        thrust = self.max_thrust * (a[0] + 1.0) / 2.0
        self.heading += self.max_turn * a[1] * self.dt
        forward = np.array([np.cos(self.heading), np.sin(self.heading)])
        force = thrust * forward - self.drag * self.vel
        self.vel = self.vel + (force / self.mass) * self.dt
        self.pos = self.pos + self.vel * self.dt

        self._step_puffs()
        obs = self._sense()
        self._steps_since_hit = 0 if obs[0] > 0 else self._steps_since_hit + 1

        new_dist = float(np.linalg.norm(self.source - self.pos))
        reward = self._dist - new_dist
        self._dist = new_dist
        if obs[0] > 0:
            reward += 0.05  # small shaping bonus for maintaining odor contact

        success = new_dist < self.source_radius
        out_of_bounds = bool(np.any(np.abs(self.pos) > self.world_size))
        terminated = success or out_of_bounds
        if success:
            reward += 5.0
        if out_of_bounds:
            reward -= 5.0

        return obs, reward, terminated, False, {
            "success": success, "distance": new_dist, "hit": bool(obs[0] > 0),
        }


gym.register(id="Plume-v0", entry_point="robot_experiment.plume_tracking:PlumeEnv", max_episode_steps=300)
