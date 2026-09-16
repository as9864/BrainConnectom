"""A minimal leaky-integrator echo-state-network reservoir."""
import numpy as np


class LeakyESN:
    def __init__(self, W, leak=0.3, input_scale=1.0, seed=0):
        self.W = W
        self.n_reservoir = W.shape[0]
        self.leak = leak
        rng = np.random.default_rng(seed)
        self._rng = rng
        self._input_scale = input_scale
        self.Win = None  # built lazily once we know input dimensionality

    def _ensure_input_weights(self, n_inputs):
        if self.Win is None or self.Win.shape[1] != n_inputs:
            self.Win = self._rng.uniform(-1, 1, size=(self.n_reservoir, n_inputs)) * self._input_scale

    def run(self, u, x0=None):
        """u: (T, n_inputs) -> states: (T, n_reservoir)"""
        u = np.atleast_2d(u)
        if u.shape[1] != 1 and u.shape[0] == 1:
            u = u.T
        T, n_inputs = u.shape
        self._ensure_input_weights(n_inputs)

        x = np.zeros(self.n_reservoir) if x0 is None else x0.copy()
        states = np.zeros((T, self.n_reservoir))
        for t in range(T):
            pre_activation = self.W @ x + self.Win @ u[t]
            x = (1 - self.leak) * x + self.leak * np.tanh(pre_activation)
            states[t] = x
        return states
