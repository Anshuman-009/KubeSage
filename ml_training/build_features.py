"""Rolling-window feature engineering shared by training and runtime inference."""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

FEATURE_WINDOW_SECONDS = 30
RECENT_DEPLOYMENT_MINUTES = 20

# Stable column order used for model input (matches models/feature_schema.json).
ML_FEATURE_COLUMNS: list[str] = [
    "memory_current_mb",
    "memory_limit_mb",
    "memory_ratio_current",
    "memory_avg_5s",
    "memory_avg_10s",
    "memory_avg_30s",
    "memory_slope_5s",
    "memory_slope_10s",
    "memory_slope_30s",
    "memory_std_30s",
    "cpu_current_mcores",
    "cpu_avg_5s",
    "cpu_avg_10s",
    "cpu_avg_30s",
    "cpu_slope_10s",
    "error_rate_current",
    "error_rate_avg_5s",
    "error_rate_avg_30s",
    "error_rate_slope_10s",
    "request_rate_current",
    "request_rate_avg_30s",
    "request_rate_slope_10s",
    "latency_p95_current",
    "latency_p95_avg_30s",
    "latency_p95_slope_10s",
    "restart_count",
    "deployment_age_minutes",
    "recent_deployment_flag",
]


def compute_rolling_average(values: Sequence[float], window: int) -> float:
    """Average of the last `window` values."""
    if window <= 0:
        raise ValueError("window must be positive")
    if len(values) < window:
        raise ValueError(f"need at least {window} values, got {len(values)}")
    sample = values[-window:]
    return sum(sample) / len(sample)


def compute_slope(values: Sequence[float]) -> float:
    """Linear regression slope over index positions 0..n-1."""
    if len(values) < 2:
        return 0.0
    xs = list(range(len(values)))
    x_bar = sum(xs) / len(xs)
    y_bar = sum(values) / len(values)
    numerator = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, values))
    denominator = sum((x - x_bar) ** 2 for x in xs)
    if denominator == 0:
        return 0.0
    return numerator / denominator


def compute_memory_ratio(used_mb: float, limit_mb: float) -> float:
    if limit_mb <= 0:
        raise ValueError("memory limit must be positive")
    return used_mb / limit_mb


def compute_rolling_std(values: Sequence[float], window: int) -> float:
    """Sample standard deviation over the last `window` values."""
    if len(values) < window:
        raise ValueError(f"need at least {window} values, got {len(values)}")
    sample = values[-window:]
    mean = sum(sample) / len(sample)
    if len(sample) < 2:
        return 0.0
    variance = sum((value - mean) ** 2 for value in sample) / (len(sample) - 1)
    return math.sqrt(variance)


def _series(rows: Sequence[Mapping[str, Any]], field: str) -> list[float]:
    return [float(row[field]) for row in rows]


def build_features(telemetry_window: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """
    Build a model-ready feature dict from a 30-second telemetry window.

    Each row must contain fields from historical_telemetry.csv:
    memory_usage_mb, memory_limit_mb, cpu_usage_mcores, error_rate_rps,
    request_rate_rps, latency_p95_ms, restart_count, deployment_age_minutes,
    plus metadata: timestamp, pod_name, service_name, namespace, scenario_tag.
    """
    if len(telemetry_window) != FEATURE_WINDOW_SECONDS:
        raise ValueError(
            f"expected exactly {FEATURE_WINDOW_SECONDS} telemetry rows, got {len(telemetry_window)}"
        )

    last = telemetry_window[-1]
    memory = _series(telemetry_window, "memory_usage_mb")
    cpu = _series(telemetry_window, "cpu_usage_mcores")
    error_rate = _series(telemetry_window, "error_rate_rps")
    request_rate = _series(telemetry_window, "request_rate_rps")
    latency_p95 = _series(telemetry_window, "latency_p95_ms")

    memory_current = memory[-1]
    memory_limit = float(last["memory_limit_mb"])
    deployment_age = int(last["deployment_age_minutes"])

    features: dict[str, Any] = {
        "timestamp": last["timestamp"],
        "pod_name": last["pod_name"],
        "service_name": last["service_name"],
        "namespace": last["namespace"],
        "scenario_tag": last.get("scenario_tag") or None,
        "memory_current_mb": memory_current,
        "memory_limit_mb": memory_limit,
        "memory_ratio_current": compute_memory_ratio(memory_current, memory_limit),
        "memory_avg_5s": compute_rolling_average(memory, 5),
        "memory_avg_10s": compute_rolling_average(memory, 10),
        "memory_avg_30s": compute_rolling_average(memory, 30),
        "memory_slope_5s": compute_slope(memory[-5:]),
        "memory_slope_10s": compute_slope(memory[-10:]),
        "memory_slope_30s": compute_slope(memory),
        "memory_std_30s": compute_rolling_std(memory, 30),
        "cpu_current_mcores": cpu[-1],
        "cpu_avg_5s": compute_rolling_average(cpu, 5),
        "cpu_avg_10s": compute_rolling_average(cpu, 10),
        "cpu_avg_30s": compute_rolling_average(cpu, 30),
        "cpu_slope_10s": compute_slope(cpu[-10:]),
        "error_rate_current": error_rate[-1],
        "error_rate_avg_5s": compute_rolling_average(error_rate, 5),
        "error_rate_avg_30s": compute_rolling_average(error_rate, 30),
        "error_rate_slope_10s": compute_slope(error_rate[-10:]),
        "request_rate_current": request_rate[-1],
        "request_rate_avg_30s": compute_rolling_average(request_rate, 30),
        "request_rate_slope_10s": compute_slope(request_rate[-10:]),
        "latency_p95_current": latency_p95[-1],
        "latency_p95_avg_30s": compute_rolling_average(latency_p95, 30),
        "latency_p95_slope_10s": compute_slope(latency_p95[-10:]),
        "restart_count": int(last["restart_count"]),
        "deployment_age_minutes": deployment_age,
        "recent_deployment_flag": 1 if deployment_age <= RECENT_DEPLOYMENT_MINUTES else 0,
    }
    return features


def feature_vector_for_model(features: Mapping[str, Any]) -> list[float]:
    """Return numeric features in schema column order for XGBoost inference."""
    vector: list[float] = []
    for column in ML_FEATURE_COLUMNS:
        value = features[column]
        vector.append(float(value))
    return vector
