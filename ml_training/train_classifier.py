"""Train XGBClassifier for memory breach probability."""

from __future__ import annotations

from typing import Any

import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from ml_training.training_artifacts import (
    CLASSIFIER_IMPORTANCE_PLOT,
    CLASSIFIER_MODEL_NAME,
    CLASSIFIER_PATH,
    DEFAULT_XGB_PARAMS,
    feature_importance_dict,
    merge_metrics,
    save_feature_importance_plot,
)
from ml_training.training_data import (
    CLASSIFIER_LABEL,
    load_training_frame,
    positive_class_weight,
    split_for_classifier,
)


def build_classifier(scale_pos_weight: float) -> xgb.XGBClassifier:
    params = {
        **DEFAULT_XGB_PARAMS,
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "scale_pos_weight": scale_pos_weight,
    }
    return xgb.XGBClassifier(**params)


def evaluate_classifier(
    model: xgb.XGBClassifier,
    x_val,
    y_val,
) -> dict[str, Any]:
    probabilities = model.predict_proba(x_val)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_val, predictions, labels=[0, 1]).ravel()
    metrics: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_val, predictions)),
        "precision": float(precision_score(y_val, predictions, zero_division=0)),
        "recall": float(recall_score(y_val, predictions, zero_division=0)),
        "f1": float(f1_score(y_val, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_val, probabilities)),
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "validation_positive_rate": float(y_val.mean()),
        "validation_rows": int(len(y_val)),
    }
    return metrics


def train_classifier() -> tuple[xgb.XGBClassifier, dict[str, Any]]:
    frame = load_training_frame()
    split = split_for_classifier(frame)
    scale_pos_weight = positive_class_weight(split.y_train)

    model = build_classifier(scale_pos_weight)
    model.fit(split.x_train, split.y_train)

    metrics = evaluate_classifier(model, split.x_val, split.y_val)
    importances = feature_importance_dict(model)

    CLASSIFIER_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(CLASSIFIER_PATH)
    save_feature_importance_plot(
        importances,
        CLASSIFIER_IMPORTANCE_PLOT,
        title="Memory Breach Classifier — Top Feature Importances",
    )

    merge_metrics(
        "classifier",
        {
            "model_name": CLASSIFIER_MODEL_NAME,
            "model_path": str(CLASSIFIER_PATH.relative_to(CLASSIFIER_PATH.parents[1])),
            "label": CLASSIFIER_LABEL,
            "prediction_horizon_seconds": 30,
            "breach_threshold_ratio": 0.9,
            "train_rows": int(len(split.x_train)),
            "validation_rows": int(len(split.x_val)),
            "train_positive_rate": float(split.y_train.mean()),
            "scale_pos_weight": float(scale_pos_weight),
            "hyperparameters": {
                **DEFAULT_XGB_PARAMS,
                "objective": "binary:logistic",
                "eval_metric": "logloss",
                "scale_pos_weight": float(scale_pos_weight),
            },
            "validation_metrics": metrics,
            "feature_importance": importances,
            "feature_importance_plot": str(
                CLASSIFIER_IMPORTANCE_PLOT.relative_to(CLASSIFIER_PATH.parents[1])
            ),
        },
    )
    return model, metrics


if __name__ == "__main__":
    _, result = train_classifier()
    print(f"Saved classifier to {CLASSIFIER_PATH}")
    print(
        "Validation metrics: "
        f"precision={result['precision']:.3f} "
        f"recall={result['recall']:.3f} "
        f"f1={result['f1']:.3f} "
        f"roc_auc={result['roc_auc']:.3f}"
    )
