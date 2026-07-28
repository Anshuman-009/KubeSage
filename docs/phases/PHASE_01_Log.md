# Phase 01 — Project Setup & Contracts

## Overview

Phase 1 establishes the project skeleton and the data contract layer for POC-RTML-AGENT-001. Two applications — a mock telemetry producer and an intelligence consumer — share a single canonical schema package. All downstream phases (feature engineering, ML, agents, UI) depend on these contracts being stable and validated before any business logic is written.

---

## Conceptual Foundation

In a distributed system, components communicate by exchanging structured messages. Without an agreed schema, a producer can change a field name and the consumer breaks silently — no exception, just wrong data.

This POC has two applications with a hard boundary between them:

```text
Mock Kube Telemetry App  ──JSON events──►  POC Intelligence App
     (producer)                                  (consumer)
```

The contract layer is the shared language at that boundary. It answers: what fields exist, what types they have, what values are valid, and what happens when an unknown field arrives.

Contracts are defined once in `shared/contracts/` and imported by both apps. Intelligence-only schemas (features, prediction, risk, LLM, alert) live in the consumer only — they never cross the app boundary.

---

## High-Level Design (HLD)

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        POC-RTML-AGENT-001                           │
├──────────────────────────────┬──────────────────────────────────────┤
│   mock-kube-telemetry-app/   │      poc-intelligence-app/           │
│                              │                                      │
│   schemas/ ──imports──┐      │   backend/app/schemas/ ──imports──┐  │
│                       │      │                                   │  │
│                       ▼      │                                   ▼  │
│              ┌────────────────────────────────────┐                 │
│              │         shared/contracts/            │                 │
│              │  TelemetryEvent  AppLogEvent        │                 │
│              │  KubeEvent       StrictModel        │                 │
│              └────────────────────────────────────┘                 │
│                              │                                      │
│                              │  intelligence-only (consumer)         │
│                              ▼                                      │
│              FeatureVector → PredictionEvent → RiskDecision         │
│              → LlmNarrative → AlertEvent → ActionEvent → Feedback   │
└──────────────────────────────┴──────────────────────────────────────┘
```

Contract version `1.0.0` is stamped on every schema. Future phases can evolve schemas by bumping this version.

---

## Low-Level Design (LLD)

```text
StrictModel (base.py)
  │
  ├── extra="forbid"          reject unknown JSON keys at boundary
  ├── str_strip_whitespace    normalize string inputs
  └── CONTRACT_VERSION        default "1.0.0" on every model

Stream contracts (shared/contracts/)
  │
  ├── TelemetryEvent
  │     type: Literal["telemetry"]
  │     memory_mb, cpu_pct, request_rate, error_rate, ...
  │
  ├── AppLogEvent
  │     type: Literal["app_log"]
  │     level: LogLevel enum, message, trace_id, latency_ms
  │
  └── KubeEvent
        type: Literal["kube_event"]
        reason, message

Intelligence contracts (poc-intelligence-app/.../schemas/)
  │
  ├── FeatureVector          30+ rolling-window ML features
  ├── PredictionEvent        breach_probability + predicted_memory_mb_30s
  │     └── @model_validator  breach_likely must match prob >= 0.5
  ├── RiskDecision           severity enum + routing flags
  ├── LlmNarrative           strict JSON explanation fields
  ├── AlertEvent             UI-facing alert payload
  ├── ActionEvent            recommended action + approval state
  └── HumanFeedbackEvent     approve/reject audit record
```

Re-export pattern:

```text
shared/contracts/telemetry.py  ──defines──►  TelemetryEvent
        ▲                                           ▲
        │ import                                    │ import
mock-kube-telemetry-app/schemas/          poc-intelligence-app/.../telemetry.py
   (producer uses class)                    (consumer uses same class)
```

Both apps hold a reference to the identical Python class object — not a copy.

---

## Data Flow Diagram (DFD)

### Stream boundary (producer → consumer)

```text
Mock Kube App
     │
     │  WebSocket JSON
     ▼
