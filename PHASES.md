# POC-RTML-AGENT-001 — Phase Tracker

Traditional development roadmap. Each phase ships a working component. Documentation covers Conceptual, HLD, LLD, DFD for every phase.

---

## Phase 1 — Project Setup & Contracts

**Status** → Complete

**Deliverables:**
- Two-app folder structure (`mock-kube-telemetry-app/`, `poc-intelligence-app/`)
- `shared/contracts/` — Pydantic schemas for all event types
- `pyproject.toml`, `.gitignore`, `README.md`

**Schemas to define:**
- Stream: `TelemetryEvent`, `AppLogEvent`, `KubeEvent`
- Pipeline: `FeatureVector`, `PredictionEvent`, `RiskDecision`, `LlmNarrative`, `AlertEvent`, `ActionEvent`, `HumanFeedbackEvent`

**Done when:** Both apps agree on all contract shapes. Contract validation tests pass.

---

## Phase 2 — Data Pipeline & Feature Engineering

**Status** → Complete

**Deliverables:**
- `ml_training/build_features.py` — rolling window feature builder
- `models/feature_schema.json` — versioned feature contract
- Validated output against `dataset/derived/derived_features.csv`

**Covers:**
- Rolling averages, slopes, ratios, std
- 30-second window → feature vector
- Train-serve contract: same logic at training and runtime

**Done when:** `build_features(window)` produces a feature dict that matches the column schema in `derived_features.csv`.

---

## Phase 3 — ML Model Training

**Status** → Complete

**Deliverables:**
- `ml_training/train_classifier.py` — XGBClassifier (breach probability)
- `ml_training/train_regressor.py` — XGBRegressor (future memory)
- `models/memory_breach_xgb_classifier.json`
- `models/future_memory_xgb_regressor.json`
- `models/training_metrics.json`
- `models/model_card.md`

**Covers:**
- Stratified train/val split on `dataset/derived/`
- Evaluation: precision, recall, F1, AUC-ROC (classifier); MAE, RMSE, R² (regressor)
- Feature importance plots

**Done when:** Both models load and produce valid inference output.

---

## Phase 4 — Mock Kube Telemetry App

**Status** → Pending

**Deliverables:**
- `mock-kube-telemetry-app/app/main.py` — FastAPI app
- WebSocket endpoint streaming telemetry, logs, k8s events
- Scenario runner: normal / memory_spike / cpu_spike / error_spike
- Controlled spike injection

**Done when:** A WebSocket client receives 60 seconds of live telemetry for one scenario.

---

## Phase 5 — Stream Ingestion, Buffer & Prediction Service

**Status** → Pending

**Deliverables:**
- `ingestion/stream_ingestion_service.py`
- `buffer/telemetry_buffer_service.py` — 30s rolling deque
- `features/feature_builder_service.py` — reuses Phase 2 logic
- `prediction/prediction_service.py` — loads Phase 3 models, runs inference
- Column-order assertion against `feature_schema.json` at startup
- `prediction_log.jsonl` per run

**Done when:** memory_spike scenario → `breach_probability` rises above 0.7 within ~60s.

---

## Phase 6 — Risk Reasoning Agent

**Status** → Pending

**Deliverables:**
- `agents/risk_reasoning_agent.py`
- Risk levels: NORMAL / WATCH / HIGH / CRITICAL (named thresholds)
- Routing flags: `requires_rag`, `requires_alert`, `requires_human_approval`
- 60-second cooldown deduplication
- Full decision audit log

**Done when:** During a spike, agent emits structured `RiskDecision` with routing flags.

---

## Phase 7 — RAG Retrieval Service

**Status** → Pending

**Deliverables:**
- `rag/document_loader.py` — load runbooks, incidents, deployment notes
- `rag/keyword_retriever.py` — TF-IDF / token overlap, top-k with scores
- `rag/embedding_retriever.py` — optional, nomic-embed-text via Ollama
- `rag/rag_retrieval_service.py` — unified retrieval interface

**Done when:** HIGH/CRITICAL decision triggers retrieval; top-3 chunks returned with source and score.

---

## Phase 8 — LLM Narrative Agent

**Status** → Pending

**Deliverables:**
- `llm/llm_api_client.py` — Ollama HTTP client
- `llm/prompt_templates.py` — system + user prompts with few-shot JSON
- `agents/llm_narrative_agent.py` — generates `LlmNarrative`, retries once on invalid JSON
- LLM call log: model, tokens, latency, `json_valid`

Initial model: `qwen3:8b`

**Done when:** HIGH risk event → valid `LlmNarrative` JSON with all required fields.

---

## Phase 9 — Action / Alert Agent & Human Approval

**Status** → Pending

**Deliverables:**
- `agents/action_alert_agent.py`
- Alert deduplication with cooldown
- `ActionEvent` with expiry; `POST /approve` and `/reject` endpoints
- Human decision logged to `human_feedback_log.jsonl`

**Done when:** Two consecutive HIGH alerts produce one dashboard alert. Approve/reject logged.

---

## Phase 10 — React Dashboard

**Status** → Pending

**Deliverables:**
- `frontend/src/App.tsx` — single WebSocket hook with reconnect
- Panels: Telemetry · Prediction · Risk · RAG Evidence · LLM Narrative · Approval · System Metrics
- Color-coded risk badge; expiry countdown on pending actions

**Done when:** User can follow full telemetry → prediction → risk → RAG → narrative → approval flow visually.

---

## Phase 11 — Evaluation & Wrap-Up

**Status** → Pending

**Deliverables:**
- `outputs/reports/final_eval_report.json` — E2E pipeline metrics
- `outputs/reports/llm_comparison_report.json` — ≥2 models on same context
- `LEARNING_LOG.md` — one insight per phase

**Done when:** Report generated. At least 2 LLMs compared on JSON validity, latency, groundedness.

---
