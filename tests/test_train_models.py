"""Tests for Phase 3 model training artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import xgboost as xgb

from ml_training.build_features import ML_FEATURE_COLUMNS, build_features, feature_vector_for_model
from ml_training.export_model_card import export_model_card
from ml_training.train_classifier import train_classifier
from ml_training.train_regressor import train_regressor
from ml_training.training_artifacts import (
    CLASSIFIER_IMPORTANCE_PLOT,
    CLASSIFIER_PATH,
    METRICS_PATH,
    MODEL_CARD_PATH,
    REGRESSOR_IMPORTANCE_PLOT,
    REGRESSOR_PATH,
)
from ml_training.training_data import load_training_frame

ROOT = Path(__file__).resolve().parents[1]
DERIVED_PATH = ROOT / "dataset" / "derived" / "derived_features.csv"
TELEMETRY_PATH = ROOT / "dataset" / "source" / "historical_telemetry.csv"
FEATURE_WINDOW_SECONDS = 30


def _window_for_feature_id(feature_id: str) -> tuple[list[dict], dict]:
    import csv

    with DERIVED_PATH.open(newline="") as handle:
        derived = {row["feature_id"]: row for row in csv.DictReader(handle)}
    row = derived[feature_id]
    with TELEMETRY_PATH.open(newline="") as handle:
        pod_rows = [item for item in csv.DictReader(handle) if item["pod_name"] == row["pod_name"]]
    timestamps = [item["timestamp"] for item in pod_rows]
    end_idx = timestamps.index(row["timestamp"])
    start_idx = end_idx - (FEATURE_WINDOW_SECONDS - 1)
    return pod_rows[start_idx : end_idx + 1], row


@pytest.fixture(scope="module")
def trained_models():
    classifier, classifier_metrics = train_classifier()
    regressor, regressor_metrics = train_regressor()
    export_model_card()
    return {
        "classifier": classifier,
        "regressor": regressor,
        "classifier_metrics": classifier_metrics,
        "regressor_metrics": regressor_metrics,
    }


def test_training_frame_join_has_expected_shape() -> None:
    frame = load_training_frame()
    assert len(frame) == 10080
    assert set(ML_FEATURE_COLUMNS).issubset(frame.columns)
    assert frame["label_memory_breach_next_30s"].isin([0, 1]).all()


def test_training_artifacts_exist(trained_models) -> None:
    assert CLASSIFIER_PATH.exists()
    assert REGRESSOR_PATH.exists()
    assert METRICS_PATH.exists()
    assert MODEL_CARD_PATH.exists()
    assert CLASSIFIER_IMPORTANCE_PLOT.exists()
    assert REGRESSOR_IMPORTANCE_PLOT.exists()


def test_classifier_validation_meets_minimum_quality(trained_models) -> None:
    metrics = trained_models["classifier_metrics"]
    assert metrics["roc_auc"] >= 0.90
    assert metrics["recall"] >= 0.50
    assert metrics["precision"] >= 0.30


def test_regressor_validation_meets_minimum_quality(trained_models) -> None:
    metrics = trained_models["regressor_metrics"]
    assert metrics["r2"] >= 0.85
    assert metrics["mae"] <= 35.0


def test_models_reload_and_predict_on_sample_window(trained_models) -> None:
    window, _ = _window_for_feature_id("payment-api-7f8d0_540")
    features = build_features(window)
    vector = [feature_vector_for_model(features)]

    classifier = xgb.XGBClassifier()
    classifier.load_model(CLASSIFIER_PATH)
    regressor = xgb.XGBRegressor()
    regressor.load_model(REGRESSOR_PATH)

    breach_probability = float(classifier.predict_proba(vector)[0][1])
    predicted_memory = float(regressor.predict(vector)[0])

    assert 0.0 <= breach_probability <= 1.0
    assert predicted_memory > 0.0
    assert breach_probability >= 0.7


def test_training_metrics_json_structure(trained_models) -> None:
    payload = json.loads(METRICS_PATH.read_text())
    assert "classifier" in payload
    assert "regressor" in payload
    assert payload["classifier"]["validation_metrics"]["roc_auc"] > 0
    assert payload["regressor"]["validation_metrics"]["rmse"] > 0
