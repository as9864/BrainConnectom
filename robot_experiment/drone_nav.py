"""2D drone-like navigation: reach a goal beacon while avoiding obstacles using only
optic-flow-style ranging "eyes" -- no camera image, no map of obstacle positions.

Each eye reports proximity (how close the nearest obstacle along that ray is) and its
time-derivative (how fast it's looming), which is the same signal insect motion-detection
circuits (T4/T5 cells in the medulla/lobula) compute from raw vision -- a lightweight proxy
for "visual input" without needing to render and process actual images. Goal direction comes
from a GPS/compass-style bearing signal, the way real drones get waypoints, so the vision
channel is specifically responsible for obstacle avoidance, not navigation.

Physics is a simple point-mass + drag (thrust and turn-rate controlled), not full quadrotor
dynamics -- this environment exists to test whether a fixed-reservoir + trained-readout
policy can turn a handful of flow channels into safe navigation, before any of this touches
real flight hardware.
"""
import gymnasium as gym
import numpy as np
from gymnasium import spaces


class DroneNavEnv(gym.Env):
    def __init__(self, n_rays=5, fov=120.0, ray_range=3.0, n_obstacles=6,
                 obstacle_radius=0.4, world_size=8.0, goal_radius=0.5,
                 mass=1.0, drag=0.6, max_thrust=2.0, max_turn=2.5, dt=0.1,
                 collision_penalty=5.0, sensor_noise=0.02):
        self.n_rays = n_rays
        self.fov = np.radians(fov)
        self.ray_range = ray_range
        self.n_obstacles = n_obstacles
        self.obstacle_radius = obstacle_radius
        self.world_size = world_size
        self.goal_radius = goal_radius
        self.mass = mass
        self.drag = drag
        self.max_thrust = max_thrust
        self.max_turn = max_turn
        self.dt = dt
        self.collision_penalty = collision_penalty
        self.sensor_noise = sensor_noise
        self.ray_angles = np.linspace(-self.fov / 2, self.fov / 2, n_rays)
        # obs = [proximity_per_ray, optic_flow_per_ray, sin(bearing), cos(bearing)]
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(2 * n_rays + 2,), dtype=np.float64)
        self.action_space = spaces.Box(-1.0, 1.0, shape=(2,), dtype=np.float64)

    def _cast_rays(self):
        prox = np.zeros(self.n_rays)
        for i, rel_angle in enumerate(self.ray_angles):
            ang = self.heading + rel_angle
            direction = np.array([np.cos(ang), np.sin(ang)])
            nearest = self.ray_range
            for obs_pos in self.obstacles:
                to_obs = obs_pos - self.pos
                proj = to_obs @ direction
                if proj <= 0:
                    continue
                closest_pt = self.pos + proj * direction
                perp_dist = np.linalg.norm(obs_pos - closest_pt)
                if perp_dist <= self.obstacle_radius:
                    hit_dist = proj - np.sqrt(max(self.obstacle_radius ** 2 - perp_dist ** 2, 0.0))
                    if 0 < hit_dist < nearest:
                        nearest = hit_dist
            for axis in range(2):
                d = direction[axis]
                if abs(d) < 1e-6:
                    continue
                for sign in (-1, 1):
                    wall = sign * self.world_size
                    t = (wall - self.pos[axis]) / d
                    if t > 0:
                        nearest = min(nearest, t)
            prox[i] = 1.0 - nearest / self.ray_range  # 0 = clear, 1 = touching
        return prox

    def _obs(self):
        prox = self._cast_rays()
        prox = prox * (1.0 + self.sensor_noise * self.np_random.standard_normal(self.n_rays))
        flow = (prox - self._prev_prox) / self.dt  # positive = looming closer
        self._prev_prox = prox
        to_goal = self.goal - self.pos
        bearing = np.arctan2(to_goal[1], to_goal[0]) - self.heading
        compass = np.array([np.sin(bearing), np.cos(bearing)])
        return np.concatenate([prox, flow, compass])

    def _random_free_point(self, min_dist_from, min_dist):
        for _ in range(200):
            p = self.np_random.uniform(-self.world_size * 0.9, self.world_size * 0.9, size=2)
            if np.linalg.norm(p - min_dist_from) < min_dist:
                continue
            if all(np.linalg.norm(p - o) > self.obstacle_radius + 0.5 for o in getattr(self, "obstacles", [])):
                return p
        return p

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.pos = np.zeros(2)
        self.vel = np.zeros(2)
        self.heading = self.np_random.uniform(-np.pi, np.pi)
        self.obstacles = []
        for _ in range(self.n_obstacles):
            self.obstacles.append(self._random_free_point(self.pos, min_dist=1.5))
        self.goal = self._random_free_point(self.pos, min_dist=4.0)
        self._dist = float(np.linalg.norm(self.goal - self.pos))
        self._prev_prox = np.zeros(self.n_rays)
        self._prev_prox = self._cast_rays()
        return self._obs(), {}

    def step(self, action):
        a = np.clip(np.asarray(action, dtype=float), -1.0, 1.0)
        thrust = self.max_thrust * (a[0] + 1.0) / 2.0
        self.heading += self.max_turn * a[1] * self.dt
        forward = np.array([np.cos(self.heading), np.sin(self.heading)])
        force = thrust * forward - self.drag * self.vel
        self.vel = self.vel + (force / self.mass) * self.dt
        self.pos = self.pos + self.vel * self.dt

        new_dist = float(np.linalg.norm(self.goal - self.pos))
        reward = self._dist - new_dist
        self._dist = new_dist

        collided = any(np.linalg.norm(self.pos - o) < self.obstacle_radius + 0.15 for o in self.obstacles)
        out_of_bounds = bool(np.any(np.abs(self.pos) > self.world_size))
        success = new_dist < self.goal_radius
        terminated = collided or out_of_bounds or success
        if success:
            reward += 5.0
        if collided or out_of_bounds:
            reward -= self.collision_penalty

        return self._obs(), reward, terminated, False, {
            "success": success, "collided": collided or out_of_bounds, "distance": new_dist,
        }


gym.register(id="DroneNav-v0", entry_point="robot_experiment.drone_nav:DroneNavEnv", max_episode_steps=150)
