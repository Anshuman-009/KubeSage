"""Train both XGBoost models and export all Phase 3 artifacts."""

from __future__ import annotations

from ml_training.export_model_card import export_model_card
from ml_training.train_classifier import train_classifier
from ml_training.train_regressor import train_regressor
from ml_training.training_artifacts import (
    CLASSIFIER_PATH,
    METRICS_PATH,
    MODEL_CARD_PATH,
    REGRESSOR_PATH,
)


def train_all() -> None:
    train_classifier()
    train_regressor()
    export_model_card()


if __name__ == "__main__":
    train_all()
    print(f"Artifacts written under models/")
    print(f"  - {CLASSIFIER_PATH.name}")
    print(f"  - {REGRESSOR_PATH.name}")
    print(f"  - {METRICS_PATH.name}")
    print(f"  - {MODEL_CARD_PATH.name}")
