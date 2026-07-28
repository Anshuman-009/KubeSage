"""Export models/feature_schema.json from build_features contract."""

from __future__ import annotations

import json
from pathlib import Path

from ml_training.build_features import FEATURE_WINDOW_SECONDS, ML_FEATURE_COLUMNS

SCHEMA_VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "models" / "feature_schema.json"

INTEGER_COLUMNS = {"restart_count", "deployment_age_minutes", "recent_deployment_flag"}


def build_feature_schema() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "feature_window_seconds": FEATURE_WINDOW_SECONDS,
        "description": "Rolling-window features derived from pod telemetry",
        "source_fields": {
            "memory_usage_mb": "memory_current_mb",
            "memory_limit_mb": "memory_limit_mb",
            "cpu_usage_mcores": "cpu_current_mcores",
            "error_rate_rps": "error_rate_current",
            "request_rate_rps": "request_rate_current",
            "latency_p95_ms": "latency_p95_current",
        },
        "ml_feature_columns": ML_FEATURE_COLUMNS,
        "columns": [
            {
                "name": name,
                "type": "int" if name in INTEGER_COLUMNS else "float",
            }
            for name in ML_FEATURE_COLUMNS
        ],
    }


def export_feature_schema(path: Path | None = None) -> Path:
    target = path or OUTPUT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_feature_schema(), indent=2) + "\n")
    return target


if __name__ == "__main__":
    print(f"Wrote {export_feature_schema()}")