┌──────────────────────────────────────────────────────────────┐
│ TelemetryEvent                                               │
│   type="telemetry"                                           │
│   pod_name, namespace, container_name                        │
│   memory_mb, memory_limit_mb, cpu_pct                        │
│   request_rate, error_rate, restart_count                    │
└──────────────────────────┬───────────────────────────────────┘
                           │  model_validate()
                           ▼
              Stream Ingestion Service (Phase 5)
                           │
                           ▼
              Telemetry Buffer (30s deque)
```

```text
Mock Kube App
     │
     ▼
┌──────────────────────────┐     ┌──────────────────────────┐
│ AppLogEvent              │     │ KubeEvent                │
│   level, message         │     │   reason, message        │
│   trace_id, latency_ms   │     │   pod_name, timestamp    │
└────────────┬─────────────┘     └────────────┬─────────────┘
             │                                 │
             └──────────────► Archive + RAG context (Phase 7+)
```

### Intelligence pipeline (consumer internal)

```text
FeatureVector
  memory_current_mb, memory_slope_30s, memory_ratio_current, ...
        │
        ▼
PredictionEvent
  breach_probability, predicted_memory_mb_30s, model_versions
        │
        ▼
RiskDecision
  severity, alert_required, rag_required, human_approval_required
        │
        ├──────────────────────┐
        ▼                      ▼
  LlmNarrative            AlertEvent
  alert_title,              alert_id, severity,
  evidence_used,             prediction_summary
  recommended_actions
        │
        ▼
  ActionEvent
  action_id, action_type, recommended_action, status
        │
        ▼
  HumanFeedbackEvent
  decision (approve|reject), decided_by, decided_at
```

---

## Architecture Decisions

**Decision 1: Single `shared/contracts/` package as source of truth**
→ Reason: Prevents producer/consumer schema drift. Both apps import the same Python class.
→ Alternative: Duplicate schema files in each app. Rejected — drift is silent and inevitable.

**Decision 2: `extra="forbid"` on all boundary schemas**
→ Reason: Unknown fields fail loudly at validation time instead of being silently ignored.
→ Alternative: `extra="ignore"` (permissive). Rejected for POC boundaries — typos must surface immediately.

**Decision 3: Stream schemas separate from intelligence schemas**
→ Reason: Only three event types cross the app boundary. Pipeline schemas (FeatureVector, PredictionEvent, etc.) are internal to the intelligence app and should not be exposed to the mock producer.
→ Alternative: One mega-schema for everything. Rejected — mixes boundary concerns with internal pipeline concerns.

**Decision 4: `breach_likely` validated against `breach_probability >= 0.5` in schema**
→ Reason: Enforces consistency at the contract level, not just in application code. A prediction event with prob=0.86 and breach_likely=false is structurally invalid.
→ Alternative: Leave consistency to the Prediction Service only. Rejected — contracts should catch invalid states early.

**Decision 5: Intelligence schemas re-export stream types rather than redefine them**
→ Reason: Consumer code imports from `app.schemas` uniformly. Stream types resolve to the same shared class.
→ Alternative: Consumer imports directly from `shared.contracts` everywhere. Rejected — splits import paths across the codebase.

---

## What Was Built

```text
shared/contracts/
  base.py              StrictModel + CONTRACT_VERSION = "1.0.0"
  telemetry.py         TelemetryEvent
  app_log.py           AppLogEvent + LogLevel enum
  kube_event.py        KubeEvent
  __init__.py          public exports

mock-kube-telemetry-app/
  schemas/__init__.py  re-exports stream contracts (producer)
  app/.gitkeep         placeholder for Phase 4 FastAPI app

poc-intelligence-app/backend/app/
  schemas/
    telemetry.py … feedback.py   stream re-exports + 7 pipeline schemas
  ingestion/.gitkeep             placeholder for Phase 5
  agents/.gitkeep                placeholder for Phase 6+

ml-training/.gitkeep             placeholder for Phase 2
models/.gitkeep                  placeholder for Phase 3

tests/test_contracts.py          10 validation tests
pyproject.toml                     project deps + pytest config
.gitignore                         .utility/, .venv/, __pycache__/
```

---

## Verify

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/test_contracts.py -v
```

Expected output:

```text
10 passed
```

Key assertions covered:
- Each of the 10 schemas validates a known-good JSON payload
- Unknown fields on stream events raise `ValidationError`
- Producer and consumer `TelemetryEvent` are the same class object
