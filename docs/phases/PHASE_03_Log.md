# Phase 03 — ML Model Training

## Overview

Phase 3 trains two XGBoost models on derived features from Phase 2: a binary classifier for memory breach probability and a regressor for projected memory usage 30 seconds ahead. Models are exported as JSON artifacts with validation metrics, feature importance plots, and a model card for runtime use in Phase 5.

---

## Conceptual Foundation

Feature vectors describe pod state over the last 30 seconds, but operators need forward-looking signals:

- **Will memory breach the limit soon?** → classification (probability)
- **How much memory will the pod use in 30 seconds?** → regression (continuous MB)

A single model cannot answer both well. The classifier optimizes for rare breach events (~6.5% positive rate). The regressor predicts absolute memory, which the risk agent converts to a ratio using the pod limit.

Training uses the same 28-column feature matrix defined in `models/feature_schema.json`. Labels come from `training_labels.csv`, joined on `feature_id`.

**Breach label:** `label_memory_breach_next_30s = 1` when memory ratio reaches ≥ 90% of limit within the next 30 seconds.

**Regressor target:** `target_memory_mb_30s` — actual memory usage (MB) 30 seconds after the feature window.

---

## High-Level Design (HLD)

```text
dataset/derived/derived_features.csv ──┐
                                       ├──► training_data.load_training_frame()
dataset/derived/training_labels.csv ───┘              │
                                                      ▼
                              ┌───────────────────────────────────────┐
                              │  80/20 split (random_state=42)        │
                              │  classifier: stratified on label      │
                              │  regressor: random split              │
                              └───────────────┬───────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
         train_classifier.py                                 train_regressor.py
         XGBClassifier                                       XGBRegressor
         scale_pos_weight=14.36                              objective=reg:squarederror
                    │                                                   │
                    ▼                                                   ▼
   memory_breach_xgb_classifier.json              future_memory_xgb_regressor.json
                    │                                                   │
                    └─────────────────────────┬─────────────────────────┘
                                              ▼
                              training_metrics.json + model_card.md
                              feature_importance_*.png
                                              │
                                              ▼
                              Phase 5 Prediction Service (runtime load)
```

---

## Low-Level Design (LLD)

```text
training_data.py
  load_training_frame()
    └── merge features + labels on feature_id
    └── assert 28 ML columns present
  split_for_classifier() → TrainingSplit (stratified)
  split_for_regressor()  → TrainingSplit (random)
  positive_class_weight() → negatives / positives

train_classifier.py
  build_classifier(scale_pos_weight)
    └── XGBClassifier(n_estimators=100, max_depth=6, lr=0.1, ...)
  evaluate_classifier()
    └── predict_proba → threshold 0.5
    └── precision, recall, F1, ROC-AUC, confusion matrix
  train_classifier()
    └── fit → save JSON → plot importances → merge metrics

train_regressor.py
  build_regressor()
    └── XGBRegressor(same tree params, reg:squarederror)
  evaluate_regressor()
    └── MAE, RMSE, R², residual p50/p95
  train_regressor()
    └── fit → save JSON → plot importances → merge metrics

train_models.py
  train_classifier() → train_regressor() → export_model_card()

export_model_card.py
  build_model_card(metrics) → models/model_card.md
```

---

## Data Flow Diagram (DFD)

```text
INPUT: derived_features.csv row
  feature_id, memory_current_mb, memory_avg_30s, memory_slope_30s, ...
        │
        │  join on feature_id
        ▼
INPUT: training_labels.csv row
  label_memory_breach_next_30s, target_memory_mb_30s
        │
        │  extract ML_FEATURE_COLUMNS[28]
        ▼
┌─────────────────────────────────────────┐
│ TRAINING MATRIX                         │
│  X: float[8064 × 28]  (train)          │
│  y_clf: {0,1}         (breach label)    │
│  y_reg: float         (memory MB)       │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
CLASSIFIER OUTPUT           REGRESSOR OUTPUT
  breach_probability        predicted_memory_mb_30s
  (0.0 – 1.0)               (continuous MB)
      │                       │
      └───────────┬───────────┘
                  ▼
Phase 5 PredictionEvent:
  breach_probability, predicted_memory_mb_30s,
  breach_likely (= prob >= 0.5)
```

---

## Architecture Decisions

**Decision 1: Two separate models (classifier + regressor) instead of one multi-output model**
→ Reason: Different objectives — rare-event detection vs continuous forecasting. Classifier needs imbalance handling; regressor does not.
→ Alternative: Single XGBoost with multi-output or derived ratio-only model. Rejected — loses calibrated breach probability.

**Decision 2: `scale_pos_weight` for class imbalance (~6.5% positive)**
→ Reason: Without reweighting, the classifier optimizes for accuracy by predicting "no breach" almost always — high accuracy, near-zero recall.
→ Alternative: SMOTE oversampling or undersampling. Rejected for POC simplicity; scale_pos_weight is native to XGBoost.

**Decision 3: Stratified split for classifier, random split for regressor**
→ Reason: Stratification preserves positive rate in validation for meaningful precision/recall on rare class. Regressor target is continuous and roughly balanced across pods.
→ Alternative: Pod-level or time-based split. Considered for production; row-level split acceptable for synthetic POC dataset.

**Decision 4: XGBoost JSON export (not pickle)**
→ Reason: Portable, versioned artifacts loadable via `model.load_model()` in Phase 5 without Python pickle security concerns.
→ Alternative: joblib/pickle. Rejected — less portable across environments.

**Decision 5: Feature importance stored as JSON + PNG plot**
→ Reason: JSON feeds programmatic inspection; PNG supports human review in model card workflow.
→ Alternative: SHAP values. Deferred — unnecessary complexity for POC.

---

## What Was Built

```text
ml_training/
  training_data.py           load/join dataset, stratified split, scale_pos_weight
  training_artifacts.py        paths, metrics merge, importance plots
  train_classifier.py          XGBClassifier training + evaluation
  train_regressor.py           XGBRegressor training + evaluation
  train_models.py              orchestrates both models + model card
  export_model_card.py         generates models/model_card.md

models/
  memory_breach_xgb_classifier.json
  future_memory_xgb_regressor.json
  training_metrics.json
  model_card.md
  feature_importance_classifier.png
  feature_importance_regressor.png

tests/
  test_train_models.py         6 tests: join, artifacts, metrics, inference
```

---

## Validation Results

| Model | Key metrics (validation, 2016 rows) |
|-------|-------------------------------------|
| Classifier | precision=0.985, recall=1.000, F1=0.992, ROC-AUC=1.000 |
| Regressor | MAE=7.21 MB, RMSE=10.67 MB, R²=0.997 |

Top classifier features: `memory_avg_5s`, `memory_avg_30s`, `memory_avg_10s`.

Top regressor features: `memory_avg_30s`, `memory_avg_10s`, `memory_limit_mb`.

Spike scenario spot-check (`payment-api-7f8d0_540`): breach_probability ≥ 0.7.

---

## Verify

```bash
pip install -e ".[dev]"
python -m ml_training.train_models
pytest tests/test_train_models.py -v
pytest tests/ -q
```

Expected:

```text
Artifacts written under models/
6 passed (test_train_models.py)
21 passed (full suite)
```

Manual inference check:

```bash
python -c "
import xgboost as xgb
from ml_training.build_features import build_features, feature_vector_for_model
import csv
from pathlib import Path

ROOT = Path('.')
# load payment-api spike window at second 540
...
"
```

Or rely on `test_models_reload_and_predict_on_sample_window` which validates `payment-api-7f8d0_540` → breach_probability ≥ 0.7.
