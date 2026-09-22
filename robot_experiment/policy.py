"""Wrap a fixed reservoir (e.g. a real connectome) as a step-by-step control policy.

reservoir_experiment.reservoir.LeakyESN only exposes a batch `run(u)` API, which
assumes the whole input sequence is known ahead of time -- fine for a fixed
benchmark input, useless for closed-loop robot control where the action taken at
t changes the observation at t+1. SteppingReservoir carries the same
leaky-integrator ESN dynamics one timestep at a time instead.
"""
import numpy as np


class SteppingReservoir:
    def __init__(self, W, leak=0.3, input_scale=1.0, seed=0):
        self.W = W
        self.n_reservoir = W.shape[0]
        self.leak = leak
        self._rng = np.random.default_rng(seed)
        self._input_scale = input_scale
        self.Win = None  # built lazily once we know the observation dimensionality
        self.x = np.zeros(self.n_reservoir)

    def _ensure_input_weights(self, n_inputs):
        if self.Win is None:
            self.Win = self._rng.uniform(-1, 1, size=(self.n_reservoir, n_inputs)) * self._input_scale

    def reset(self):
        self.x = np.zeros(self.n_reservoir)

    def step(self, u):
        self._ensure_input_weights(u.shape[0])
        pre_activation = self.W @ self.x + self.Win @ u
        self.x = (1 - self.leak) * self.x + self.leak * np.tanh(pre_activation)
        return self.x


class ReservoirPolicy:
    """obs -> fixed reservoir -> linear readout -> action (clipped to the env's action bounds).

    Wout starts as a random fixed readout. Nothing here is trained yet -- this
    class only exists to check that the reservoir dynamics stay bounded and
    actually close the loop with the robot body. Training Wout to make the
    robot walk is a separate step (e.g. treat Wout as the parameters an RL/ES
    loop optimizes, same "fixed reservoir + trained readout" split used in
    reservoir_experiment).
    """

    def __init__(self, W, n_actions, leak=0.3, input_scale=1.0, readout_scale=None, seed=0,
                 action_low=-1.0, action_high=1.0):
        self.reservoir = SteppingReservoir(W, leak=leak, input_scale=input_scale, seed=seed)
        self.n_actions = n_actions
        n_reservoir = W.shape[0]
        if readout_scale is None:
            # Summing ~n_reservoir random terms blows up with a fixed-scale init (raw output
            # saturates the action clip almost always, killing the ES gradient signal). Scale
            # down by 1/sqrt(n_reservoir) so the pre-clip output starts in a sane range.
            readout_scale = 1.0 / np.sqrt(n_reservoir)
        rng = np.random.default_rng(seed + 1)
        self.Wout = rng.uniform(-1, 1, size=(n_actions, n_reservoir)) * readout_scale
        self.action_low = action_low
        self.action_high = action_high

    def reset(self):
        self.reservoir.reset()

    def act(self, obs):
        state = self.reservoir.step(np.asarray(obs, dtype=float))
        action = self.Wout @ state
        return np.clip(action, self.action_low, self.action_high)
