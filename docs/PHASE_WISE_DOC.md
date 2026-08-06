# Phase-Wise Documentation

Deep architecture and design record for each build phase of POC-RTML-AGENT-001.

---

## Phase index

| Phase | Title | Status | Log |
|-------|-------|--------|-----|
| 01 | Project Setup & Contracts | ✅ Complete | [PHASE_01_Log.md](phases/PHASE_01_Log.md) |
| 02 | Data Pipeline & Feature Engineering | ✅ Complete | [PHASE_02_Log.md](phases/PHASE_02_Log.md) |
| 03 | ML Model Training | ✅ Complete | [PHASE_03_Log.md](phases/PHASE_03_Log.md) |
| 04 | Mock Kube Telemetry App | ⬜ Pending | — |
| 05 | Stream Ingestion, Buffer & Prediction Service | ⬜ Pending | — |
| 06 | Risk Reasoning Agent | ⬜ Pending | — |
| 07 | RAG Retrieval Service | ⬜ Pending | — |
| 08 | LLM Narrative Agent | ⬜ Pending | — |
| 09 | Action / Alert Agent & Human Approval | ⬜ Pending | — |
| 10 | React Dashboard | ⬜ Pending | — |
| 11 | Evaluation & Wrap-Up | ⬜ Pending | — |

---

## Phase 01 — Project Setup & Contracts

Phase 1 delivered the two-app project skeleton and the full Pydantic contract layer. Stream event types are defined once in `shared/contracts/` and imported by both apps. Intelligence-only schemas model the full internal pipeline from ML features through human feedback.

Key decisions: single shared contract package, strict boundary validation (`extra="forbid"`), separation of stream vs pipeline schemas.

**Full log** → [phases/PHASE_01_Log.md](phases/PHASE_01_Log.md)

---

## Phase 02 — Data Pipeline & Feature Engineering

Phase 2 implemented `ml_training/build_features.py` — a shared rolling-window feature builder validated to match `dataset/derived/derived_features.csv` within 1e-6 tolerance. A 30-second telemetry window produces 28 ML features including rolling averages, linear-regression slopes, memory ratios, and sample standard deviation. `models/feature_schema.json` locks the column order for train-serve parity in Phase 3 (training) and Phase 5 (runtime inference).

Key decisions: single shared module for train and serve, linear-regression slopes matching the reference dataset, sample std (ddof=1), deployment flag threshold at 20 minutes.

**Full log** → [phases/PHASE_02_Log.md](phases/PHASE_02_Log.md)

---

## Phase 03 — ML Model Training

Phase 3 trained two XGBoost models on the 28-column feature matrix from Phase 2. The classifier predicts memory breach probability within 30 seconds (label: ratio ≥ 90%); the regressor predicts future memory in MB. Artifacts include JSON model files, validation metrics, feature importance plots, and a model card. Classifier validation: precision 0.985, recall 1.0, ROC-AUC 1.0. Regressor validation: MAE 7.2 MB, R² 0.997.

Key decisions: separate classifier/regressor, `scale_pos_weight` for ~6.5% positive rate, stratified classifier split, XGBoost JSON export for Phase 5 runtime loading.

**Full log** → [phases/PHASE_03_Log.md](phases/PHASE_03_Log.md)

---

## Upcoming phases

Phases 04–11 will be documented here as each completes.
