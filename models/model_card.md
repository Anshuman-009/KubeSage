# Model Card — KubeSage

## Overview

Two XGBoost models predict pod memory risk from a 30-second rolling telemetry window:

| Model | Type | Output |
|-------|------|--------|
| `memory-breach-xgb-v1` | XGBClassifier | Breach probability in next 30s |
| `future-memory-xgb-v1` | XGBRegressor | Projected memory usage (MB) in next 30s |

## Training Data

- Features: `dataset/derived/derived_features.csv` (28 columns)
- Labels: `dataset/derived/training_labels.csv`
- Join key: `feature_id`
- Train/validation split: 80/20 (`random_state=42`)
- Classifier split: stratified on `label_memory_breach_next_30s`
- Dataset positive breach rate (train split): 6.51%
- Validation positive rate: 6.50%

## Label Definitions

**Classifier label (`label_memory_breach_next_30s`):** `1` if pod memory ratio reaches ≥ 90% of limit within the next 30 seconds; else `0`.

**Regressor target (`target_memory_mb_30s`):** Actual memory usage (MB) observed 30 seconds after the feature window end.

## Feature List

Fixed column order from `models/feature_schema.json`:

- `memory_current_mb`
- `memory_limit_mb`
- `memory_ratio_current`
- `memory_avg_5s`
- `memory_avg_10s`
- `memory_avg_30s`
- `memory_slope_5s`
- `memory_slope_10s`
- `memory_slope_30s`
- `memory_std_30s`
- `cpu_current_mcores`
- `cpu_avg_5s`
- `cpu_avg_10s`
- `cpu_avg_30s`
- `cpu_slope_10s`
- `error_rate_current`
- `error_rate_avg_5s`
- `error_rate_avg_30s`
- `error_rate_slope_10s`
- `request_rate_current`
- `request_rate_avg_30s`
- `request_rate_slope_10s`
- `latency_p95_current`
- `latency_p95_avg_30s`
- `latency_p95_slope_10s`
- `restart_count`
- `deployment_age_minutes`
- `recent_deployment_flag`

## Classifier Evaluation (validation)

| Metric | Value |
|--------|-------|
| Precision | 0.985 |
| Recall | 1.000 |
| F1 | 0.992 |
| ROC-AUC | 1.000 |
| Accuracy | 0.999 |

Confusion matrix (validation):

```text
                Predicted 0   Predicted 1
Actual 0              1883            2
Actual 1                 0          131
```

Top features:

- `memory_avg_5s` — 0.4553
- `memory_avg_30s` — 0.2976
- `memory_avg_10s` — 0.2104
- `memory_current_mb` — 0.0226
- `latency_p95_avg_30s` — 0.0017

Imbalance handling: `scale_pos_weight=14.36`

## Regressor Evaluation (validation)

| Metric | Value |
|--------|-------|
| MAE | 7.21 MB |
| RMSE | 10.67 MB |
| R² | 0.997 |
| Residual p50 | 5.62 MB |
| Residual p95 | 18.55 MB |

Top features:

- `memory_avg_30s` — 0.4598
- `memory_avg_10s` — 0.2267
- `memory_avg_5s` — 0.1477
- `memory_limit_mb` — 0.0947
- `error_rate_avg_30s` — 0.0169

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

- `models/memory_breach_xgb_classifier.json`
- `models/future_memory_xgb_regressor.json`
- `models/feature_schema.json`
- `models/training_metrics.json`
- `models/feature_importance_classifier.png`
- `models/feature_importance_regressor.png`
