# KubeSage

**Real-time ML + RAG + LLM alert intelligence for Kubernetes telemetry.**

KubeSage is a POC that simulates how a production SRE assistant would work: detect workload risk from live pod metrics, ground predictions in operational evidence, explain what is happening in plain language, and route risky actions through human approval.

---

## The idea

Kubernetes operators often see symptoms — rising memory, probe failures, error spikes — before they understand *why* or *what to do*. KubeSage explores an end-to-end pattern for closing that gap:

1. **Predict** — Train XGBoost models on historical telemetry to forecast memory breach risk and future usage.
2. **Reason** — Agent-style components decide severity and whether to escalate.
3. **Ground** — RAG retrieves relevant runbooks, incidents, logs, and deployment notes.
4. **Explain** — A local LLM turns prediction + evidence into an operator-readable narrative.
5. **Act safely** — Alerts and recommended actions go through human-in-the-loop approval before anything risky runs.

The system is built as **two cooperating apps** plus shared contracts:

```text
Mock Kube Telemetry App          KubeSage Intelligence App
(simulates a cluster)     →      (ML, agents, RAG, LLM, alerts)
                                          ↓
                                 React dashboard (planned)
```

This is not a full production platform yet. It is a focused foundation for learning how intelligence enters a live software system — with a clear path toward real Prometheus/OpenTelemetry sources, production runbooks, and a full KubeSage UI.

---

## How it works

```text
Historical / synthetic data
  ├── pod telemetry, app logs, k8s events
  ├── failure labels, runbooks, incidents
        ↓
Feature engineering (30s rolling window)
        ↓
XGBoost training → exported model artifacts
        ↓

Live stream (Mock Kube App)
        ↓
Buffer → features → prediction
        ↓
Risk agent → RAG evidence → LLM narrative
        ↓
Alert + human approval → runtime logs → future retraining
```

**Primary prediction targets:**

| Model | Question it answers |
|-------|---------------------|
| `memory-breach-xgb-v1` (classifier) | Will memory cross 90% of limit in the next 30 seconds? |
| `future-memory-xgb-v1` (regressor) | What will memory usage (MB) be 30 seconds from now? |

---

## Repository layout

```text
mock-kube-telemetry-app/    Streams Kubernetes-style pod metrics, logs, and events
poc-intelligence-app/       ML prediction, RAG, LLM agents, and React dashboard (planned)
shared/                     Pydantic contracts shared across both apps
dataset/                    Synthetic production-style training + runtime data
ml_training/                Feature engineering and XGBoost training scripts
models/                     Trained artifacts, feature schema, and model card
tests/                      Contract, feature, and model validation tests
docs/                       System design and phase-wise architecture docs
```

---

## Progress

Development follows an 11-phase roadmap. See [`PHASES.md`](PHASES.md) for the full checklist and [`docs/PHASE_WISE_DOC.md`](docs/PHASE_WISE_DOC.md) for deep per-phase architecture notes.

### Completed

| Phase | Focus | Highlights |
|-------|-------|------------|
| **1 — Setup & contracts** | Project skeleton and shared schemas | Two-app folder structure; Pydantic contracts for telemetry, logs, k8s events, predictions, risk, LLM narratives, alerts, and human feedback; contract tests passing |
| **2 — Feature engineering** | Train-serve feature pipeline | `build_features()` over 30s windows (rolling averages, slopes, ratios, std); `models/feature_schema.json`; validated against `dataset/derived/derived_features.csv` |
| **3 — ML training** | XGBoost classifier + regressor | Trained models exported to `models/`; model card and metrics; classifier F1 ≈ 0.99 / AUC ≈ 1.0 on validation; regressor R² ≈ 0.997 |

**Shipped artifacts so far:**

- `shared/contracts/` — canonical event and pipeline schemas
- `ml_training/build_features.py`, `train_classifier.py`, `train_regressor.py`
- `models/memory_breach_xgb_classifier.json`, `future_memory_xgb_regressor.json`
- `models/feature_schema.json`, `training_metrics.json`, `model_card.md`
- Synthetic dataset pack under `dataset/` (6 service scenarios: memory leak, CPU saturation, DB pool exhaustion, etc.)

### Up next — Phase 4: Mock Kube Telemetry App

The foundation (contracts, features, models) is in place. **Phase 4 is the current focus**: build the FastAPI app that replays and streams live telemetry so the intelligence pipeline can be wired end-to-end.

Planned deliverables:

- `mock-kube-telemetry-app/app/main.py` — FastAPI service
- WebSocket endpoint for telemetry, logs, and k8s events
- Scenario runner: `normal`, `memory_spike`, `cpu_spike`, `error_spike`
- Controlled spike injection for testing prediction and alerting

**Done when:** a WebSocket client receives 60 seconds of live telemetry for one scenario.

### Planned (Phases 5–11)

| Phase | Focus |
|-------|-------|
| 5 | Stream ingestion, 30s buffer, and live prediction service |
| 6 | Risk reasoning agent (NORMAL / WATCH / HIGH / CRITICAL) |
| 7 | RAG retrieval over runbooks, incidents, logs, deployment notes |
| 8 | LLM narrative agent (local Ollama, grounded JSON output) |
| 9 | Action / alert agent with human approve / reject flow |
| 10 | React dashboard (telemetry → prediction → narrative → approval) |
| 11 | Evaluation reports and LLM comparison |

---

## Dataset

Synthetic, production-shaped data in `dataset/` — telemetry, logs, events, runbooks, and incidents are connected across six scenarios so ML training and RAG retrieval behave realistically.

```text
dataset/source/     Raw telemetry CSV, app logs, k8s events, runbooks, incidents
dataset/derived/    ML features + training labels (pre-computed)
dataset/runtime/    Runtime log sinks (populated during live runs)
```

Details: [`dataset/README.md`](dataset/README.md)

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Verify completed phases

**Phase 1 — contracts**

```bash
pytest tests/test_contracts.py -v
```

Expected: **10 passed**

**Phase 2 — feature engineering**

```bash
python -m ml_training.export_feature_schema
pytest tests/test_build_features.py -v
```

Expected: **5 passed** + `models/feature_schema.json` written

**Phase 3 — model training**

```bash
pytest tests/test_train_models.py -v
```

Expected: models load and produce valid inference output

---

## Documentation

| Doc | Description |
|-----|-------------|
| [`docs/KubeSage-design.md`](docs/KubeSage-design.md) | Full system design, agent definitions, schema contracts, folder structure |
| [`PHASES.md`](PHASES.md) | Phase tracker and deliverables |
| [`docs/PHASE_WISE_DOC.md`](docs/PHASE_WISE_DOC.md) | Conceptual, HLD, LLD, and DFD notes per phase |
| [`docs/poc_planning.md`](docs/poc_planning.md) | Original POC planning and learning goals |
| [`models/model_card.md`](models/model_card.md) | Model card for trained XGBoost artifacts |
