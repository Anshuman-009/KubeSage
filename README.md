# POC-RTML-AGENT-001

Real-Time ML + RAG + LLM Alert Intelligence for Kubernetes Telemetry.

---

## What this is

A two-application POC that chains: live telemetry → XGBoost prediction → risk agent → RAG retrieval → LLM narrative → human-in-the-loop alert.

```text
mock-kube-telemetry-app/    → streams Kubernetes-style pod metrics, logs, events
poc-intelligence-app/       → ML prediction, RAG, LLM, agents, React dashboard
shared/                     → Pydantic contracts shared across both apps
dataset/                    → synthetic production-style training + runtime data
ml_training/                → feature engineering + XGBoost training scripts
models/                     → trained model artifacts + feature schema
```

---

## Architecture reference

`docs/POC-RTML-AGENT-001-updated.md` — full system design, agent definitions, schema contracts, folder structure.

---

## Phase progress

`PHASES.md` — development checklist (11 phases).

`docs/PHASE_WISE_DOC.md` — deep documentation per phase: Conceptual, HLD, LLD, DFD.

---

## Dataset

Synthetic production-style dataset in `dataset/`:

```text
dataset/source/     → raw telemetry CSV, app logs, k8s events, runbooks, incidents
dataset/derived/    → ML features + training labels (pre-computed)
dataset/runtime/    → runtime log sinks (populated during live runs)
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Verify Phase 1

```bash
pytest tests/test_contracts.py -v
```

Expected: **10 passed**

## Verify Phase 2

```bash
python -m ml_training.export_feature_schema
pytest tests/test_build_features.py -v
```

Expected: **5 passed** + `models/feature_schema.json` written
