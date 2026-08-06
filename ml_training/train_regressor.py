"""Train XGBRegressor for future memory projection."""

from __future__ import annotations

from typing import Any

import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ml_training.training_artifacts import (
    DEFAULT_XGB_PARAMS,
    REGRESSOR_IMPORTANCE_PLOT,
    REGRESSOR_MODEL_NAME,
    REGRESSOR_PATH,
    feature_importance_dict,
    merge_metrics,
    save_feature_importance_plot,
)
from ml_training.training_data import REGRESSOR_TARGET, load_training_frame, split_for_regressor


def build_regressor() -> xgb.XGBRegressor:
    params = {
        **DEFAULT_XGB_PARAMS,
        "objective": "reg:squarederror",
        "eval_metric": "rmse",
    }
    return xgb.XGBRegressor(**params)


def evaluate_regressor(
    model: xgb.XGBRegressor,
    x_val,
    y_val,
) -> dict[str, Any]:
    predictions = model.predict(x_val)
    rmse = float(np.sqrt(mean_squared_error(y_val, predictions)))
    residuals = predictions - y_val

    return {
        "mae": float(mean_absolute_error(y_val, predictions)),
        "rmse": rmse,
        "r2": float(r2_score(y_val, predictions)),
        "validation_rows": int(len(y_val)),
        "residual_p50_mb": float(np.percentile(np.abs(residuals), 50)),
        "residual_p95_mb": float(np.percentile(np.abs(residuals), 95)),
    }


def train_regressor() -> tuple[xgb.XGBRegressor, dict[str, Any]]:
    frame = load_training_frame()
    split = split_for_regressor(frame)

    model = build_regressor()
    model.fit(split.x_train, split.y_train)

    metrics = evaluate_regressor(model, split.x_val, split.y_val)
    importances = feature_importance_dict(model)

    REGRESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(REGRESSOR_PATH)
    save_feature_importance_plot(
        importances,
        REGRESSOR_IMPORTANCE_PLOT,
        title="Future Memory Regressor — Top Feature Importances",
    )

    merge_metrics(
        "regressor",
        {
            "model_name": REGRESSOR_MODEL_NAME,
            "model_path": str(REGRESSOR_PATH.relative_to(REGRESSOR_PATH.parents[1])),
            "target": REGRESSOR_TARGET,
            "prediction_horizon_seconds": 30,
            "train_rows": int(len(split.x_train)),
            "validation_rows": int(len(split.x_val)),
            "hyperparameters": {
                **DEFAULT_XGB_PARAMS,
                "objective": "reg:squarederror",
                "eval_metric": "rmse",
            },
            "validation_metrics": metrics,
            "feature_importance": importances,
            "feature_importance_plot": str(
                REGRESSOR_IMPORTANCE_PLOT.relative_to(REGRESSOR_PATH.parents[1])
            ),
        },
    )
    return model, metrics


if __name__ == "__main__":
    _, result = train_regressor()
    print(f"Saved regressor to {REGRESSOR_PATH}")
    print(
        "Validation metrics: "
        f"mae={result['mae']:.2f} "
        f"rmse={result['rmse']:.2f} "
        f"r2={result['r2']:.3f}"
    )
