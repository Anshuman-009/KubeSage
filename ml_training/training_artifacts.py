"""Shared helpers for model training artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ml_training.build_features import ML_FEATURE_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"

CLASSIFIER_PATH = MODELS_DIR / "memory_breach_xgb_classifier.json"
REGRESSOR_PATH = MODELS_DIR / "future_memory_xgb_regressor.json"
METRICS_PATH = MODELS_DIR / "training_metrics.json"
MODEL_CARD_PATH = MODELS_DIR / "model_card.md"
CLASSIFIER_IMPORTANCE_PLOT = MODELS_DIR / "feature_importance_classifier.png"
REGRESSOR_IMPORTANCE_PLOT = MODELS_DIR / "feature_importance_regressor.png"

CLASSIFIER_MODEL_NAME = "memory-breach-xgb-v1"
REGRESSOR_MODEL_NAME = "future-memory-xgb-v1"

DEFAULT_XGB_PARAMS: dict[str, Any] = {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "n_jobs": -1,
}


def feature_importance_dict(
    model: Any,
    feature_names: Sequence[str] | None = None,
) -> dict[str, float]:
    """Return feature importances keyed by column name."""
    names = list(feature_names or ML_FEATURE_COLUMNS)
    scores = model.feature_importances_
    return {name: float(score) for name, score in zip(names, scores)}


def save_feature_importance_plot(
    importances: Mapping[str, float],
    output_path: Path,
    *,
    title: str,
    top_n: int = 15,
) -> Path:
    """Write a horizontal bar chart of top feature importances."""
    import matplotlib.pyplot as plt

    ranked = sorted(importances.items(), key=lambda item: item[1], reverse=True)[:top_n]
    labels = [name for name, _ in reversed(ranked)]
    values = [score for _, score in reversed(ranked)]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.barh(labels, values, color="#2563eb")
    axis.set_title(title)
    axis.set_xlabel("Importance (gain)")
    figure.tight_layout()
    figure.savefig(output_path, dpi=120)
    plt.close(figure)
    return output_path


def load_metrics() -> dict[str, Any]:
    if not METRICS_PATH.exists():
        return {}
    return json.loads(METRICS_PATH.read_text())


def save_metrics(metrics: Mapping[str, Any]) -> Path:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(dict(metrics), indent=2) + "\n")
    return METRICS_PATH


def merge_metrics(section: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    metrics = load_metrics()
    metrics[section] = dict(payload)
    save_metrics(metrics)
    return metrics
