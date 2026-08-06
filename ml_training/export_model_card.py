"""Generate models/model_card.md from training metrics."""

from __future__ import annotations

from pathlib import Path

from ml_training.build_features import ML_FEATURE_COLUMNS
from ml_training.training_artifacts import MODEL_CARD_PATH, load_metrics

BREACH_THRESHOLD_RATIO = 0.9
PREDICTION_HORIZON_SECONDS = 30


def _top_features(importances: dict[str, float], limit: int = 5) -> str:
    ranked = sorted(importances.items(), key=lambda item: item[1], reverse=True)[:limit]
    lines = [f"- `{name}` — {score:.4f}" for name, score in ranked]
    return "\n".join(lines)


def build_model_card(metrics: dict) -> str:
    classifier = metrics["classifier"]
    regressor = metrics["regressor"]
    clf_metrics = classifier["validation_metrics"]
    reg_metrics = regressor["validation_metrics"]

    return f"""# Model Card — KubeSage

## Overview

Two XGBoost models predict pod memory risk from a 30-second rolling telemetry window:

| Model | Type | Output |
|-------|------|--------|
| `{classifier["model_name"]}` | XGBClassifier | Breach probability in next {PREDICTION_HORIZON_SECONDS}s |
| `{regressor["model_name"]}` | XGBRegressor | Projected memory usage (MB) in next {PREDICTION_HORIZON_SECONDS}s |

## Training Data

- Features: `dataset/derived/derived_features.csv` ({len(ML_FEATURE_COLUMNS)} columns)
- Labels: `dataset/derived/training_labels.csv`
- Join key: `feature_id`
- Train/validation split: 80/20 (`random_state=42`)
- Classifier split: stratified on `{classifier["label"]}`
- Dataset positive breach rate (train split): {classifier["train_positive_rate"]:.2%}
- Validation positive rate: {classifier["validation_metrics"]["validation_positive_rate"]:.2%}

## Label Definitions

**Classifier label (`{classifier["label"]}`):** `1` if pod memory ratio reaches ≥ {BREACH_THRESHOLD_RATIO:.0%} of limit within the next {PREDICTION_HORIZON_SECONDS} seconds; else `0`.

**Regressor target (`{regressor["target"]}`):** Actual memory usage (MB) observed {PREDICTION_HORIZON_SECONDS} seconds after the feature window end.

## Feature List

Fixed column order from `models/feature_schema.json`:

{chr(10).join(f"- `{column}`" for column in ML_FEATURE_COLUMNS)}

## Classifier Evaluation (validation)

| Metric | Value |
|--------|-------|
| Precision | {clf_metrics["precision"]:.3f} |
| Recall | {clf_metrics["recall"]:.3f} |
| F1 | {clf_metrics["f1"]:.3f} |
| ROC-AUC | {clf_metrics["roc_auc"]:.3f} |
| Accuracy | {clf_metrics["accuracy"]:.3f} |

Confusion matrix (validation):

```text
                Predicted 0   Predicted 1
Actual 0        {clf_metrics["confusion_matrix"]["true_negative"]:>10}   {clf_metrics["confusion_matrix"]["false_positive"]:>10}
Actual 1        {clf_metrics["confusion_matrix"]["false_negative"]:>10}   {clf_metrics["confusion_matrix"]["true_positive"]:>10}
```

Top features:

{_top_features(classifier["feature_importance"])}

Imbalance handling: `scale_pos_weight={classifier["scale_pos_weight"]:.2f}`

## Regressor Evaluation (validation)

| Metric | Value |
|--------|-------|
| MAE | {reg_metrics["mae"]:.2f} MB |
| RMSE | {reg_metrics["rmse"]:.2f} MB |
| R² | {reg_metrics["r2"]:.3f} |
| Residual p50 | {reg_metrics["residual_p50_mb"]:.2f} MB |
| Residual p95 | {reg_metrics["residual_p95_mb"]:.2f} MB |

Top features:

{_top_features(regressor["feature_importance"])}

## Known Limitations

- Trained on synthetic telemetry with a small number of breach scenarios (~6.5% positive class).
- Row-level split may leak adjacent windows from the same pod between train and validation.
- Regressor accuracy degrades during rapid spike ramps not seen in training.
- Models assume feature schema v1.0.0; runtime must assert column order before inference.

## Runtime Usage

```python
import xgboost as xgb
from ml_training.build_features import build_features, feature_vector_for_model

classifier = xgb.XGBClassifier()
classifier.load_model("models/memory_breach_xgb_classifier.json")

regressor = xgb.XGBRegressor()
regressor.load_model("models/future_memory_xgb_regressor.json")

features = build_features(telemetry_window_30_rows)
vector = [feature_vector_for_model(features)]

breach_probability = float(classifier.predict_proba(vector)[0][1])
predicted_memory_mb_30s = float(regressor.predict(vector)[0])
predicted_memory_ratio_30s = predicted_memory_mb_30s / features["memory_limit_mb"]
```

Artifacts:

- `{classifier["model_path"]}`
- `{regressor["model_path"]}`
- `models/feature_schema.json`
- `models/training_metrics.json`
- `{classifier["feature_importance_plot"]}`
- `{regressor["feature_importance_plot"]}`
"""


def export_model_card(path: Path | None = None) -> Path:
    target = path or MODEL_CARD_PATH
    metrics = load_metrics()
    if "classifier" not in metrics or "regressor" not in metrics:
        raise ValueError("training metrics must include classifier and regressor sections")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_model_card(metrics))
    return target


if __name__ == "__main__":
    print(f"Wrote {export_model_card()}")
