"""Standard reservoir-computing benchmark tasks: memory capacity and NARMA-10."""
import numpy as np
from sklearn.linear_model import Ridge


def generate_memory_capacity_input(T, seed=0):
    rng = np.random.default_rng(seed)
    u = rng.uniform(-1, 1, size=(T, 1))
    return u


def generate_narma10(T, seed=0):
    rng = np.random.default_rng(seed)
    u = rng.uniform(0, 0.5, size=T + 10)
    y = np.zeros(T + 10)
    for t in range(9, T + 9):
        y[t + 1] = (
            0.3 * y[t]
            + 0.05 * y[t] * np.sum(y[t - 9:t + 1])
            + 1.5 * u[t - 9] * u[t]
            + 0.1
        )
    return u[10:].reshape(-1, 1), y[10:].reshape(-1, 1)


def evaluate_memory_capacity(states, u, max_delay=30, washout=100, ridge_alpha=1e-6):
    """Jaeger (2001) memory capacity: sum over delays k of R^2 reconstructing u[t-k]
    from the reservoir state at time t, using a linear readout trained per delay.
    """
    T = states.shape[0]
    per_delay_r2 = []
    for k in range(1, max_delay + 1):
        X = states[washout + k:]
        y = u[washout: T - k].flatten()
        n = min(len(X), len(y))
        X, y = X[:n], y[:n]
        split = int(n * 0.7)
        model = Ridge(alpha=ridge_alpha)
        model.fit(X[:split], y[:split])
        pred = model.predict(X[split:])
        y_test = y[split:]
        ss_res = np.sum((y_test - pred) ** 2)
        ss_tot = np.sum((y_test - y_test.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        per_delay_r2.append(max(r2, 0.0))
    return float(np.sum(per_delay_r2)), per_delay_r2


def evaluate_narma10(states, y, washout=100, ridge_alpha=1e-6, train_frac=0.7):
    X = states[washout:]
    target = y[washout:].flatten()
    split = int(len(X) * train_frac)
    model = Ridge(alpha=ridge_alpha)
    model.fit(X[:split], target[:split])
    pred = model.predict(X[split:])
    y_test = target[split:]
    nrmse = np.sqrt(np.mean((pred - y_test) ** 2)) / np.std(y_test)
    return float(nrmse)
