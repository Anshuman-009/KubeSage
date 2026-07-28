"""Tests for rolling-window feature engineering."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from ml_training.build_features import (
    FEATURE_WINDOW_SECONDS,
    ML_FEATURE_COLUMNS,
    build_features,
    compute_memory_ratio,
    compute_rolling_average,
    compute_rolling_std,
    compute_slope,
    feature_vector_for_model,
)
from ml_training.export_feature_schema import export_feature_schema

ROOT = Path(__file__).resolve().parents[1]
TELEMETRY_PATH = ROOT / "dataset" / "source" / "historical_telemetry.csv"
DERIVED_PATH = ROOT / "dataset" / "derived" / "derived_features.csv"


def _load_pod_rows(pod_name: str) -> list[dict]:
    with TELEMETRY_PATH.open(newline="") as handle:
        return [row for row in csv.DictReader(handle) if row["pod_name"] == pod_name]


def _window_for_feature_id(feature_id: str) -> tuple[list[dict], dict]:
    with DERIVED_PATH.open(newline="") as handle:
        derived = {row["feature_id"]: row for row in csv.DictReader(handle)}

    row = derived[feature_id]
    pod_rows = _load_pod_rows(row["pod_name"])
    timestamps = [item["timestamp"] for item in pod_rows]
    end_idx = timestamps.index(row["timestamp"])
    start_idx = end_idx - (FEATURE_WINDOW_SECONDS - 1)
    return pod_rows[start_idx : end_idx + 1], row


def test_compute_helpers() -> None:
    assert compute_rolling_average([1, 2, 3, 4, 5], 5) == 3.0
    assert compute_memory_ratio(512, 1024) == 0.5
    assert compute_slope([10, 12, 14]) == pytest.approx(2.0)
    assert compute_rolling_std([1, 2, 3], 3) == pytest.approx(1.0)


def test_build_features_matches_derived_row_payment_api() -> None:
    window, expected = _window_for_feature_id("payment-api-7f8d0_30")
    actual = build_features(window)

    numeric_fields = [key for key in expected.keys() if key not in {"feature_id"}]
    for field in numeric_fields:
        if field in {"timestamp", "pod_name", "service_name", "namespace", "scenario_tag"}:
            assert actual[field] == expected[field]
        else:
            assert float(actual[field]) == pytest.approx(float(expected[field]), rel=1e-6, abs=1e-6)


def test_build_features_matches_random_sample_rows() -> None:
    sample_ids = [
        "auth-api-6d1a0_30",
        "auth-api-6d1a0_120",
        "payment-api-7f8d0_540",
        "checkout-api-7f8d0_45",
    ]
    compare_fields = ML_FEATURE_COLUMNS + [
        "timestamp",
        "pod_name",
        "service_name",
        "namespace",
        "scenario_tag",
    ]

    string_fields = {"timestamp", "pod_name", "service_name", "namespace", "scenario_tag"}

    for feature_id in sample_ids:
        window, expected = _window_for_feature_id(feature_id)
        actual = build_features(window)
        for field in compare_fields:
            if field in string_fields:
                assert actual[field] == expected[field]
            else:
                assert float(actual[field]) == pytest.approx(
                    float(expected[field]), rel=1e-6, abs=1e-6
                )


def test_build_features_requires_exact_window_size() -> None:
    window, _ = _window_for_feature_id("auth-api-6d1a0_30")
    with pytest.raises(ValueError):
        build_features(window[:10])


def test_feature_vector_column_order_matches_schema() -> None:
    schema_path = export_feature_schema()
    schema = json.loads(schema_path.read_text())
    window, expected = _window_for_feature_id("auth-api-6d1a0_30")
    features = build_features(window)
    vector = feature_vector_for_model(features)

    assert schema["ml_feature_columns"] == ML_FEATURE_COLUMNS
    assert len(vector) == len(ML_FEATURE_COLUMNS)
    for index, column in enumerate(ML_FEATURE_COLUMNS):
        assert vector[index] == pytest.approx(float(expected[column]), rel=1e-6, abs=1e-6)
