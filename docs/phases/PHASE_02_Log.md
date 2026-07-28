# Phase 02 — Data Pipeline & Feature Engineering

## Overview

Phase 2 implements the shared feature engineering pipeline that converts a 30-second window of raw pod telemetry into a model-ready feature vector. The same logic will be used during offline training (Phase 3) and live runtime inference (Phase 5). Output is validated against `dataset/derived/derived_features.csv`.

---

## Conceptual Foundation

Raw telemetry is a time series — one row per second with point-in-time values. A model cannot learn effectively from a single snapshot because it misses trajectory: is memory rising, stable, or falling?

Feature engineering transforms the last 30 seconds of telemetry into derived signals:
- **Rolling averages** — smoothed level over 5s, 10s, 30s windows
- **Slopes** — rate of change (linear regression over the window)
- **Ratios** — memory usage relative to pod limit (generalizes across pods)
- **Standard deviation** — volatility of memory over 30s

The critical constraint is **train-serve parity**: the exact same `build_features()` function must run during batch training and live inference. Any drift between the two causes silent model degradation.

---

## High-Level Design (HLD)

```text
historical_telemetry.csv                live WebSocket stream (Phase 4+)
        │                                         │
        │  group by pod, take 30-row window       │  30s deque buffer
        ▼                                         ▼
┌───────────────────────────────────────────────────────────────┐
│                  ml_training/build_features.py                │
│                                                               │
│   compute_rolling_average()   compute_slope()               │
│   compute_memory_ratio()      compute_rolling_std()         │
│                                                               │
│   build_features(telemetry_window[30]) → feature dict         │
└───────────────────────────┬───────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
   dataset/derived/derived_features.csv   models/feature_schema.json
   (validation reference)                 (runtime column-order contract)
              │
              ▼
        XGBoost training (Phase 3)
```

---

## Low-Level Design (LLD)

```text
build_features(telemetry_window: list[dict])
  │
  ├── validate len(window) == 30
  │
  ├── extract series from raw fields:
  │     memory_usage_mb  → memory[]
  │     cpu_usage_mcores → cpu[]
  │     error_rate_rps   → error_rate[]
  │     request_rate_rps → request_rate[]
  │     latency_p95_ms   → latency_p95[]
  │
  ├── point-in-time (last row):
  │     memory_current_mb, cpu_current_mcores, error_rate_current, ...
  │     memory_ratio_current = memory_current / memory_limit
  │     recent_deployment_flag = 1 if deployment_age_minutes <= 20
  │
  ├── rolling averages (tail of series):
  │     memory_avg_5s, memory_avg_10s, memory_avg_30s
  │     cpu_avg_5s, cpu_avg_10s, cpu_avg_30s
  │     error_rate_avg_5s, error_rate_avg_30s
  │     request_rate_avg_30s, latency_p95_avg_30s
  │
  ├── slopes (linear regression on index 0..n-1):
  │     memory_slope_5s/10s/30s, cpu_slope_10s
  │     error_rate_slope_10s, request_rate_slope_10s, latency_p95_slope_10s
  │
  └── memory_std_30s (sample std dev, ddof=1)

feature_vector_for_model(features) → list[float]
  └── returns ML_FEATURE_COLUMNS in fixed order (28 columns)
```

---

## Data Flow Diagram (DFD)

```text
RAW TELEMETRY ROW (1 second)
  timestamp, pod_name, service_name, namespace, scenario_tag
  memory_usage_mb, memory_limit_mb
  cpu_usage_mcores, error_rate_rps, request_rate_rps, latency_p95_ms
  restart_count, deployment_age_minutes
        │
        │  ×30 rows (sliding window)
        ▼
┌─────────────────────────────────────────────────────────────┐
│ DERIVED FEATURES (output of build_features)                 │
│                                                             │
│  memory_current_mb ──────── from last memory_usage_mb       │
│  memory_ratio_current ───── memory_current / memory_limit   │
│  memory_avg_30s ─────────── mean(last 30 memory values)     │
│  memory_slope_30s ───────── linreg slope(last 30 values)    │
│  memory_std_30s ─────────── sample std(last 30 values)      │
│  cpu_current_mcores ─────── from last cpu_usage_mcores      │
│  error_rate_current ─────── from last error_rate_rps        │
│  request_rate_current ───── from last request_rate_rps      │
│  latency_p95_current ────── from last latency_p95_ms        │
│  recent_deployment_flag ─── 1 if deployment_age_minutes≤20  │
│  restart_count, deployment_age_minutes ─ from last row      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
              models/feature_schema.json
              ml_feature_columns[28] → ordered float vector
                           │
                           ▼
                    XGBoost (Phase 3)
```

---

## Architecture Decisions

**Decision 1: Single `build_features()` module shared by training and runtime**
→ Reason: Eliminates train-serve skew — the primary cause of ML model degradation in production.
→ Alternative: Separate training and inference feature code. Rejected — drift is inevitable.

**Decision 2: Linear regression slope over index positions (0..n-1)**
→ Reason: Matches the pre-computed `dataset/derived/derived_features.csv` exactly. Validated to 1e-6 tolerance across multiple pods.
→ Alternative: Simple delta (last − first) / seconds. Rejected — does not match reference dataset.

**Decision 3: Sample standard deviation (ddof=1) for `memory_std_30s`**
→ Reason: Matches reference dataset. Population std (ddof=0) produces measurably different values.
→ Alternative: Population std. Rejected after validation mismatch.

**Decision 4: `recent_deployment_flag = 1 if deployment_age_minutes <= 20`**
→ Reason: Derived by correlating flag values in `derived_features.csv` with raw telemetry ages. All flag=1 rows have age 0–20; all flag=0 rows have age ≥ 21.
→ Alternative: Fixed calendar-time since deployment event. Rejected — age field already captures this.

**Decision 5: `models/feature_schema.json` exports fixed column order**
→ Reason: XGBoost inference requires features in the exact order used during training. Schema file is the runtime assertion target (Phase 5 will fail fast on mismatch).
→ Alternative: Rely on dict key order. Rejected — not guaranteed across Python versions/serializations.

---

## What Was Built

```text
ml_training/
  __init__.py
  build_features.py           core feature functions + build_features()
  export_feature_schema.py    writes models/feature_schema.json

models/
  feature_schema.json         28 ML columns, version 1.0.0, fixed order

tests/
  test_build_features.py      5 tests validating against derived_features.csv
```

---

## Verify

```bash
source .venv/bin/activate
python -m ml_training.export_feature_schema
pytest tests/test_build_features.py -v
```

Expected:

```text
5 passed
Wrote models/feature_schema.json
```

Validation covers: helper functions, payment-api row at second 30, random sample across 4 pods/scenarios, exact window size enforcement, and ML column order against schema.
