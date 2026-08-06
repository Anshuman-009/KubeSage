"""Load and split derived feature rows for model training."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from ml_training.build_features import ML_FEATURE_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
DERIVED_FEATURES_PATH = ROOT / "dataset" / "derived" / "derived_features.csv"
TRAINING_LABELS_PATH = ROOT / "dataset" / "derived" / "training_labels.csv"

CLASSIFIER_LABEL = "label_memory_breach_next_30s"
REGRESSOR_TARGET = "target_memory_mb_30s"

DEFAULT_RANDOM_STATE = 42
DEFAULT_TEST_SIZE = 0.2


@dataclass(frozen=True)
class TrainingSplit:
    """Train/validation matrices with aligned metadata."""

    x_train: pd.DataFrame
    x_val: pd.DataFrame
    y_train: pd.Series
    y_val: pd.Series
    feature_ids_train: pd.Series
    feature_ids_val: pd.Series


def load_training_frame(
    features_path: Path | None = None,
    labels_path: Path | None = None,
) -> pd.DataFrame:
    """Join derived features with labels on feature_id."""
    features = pd.read_csv(features_path or DERIVED_FEATURES_PATH)
    labels = pd.read_csv(labels_path or TRAINING_LABELS_PATH)

    frame = features.merge(labels, on="feature_id", suffixes=("", "_label"))
    if "timestamp_label" in frame.columns:
        frame = frame.drop(columns=["timestamp_label"])

    missing = set(ML_FEATURE_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"training frame missing ML feature columns: {sorted(missing)}")

    for column in ML_FEATURE_COLUMNS:
        frame[column] = pd.to_numeric(frame[column])

    frame[CLASSIFIER_LABEL] = frame[CLASSIFIER_LABEL].astype(int)
    frame[REGRESSOR_TARGET] = pd.to_numeric(frame[REGRESSOR_TARGET])

    if frame["feature_id"].duplicated().any():
        raise ValueError("duplicate feature_id rows after join")

    return frame


def split_for_classifier(
    frame: pd.DataFrame,
    *,
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> TrainingSplit:
    """Stratified train/validation split for breach classification."""
    x = frame[ML_FEATURE_COLUMNS]
    y = frame[CLASSIFIER_LABEL]
    feature_ids = frame["feature_id"]

    x_train, x_val, y_train, y_val, ids_train, ids_val = train_test_split(
        x,
        y,
        feature_ids,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    return TrainingSplit(x_train, x_val, y_train, y_val, ids_train, ids_val)


def split_for_regressor(
    frame: pd.DataFrame,
    *,
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> TrainingSplit:
    """Random train/validation split for memory regression."""
    x = frame[ML_FEATURE_COLUMNS]
    y = frame[REGRESSOR_TARGET]
    feature_ids = frame["feature_id"]

    x_train, x_val, y_train, y_val, ids_train, ids_val = train_test_split(
        x,
        y,
        feature_ids,
        test_size=test_size,
        random_state=random_state,
    )
    return TrainingSplit(x_train, x_val, y_train, y_val, ids_train, ids_val)


def positive_class_weight(y_train: pd.Series) -> float:
    """Compute scale_pos_weight from training labels."""
    positives = int(y_train.sum())
    negatives = int(len(y_train) - positives)
    if positives == 0:
        raise ValueError("training split has no positive breach labels")
    return negatives / positives
