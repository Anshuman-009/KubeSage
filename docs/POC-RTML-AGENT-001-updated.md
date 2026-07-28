# POC-RTML-AGENT-001

## Real-Time ML + RAG + LLM Alert Intelligence for Kubernetes Telemetry

---

## 1. Purpose

This POC is a 10–12 hour learning experiment designed to understand how real-time telemetry can be converted into ML-based prediction, RAG-backed evidence, LLM-readable explanation, and human-safe operational alerts.

This is not the full KubeSage project.

This POC exists to learn:

1. How historical Kubernetes-style telemetry, pod logs, application logs, metrics, and failure events become ML training data.
2. How XGBoost models are trained, exported, loaded, and used inside a live FastAPI application.
3. How live telemetry from a mock Kubernetes cluster is buffered and transformed into rolling-window features.
4. How a trained model can produce near real-time prediction and projection.
5. How RAG retrieves supporting context from runbooks, past incidents, archived logs, and deployment notes.
6. How an LLM converts prediction + evidence into a user-understandable alert narrative.
7. How only selected components behave as decision-making AI agents.
8. How human intervention is introduced before risky operational actions.
9. How runtime telemetry and outcomes are stored for replay, evaluation, and future model improvement.
10. How different locally hosted LLMs behave on the same alert context.

---

## 2. Final POC Definition

POC-RTML-AGENT-001 uses a two-application setup.

```text
1. Mock Kube Telemetry App
   -> mimics a Kubernetes cluster by streaming pod metrics, app logs, Kubernetes-style events, and controlled failure spikes.

2. POC Intelligence App
   -> receives telemetry from the mock app, buffers live data, builds features, runs trained XGBoost models, invokes decision-making AI agents, retrieves evidence through RAG, calls local LLMs, emits alerts, and displays everything in a React dashboard.
```

The goal is to understand:

```text
Realtime prediction based on trained models
LLM response generation for user understanding
Agentic decision flow around risk, explanation, alerting, and human approval
```

---

## 3. Architecture Overview

```text
Historical / Synthetic Data
  ├── pod telemetry
  ├── application logs
  ├── Kubernetes events
  ├── failure labels
  └── past incident notes
        ↓
Feature Engineering
        ↓
Train XGBoost Models
        ↓
Export Model Artifacts
        ↓

┌──────────────────────────────┐
│ Mock Kube Telemetry App      │
│ - streams pod metrics        │
│ - streams app logs           │
│ - streams Kube-like events   │
│ - injects dummy spikes       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ POC Intelligence App         │
│ - receives telemetry         │
│ - buffers 30-sec window      │
│ - builds features            │
│ - runs XGBoost prediction    │
│ - triggers AI agents         │
│ - retrieves RAG evidence     │
│ - calls local LLM            │
│ - emits alert + narrative    │
│ - logs runtime outcomes      │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ React Dashboard              │
│ - live telemetry             │
│ - prediction/projection      │
│ - RAG evidence               │
│ - LLM narrative              │
│ - approval/reject controls   │
└──────────────────────────────┘
```

---

## 4. Application 1 — Mock Kube Telemetry App

### 4.1 Purpose

The Mock Kube Telemetry App acts like a fake Kubernetes cluster.

It does not contain ML, RAG, LLM, or decision-making logic.

Its job is to produce realistic live inputs.

### 4.2 Responsibilities

```text
simulate namespaces
simulate pods
simulate pod CPU/memory/network metrics
simulate request rate and error rate
simulate application logs
simulate Kubernetes-style events
inject controlled spikes
stream telemetry to the POC Intelligence App
```

### 4.3 Example Scenarios

```text
normal workload
memory leak after deployment
CPU spike
error-rate spike
pod restart
OOMKilled-style event
node pressure-style event
```

### 4.4 Suggested Endpoints

```text
GET  /health
GET  /scenarios
POST /scenario/start
POST /scenario/stop
WS   /ws/kube-stream
```

### 4.5 Example Telemetry Event

```json
{
  "type": "telemetry",
  "timestamp": "00:31",
  "namespace": "payments",
  "pod_name": "payment-api-7d9f",
  "container_name": "payment-api",
  "memory_mb": 842,
  "memory_limit_mb": 1024,
  "cpu_pct": 81,
  "request_rate": 210,
  "error_rate": 19,
  "restart_count": 1,
  "deployment_age_minutes": 12
}
```

### 4.6 Example Log Event

```json
{
  "type": "app_log",
  "timestamp": "00:33",
  "pod_name": "payment-api-7d9f",
  "level": "ERROR",
  "message": "request timeout while calling ledger-service",
  "trace_id": "trace-001",
  "latency_ms": 2300
}
```

### 4.7 Example Kubernetes Event

```json
{
  "type": "kube_event",
  "timestamp": "00:42",
  "pod_name": "payment-api-7d9f",
  "reason": "OOMKilled",
  "message": "Container was terminated due to memory pressure"
}
```

---

## 5. Application 2 — POC Intelligence App

### 5.1 Purpose

The POC Intelligence App is the actual AI/ML system.

It receives live telemetry from the Mock Kube Telemetry App and performs:

```text
stream ingestion
30-second buffering
feature building
ML prediction and projection
risk reasoning
RAG evidence retrieval
LLM explanation
alerting
human approval handling
runtime evaluation
```

### 5.2 Suggested Stack

```text
FastAPI backend
React frontend
XGBoost ML models
local markdown RAG archive
nomic-embed-text for embeddings
local hosted LLM API
WebSocket for UI events
JSONL runtime archive
```

---

## 6. Decision Boundary: Agents vs Services

This POC should not call every component an agent.

Only three components are decision-making AI agents.

```text
Decision-making AI agents:
1. Risk Reasoning Agent
2. LLM Narrative Agent
3. Action / Alert Agent
```

Everything else is a supporting service or tool.

```text
Supporting services/tools:
- Stream Ingestion Service
- Telemetry Buffer Service
- Feature Builder Service
- Prediction Service
- RAG Retrieval Service
- LLM API Client
- Runtime Archive Service
- Evaluation Logger Service
```

Clean rule:

```text
Services collect, transform, compute, retrieve, and log.
Agents reason, decide, explain, and choose next steps.
```

---

## 7. The Three AI Agents

---

### 7.1 Risk Reasoning Agent

This is the main decision-making agent in the POC.

It receives:

```text
latest telemetry state
rolling feature vector
XGBoost classifier output
XGBoost regressor output
recent logs/events summary
```

It decides:

```text
Is this NORMAL, WATCH, HIGH, or CRITICAL?
Should RAG be triggered?
Should an alert be emitted?
Is human intervention required?
What evidence should be requested?
```

Example output:

```json
{
  "severity": "HIGH",
  "alert_required": true,
  "rag_required": true,
  "human_approval_required": false,
  "reason": "High breach probability and projected memory ratio above warning threshold",
  "evidence_query": "payment-api high memory slope high error rate recent deployment possible memory leak"
}
```

---

### 7.2 LLM Narrative Agent

This agent converts technical findings into a user-understandable explanation.

It receives:

```text
risk reasoning output
ML prediction/projection
retrieved RAG context
live telemetry summary
recent logs/events summary
```

It decides:

```text
Which explanation style is needed?
Which evidence should be included?
How much uncertainty should be stated?
Which local LLM should be used for this response?
```

It calls the LLM through the LLM API client.

Output format:

```json
{
  "alert_title": "Payment API memory breach risk",
  "severity": "HIGH",
  "prediction_summary": "The pod has an 86% probability of breaching memory threshold. The model projects memory to reach 940MB within the next 30 seconds.",
  "evidence_used": [
    "incident_2026_05_23_memory_growth.md",
    "runbook_memory_spike.md"
  ],
  "likely_cause": "Possible memory growth after recent deployment",
  "recommended_actions": [
    "Check recent deployment changes",
    "Inspect memory usage across replicas",
    "Review application logs for timeout/error growth",
    "Prepare rollback or scaling if pressure continues"
  ],
  "confidence": "medium-high",
  "uncertainty": "This prediction is based on a short rolling window and synthetic POC telemetry."
}
```

---

### 7.3 Action / Alert Agent

This agent decides what should happen after risk and explanation are ready.

It receives:

```text
risk assessment
LLM narrative
recommended actions
human approval policy
current alert state
```

It decides:

```text
Should the UI receive an alert?
Should duplicate alerts be suppressed?
Should this require human approval?
Which action buttons should be shown?
Should a final summary event be emitted?
```

Automatic actions allowed:

```text
send alert
show evidence
show recommended action
log incident candidate
prepare approval request
```

Actions that require human approval:

```text
restart pod
scale deployment
rollback deployment
create ticket
notify external system
```

For this POC, approved actions only get logged.

No real Kubernetes mutation is performed.

---

## 8. Supporting Services and Tools

### 8.1 Stream Ingestion Service

Receives live events from the Mock Kube Telemetry App.

Responsibilities:

```text
connect to mock stream
validate payloads
normalize event shape
store raw event
forward telemetry to buffer
forward logs/events to archive
```

---

### 8.2 Telemetry Buffer Service

Maintains a 30-second rolling window.

Responsibilities:

```text
hold recent telemetry
expire old telemetry
provide latest window to feature builder
```

---

### 8.3 Feature Builder Service

Converts rolling telemetry into model-ready features.

Responsibilities:

```text
calculate rolling averages
calculate slopes
calculate ratios
calculate standard deviation
validate against feature_schema.json
```

---

### 8.4 Prediction Service

Loads trained XGBoost models and performs inference.

Models:

```text
XGBClassifier -> breach probability
XGBRegressor  -> future memory projection
```

Output:

```json
{
  "breach_probability": 0.86,
  "breach_likely": true,
  "predicted_memory_mb_30s": 940,
  "predicted_memory_ratio_30s": 0.91,
  "model_versions": {
    "classifier": "memory-breach-xgb-v1",
    "regressor": "future-memory-xgb-v1"
  }
}
```

---

### 8.5 RAG Retrieval Service

RAG is a service/tool, not one of the decision agents.

It is triggered by the Risk Reasoning Agent.

It retrieves:

```text
runbooks
past incidents
archived log summaries
Kubernetes event explanations
deployment risk notes
```

---

### 8.6 LLM API Client

This is a tool used by the LLM Narrative Agent.

Available local models:

```text
llama3:latest
nomic-embed-text:latest
qwen3-coder:latest
qwen3:8b
qwen3:4b
qwen2.5:latest
gpt-oss:20b
llama3.2:3b
```

Suggested roles:

```text
nomic-embed-text:latest -> embeddings for RAG
qwen3:8b                -> default narrative model
qwen3:4b                -> fast lightweight explanation
qwen2.5:latest          -> fallback general explanation
llama3:latest           -> baseline comparison
llama3.2:3b             -> low-latency quick summary
gpt-oss:20b             -> deeper final analysis
qwen3-coder:latest      -> optional log/code/config reasoning
```

---

### 8.7 Runtime Archive Service

Stores all runtime events for replay, evaluation, and future retraining.

Stores:

```text
raw telemetry
raw logs
Kubernetes-style events
feature vectors
prediction outputs
risk decisions
retrieved RAG context
LLM responses
alerts
human approval/rejection
actual outcomes
```

---

### 8.8 Evaluation Logger Service

Tracks system quality.

Metrics:

```text
ML latency
prediction quality
RAG retrieval latency
RAG relevance
LLM latency
LLM JSON validity
LLM groundedness
alert latency
human feedback
actual outcome comparison
```

---

## 9. What We Are Predicting

This POC focuses on memory pressure prediction first.

### 9.1 Classification

Question:

```text
Will this pod breach the memory threshold in the next 30 seconds?
```

Model:

```text
XGBClassifier
```

Output:

```json
{
  "breach_probability": 0.87,
  "breach_likely": true,
  "prediction_horizon": "next_30_seconds"
}
```

### 9.2 Projection / Regression

Question:

```text
What will the memory usage be after 30 seconds?
```

Model:

```text
XGBRegressor
```

Output:

```json
{
  "predicted_memory_mb_30s": 948,
  "predicted_memory_ratio_30s": 0.92
}
```

### 9.3 Operational Interpretation

The Risk Reasoning Agent interprets ML outputs into operational severity.

Example:

```json
{
  "estimated_seconds_to_threshold": 22,
  "severity": "HIGH",
  "human_approval_required": false
}
```

---

## 10. Dataset Plan

### 10.1 Primary Dataset

Use synthetic Kubernetes-style telemetry for the first version.

Reason:

```text
controlled spike behavior
easy labeling
repeatability
clear failure scenarios
no dependency on noisy external datasets
```

### 10.2 Optional External Dataset Exploration

After the synthetic version works, explore:

```text
Kaggle Kubernetes anomaly datasets
AIOps failure detection datasets
synthetic Kubernetes/Istio log datasets
OpenTelemetry Demo-generated telemetry
public log anomaly datasets
```

External datasets should not block the first POC.

---

## 11. Historical Data Needed

### 11.1 Pod Telemetry

```text
timestamp
pod_name
namespace
container_name
memory_usage_mb
memory_limit_mb
cpu_usage_percent
cpu_limit_percent
network_rx_bytes
network_tx_bytes
disk_read_bytes
disk_write_bytes
request_rate
error_rate
restart_count
deployment_age_minutes
```

### 11.2 Application Logs

```text
timestamp
pod_name
service_name
log_level
message
trace_id
request_id
error_type
latency_ms
```

### 11.3 Kubernetes Events

```text
timestamp
pod_name
namespace
event_type
event_reason
event_message
```

Example reasons:

```text
OOMKilled
CrashLoopBackOff
ReadinessProbeFailed
LivenessProbeFailed
NodeMemoryPressure
Evicted
DeploymentRollout
ScalingEvent
```

### 11.4 Incident Archive

```text
incident_id
incident_date
service_name
symptoms
root_cause
resolution
related_metrics
related_logs
```

### 11.5 Labels and Targets

Classification labels:

```text
label_memory_breach_next_30s
label_pod_restart_next_30s
label_error_spike_next_30s
```

Regression targets:

```text
target_memory_mb_30s
target_memory_ratio_30s
target_cpu_pct_30s
```

For the first POC, only use:

```text
label_memory_breach_next_30s
target_memory_mb_30s
target_memory_ratio_30s
```

---

## 12. Feature Engineering Plan

Raw telemetry should not go directly to the model.

The POC should generate rolling-window features from the 30-second buffer.

### 12.1 Window Features

```text
latest value
5-second average
10-second average
30-second average
5-second slope
10-second slope
30-second slope
max value
min value
standard deviation
```

### 12.2 Feature Set

```text
memory_current_mb
memory_ratio_current
memory_avg_5s
memory_avg_10s
memory_avg_30s
memory_slope_5s
memory_slope_10s
memory_slope_30s
memory_std_30s

cpu_current_pct
cpu_avg_5s
cpu_avg_10s
cpu_avg_30s
cpu_slope_10s

error_rate_current
error_rate_avg_5s
error_rate_avg_30s
error_rate_slope_10s

request_rate_current
request_rate_avg_30s
request_rate_slope_10s

restart_count
deployment_age_minutes
recent_deployment_flag
memory_limit_mb
```

### 12.3 Important Rule

The same feature builder must be used in:

```text
training pipeline
runtime inference pipeline
```

This prevents training/runtime feature drift.

---

## 13. ML Model Plan

### 13.1 Model Family

Use:

```text
XGBoost
```

Models:

```text
XGBClassifier
XGBRegressor
```

### 13.2 Classifier Metrics

```text
accuracy
precision
recall
F1 score
ROC-AUC
confusion matrix
feature importance
```

### 13.3 Regressor Metrics

```text
MAE
RMSE
R2 score
prediction error distribution
```

### 13.4 Model Artifacts

Export:

```text
models/memory_breach_xgb_classifier.json
models/future_memory_xgb_regressor.json
models/feature_schema.json
models/training_metrics.json
models/model_card.md
```

---

## 14. RAG Pipeline Plan

### 14.1 RAG Purpose

RAG does not predict.

RAG grounds the prediction with evidence.

The ML model says:

```text
This pod is likely to breach memory threshold.
```

The RAG service retrieves:

```text
Which runbooks, past incidents, logs, or deployment notes support this?
```

The LLM Narrative Agent explains:

```text
Why the alert matters, what evidence supports it, and what should be checked next.
```

### 14.2 RAG Sources

```text
docs/runbooks/runbook_memory_spike.md
docs/runbooks/runbook_oomkill.md
docs/runbooks/runbook_crashloopbackoff.md
docs/incidents/incident_2026_05_23_memory_growth.md
docs/incidents/incident_2026_05_28_api_timeout.md
docs/k8s-events/oomkilled.md
docs/k8s-events/node_memory_pressure.md
docs/deployments/deployment_risk_notes.md
docs/log-patterns/high_error_rate.md
```

### 14.3 Retrieval Approach

Start with:

```text
keyword retrieval
```

Then add:

```text
embedding retrieval using nomic-embed-text:latest
```

Then compare both.

### 14.4 RAG Trigger Policy

```text
NORMAL   -> no RAG
WATCH    -> optional lightweight retrieval
HIGH     -> retrieve runbook + incident evidence
CRITICAL -> retrieve evidence + LLM explanation + human review
```

---

## 15. LLM Usage Plan

### 15.1 LLM Role

The LLM should not predict.

The LLM should:

```text
explain the prediction
use RAG evidence
summarize operational risk
recommend actions
mention uncertainty
return strict JSON for UI
```

### 15.2 LLM Output Contract

```json
{
  "alert_title": "",
  "severity": "",
  "prediction_summary": "",
  "evidence_used": [],
  "likely_cause": "",
  "recommended_actions": [],
  "requires_human_approval": false,
  "confidence": "",
  "uncertainty": ""
}
```

### 15.3 LLM Metrics

```text
model_name
latency_ms
json_valid
retry_count
response_length
groundedness_score
actionability_score
hallucination_flag
```

---

## 16. Human Intervention Plan

Agents can automatically:

```text
observe telemetry
run prediction
retrieve evidence
generate explanation
send alert
prepare recommended action
log incident candidate
```

Agents cannot automatically:

```text
restart pod
scale deployment
rollback deployment
create ticket
notify external system
```

Those require human approval.

For this POC, human approval only logs the decision.

No real Kubernetes action is executed.

Example approval payload:

```json
{
  "action_id": "action-001",
  "recommended_action": "Scale payment-api from 2 to 4 replicas",
  "requires_human_approval": true,
  "status": "pending"
}
```

---

## 17. React Interface Plan

Single-page dashboard:

```text
Live Telemetry Panel
Prediction / Projection Panel
Risk Reasoning Panel
RAG Evidence Panel
LLM Narrative Panel
Action / Approval Panel
Runtime Metrics Panel
```

UI behavior:

```text
1. Show live telemetry from Mock Kube App.
2. Show prediction and projected memory.
3. Show risk decision.
4. Show immediate alert.
5. Show retrieved evidence.
6. Show LLM narrative after it arrives.
7. Show recommended action.
8. Allow approve/reject for human-gated actions.
```

Important behavior:

```text
ML alert should appear before LLM explanation.
```

Reason:

```text
ML inference is fast.
RAG + LLM may take longer.
```

---

## 18. Runtime Data Storage and Future Learning Loop

Live inputs should be stored.

Runtime archive:

```text
outputs/runtime/raw_telemetry_log.jsonl
outputs/runtime/app_log.jsonl
outputs/runtime/kube_event_log.jsonl
outputs/runtime/feature_log.jsonl
outputs/runtime/prediction_log.jsonl
outputs/runtime/risk_decision_log.jsonl
outputs/runtime/rag_log.jsonl
outputs/runtime/llm_log.jsonl
outputs/runtime/alert_log.jsonl
outputs/runtime/human_feedback_log.jsonl
outputs/runtime/outcome_log.jsonl
```

Future learning loop:

```text
live telemetry received
    ↓
prediction made
    ↓
alert emitted
    ↓
action recommended
    ↓
human approves/rejects
    ↓
actual outcome observed
    ↓
prediction correctness measured
    ↓
runtime data becomes future training/evaluation data
```

Important rule:

```text
The LLM does not learn automatically from the stream.
The system improves when runtime data is stored, labeled, evaluated, and used for retraining.
```

---

## 19. Metrics Plan

### 19.1 ML Training Metrics

Classifier:

```text
accuracy
precision
recall
F1 score
ROC-AUC
confusion matrix
feature importance
```

Regressor:

```text
MAE
RMSE
R2 score
prediction error distribution
```

### 19.2 Runtime ML Metrics

```text
inference_latency_ms
breach_probability
predicted_memory_mb_30s
predicted_memory_ratio_30s
prediction_status
detection_second
actual_breach_second
lead_time_seconds
```

### 19.3 RAG Metrics

```text
retrieval_latency_ms
retrieved_doc_count
retrieval_scores
expected_doc_found
context_length
```

### 19.4 LLM Metrics

```text
model_name
latency_ms
json_valid
retry_count
groundedness_score
actionability_score
hallucination_flag
```

### 19.5 Agent Metrics

```text
risk_reasoning_latency_ms
risk_decision
rag_triggered
human_approval_required
action_selected
alert_suppressed_duplicate
```

### 19.6 WebSocket / UI Metrics

```text
connection_duration_seconds
events_sent
telemetry_events_sent
prediction_events_sent
alerts_sent
llm_explanations_sent
dropped_events
alert_delivery_latency_ms
```

### 19.7 End-to-End Metrics

```text
spike_start_second
ml_detection_second
risk_decision_second
alert_emit_second
rag_complete_second
llm_complete_second
human_feedback_second
total_explanation_latency_ms
```

---

## 20. Project Folder Structure

```text
poc-rtml-agent-rag/
  README.md

  mock-kube-telemetry-app/
    app/
      main.py
      scenarios/
        normal_workload.py
        memory_leak_after_deployment.py
        cpu_spike.py
        error_spike.py
        oomkilled_event.py
      stream/
        telemetry_streamer.py
        log_streamer.py
        event_streamer.py
      schemas/
        telemetry.py
        app_log.py
        kube_event.py
    data/
      scenarios/
        spike_scenario_01.jsonl
    README.md

  poc-intelligence-app/
    backend/
      app/
        main.py

        ingestion/
          stream_ingestion_service.py

        buffer/
          telemetry_buffer_service.py

        features/
          feature_builder_service.py

        prediction/
          prediction_service.py
          model_loader.py

        rag/
          document_loader.py
          keyword_retriever.py
          embedding_retriever.py
          query_builder.py
          rag_retrieval_service.py

        llm/
          llm_api_client.py
          prompt_templates.py

        agents/
          risk_reasoning_agent.py
          llm_narrative_agent.py
          action_alert_agent.py

        websocket/
          connection_manager.py
          event_types.py

        archive/
          runtime_archive_service.py

        evaluation/
          evaluation_logger_service.py

        schemas/
          telemetry.py
          features.py
          prediction.py
          risk.py
          rag.py
          llm.py
          alert.py
          action.py
          feedback.py

    frontend/
      package.json
      src/
        App.tsx
        components/
          LiveTelemetryPanel.tsx
          PredictionPanel.tsx
          RiskReasoningPanel.tsx
          RagEvidencePanel.tsx
          LlmNarrativePanel.tsx
          ActionApprovalPanel.tsx
          MetricsPanel.tsx

    ml-training/
      generate_synthetic_data.py
      build_features.py
      train_classifier.py
      train_regressor.py
      evaluate_models.py

    data/
      historical/
        synthetic_pod_telemetry.csv
      features/
        training_features.csv

    models/
      memory_breach_xgb_classifier.json
      future_memory_xgb_regressor.json
      feature_schema.json
      training_metrics.json
      model_card.md

    docs/
      runbooks/
        runbook_memory_spike.md
        runbook_oomkill.md
        runbook_crashloopbackoff.md
      incidents/
        incident_2026_05_23_memory_growth.md
        incident_2026_05_28_api_timeout.md
      k8s-events/
        oomkilled.md
        node_memory_pressure.md
      deployments/
        deployment_risk_notes.md
      log-patterns/
        high_error_rate.md

    outputs/
      runtime/
        raw_telemetry_log.jsonl
        app_log.jsonl
        kube_event_log.jsonl
        feature_log.jsonl
        prediction_log.jsonl
        risk_decision_log.jsonl
        rag_log.jsonl
        llm_log.jsonl
        alert_log.jsonl
        human_feedback_log.jsonl
        outcome_log.jsonl
      reports/
        final_eval_report.json
        llm_comparison_report.json
```

---

## 21. Learning-First Development Roadmap

Each phase is a learning unit. The concept comes first. The build is the vehicle for internalizing that concept — not the goal. Code is a byproduct of understanding.

Total estimated time: 10–12 hours

---

### Phase 1 — Contracts: The Language of Distributed Systems

Estimated time:

```text
1 hour
```

What you are learning:

```text
How two separate applications agree on data shapes before any business logic is written.
Why explicit contracts prevent an entire class of silent runtime bugs.
How schema design is the first architectural decision in any data-intensive system.
```

The intuition:

```text
When two applications talk to each other, they need a shared language.
In distributed systems, that language is expressed through schemas and contracts.
If the telemetry producer changes what it emits without telling the consumer,
the consumer breaks silently — no error, just wrong data. Defining contracts first
forces you to think about the boundaries between systems before worrying about
their internal implementations.
```

Nuances and questions to sit with:

```text
- Why do we separate telemetry events, log events, and Kubernetes events into
  distinct schemas rather than one combined blob?
- What is the difference between a strict schema (fails on unexpected fields)
  and a permissive one (ignores them)? Which should you use at a POC boundary and why?
- How does Pydantic enforce schemas at the Python level, and why is that not
  sufficient as a contract for a multi-application system?
- What is schema evolution and why does it matter even at the POC stage?
- Who "owns" the contract when two teams produce and consume the same event type?
```

Tasks:

```text
Create two-app folder structure
Define telemetry event schema (Pydantic)
Define app log event schema (Pydantic)
Define Kubernetes event schema (Pydantic)
Define feature schema (Pydantic)
Define prediction schema (Pydantic)
Define risk decision schema (Pydantic)
Define LLM narrative schema (Pydantic)3.12
Define alert/action schema (Pydantic)
Write one contract validation test per schema with a known-good sample payload
```

Deliverables:

```text
mock-kube-telemetry-app/schemas/
poc-intelligence-app/backend/app/schemas/
README.md
```

Learning verification — answer these before moving to Phase 2:

```text
1. Why do we define schemas before writing any business logic?
2. What breaks if the producer changes a field name without updating the contract?
3. What is the difference between schema validation and type checking?
4. Why does schema-first design enable parallel development on both apps?
5. Give one example of schema evolution and how a versioned contract handles it.
```

---

### Phase 2 — How Raw Telemetry Becomes ML Training Data

Estimated time:

```text
1 hour
```

What you are learning:

```text
How raw operational signals — pod metrics, error counts, memory readings —
become a structured dataset that an ML model can learn from.
What makes data "ML-ready."
How temporal patterns are represented in tabular form.
```

The intuition:

```text
A machine learning model learns from examples. Each example is a row with
features (inputs) and a label (what we want the model to predict).

Raw telemetry is a time series — a continuous sequence of values over time.
To turn it into training examples, you must ask two questions:
  1. What window of time does each row represent?
  2. What happened after that window ends? (the label)

This is the fundamental question of supervised learning for temporal data.
The answer to question 2 must never appear as a feature in question 1 —
that would be label leakage.
```

Nuances and questions to sit with:

```text
- Why do you need both normal patterns and failure patterns in training data?
  What happens if you train only on failures? Only on normal data?
- What is class imbalance? If memory breaches are rare (5% of all rows),
  how does that affect what the model learns?
- What is the difference between a label (what happened) and a target
  (a continuous quantity we want to predict)? When do you use each?
- What is label leakage, and why does it make models look perfect during
  training and fail catastrophically in production?
- Why do we use synthetic data for this POC, and what are the real limitations
  of training on synthetic patterns rather than real incidents?
```

Tasks:

```text
Open ksg_production_style_synthetic_datasets/ and read the README carefully
Trace one row of historical_telemetry.csv to its corresponding row in
  derived_features.csv and its entry in training_labels.csv
Annotate that trace: which columns are raw, which are derived, which is the label
Identify all four synthetic failure patterns (normal / memory_leak / cpu_spike / error_spike)
  and describe in your own words what each one looks like numerically
Document your understanding of the breach label generation logic in a comment block
  before writing any code
```

Deliverables:

```text
notebooks/01_data_exploration.ipynb
  (or data_exploration.py with inline annotations)
```

Learning verification — answer these before moving to Phase 3:

```text
1. What is the feature window for one training example in this dataset?
2. How is the breach label computed? What threshold was used and why?
3. What would happen to training quality if we included future memory readings
   as a feature column?
4. Why do we have multiple synthetic failure patterns rather than just one?
5. What does the XGBRegressor predict that the XGBClassifier does not?
```

---

### Phase 3 — Feature Engineering: Why Raw Numbers Are Not Enough

Estimated time:

```text
1 hour
```

What you are learning:

```text
Why raw sensor readings are rarely sufficient inputs for ML models.
How derived features — rolling averages, slopes, ratios, window aggregates —
capture patterns that raw point-in-time values cannot express.
Why the same feature engineering logic must run identically during training and
at runtime — and what happens when it does not.
```

The intuition:

```text
A model trained on raw values can learn that "memory = 4 GB" might be dangerous.
But it cannot learn that "memory was rising at 200 MB/min for the last 30 seconds"
is more dangerous than a static high reading — unless you give it that trend as a feature.

Rolling-window features encode rate of change and trajectory, not just current state.
These are often the features that actually matter for time-series prediction.

The deeper lesson is this: feature engineering is where domain knowledge gets
encoded into the model. The model can only learn patterns from what you give it.
```

Nuances and questions to sit with:

```text
- What is train-serve skew? Why is it one of the most common causes of ML model
  degradation in production, and how does it happen silently?
- Why must the feature engineering code be shared (or byte-for-byte identical)
  between the training pipeline and the runtime inference path?
- What is a rolling average and how is it different from a simple average
  over the entire history?
- What does a slope feature capture that a rolling average does not?
- What is a memory ratio (used_memory / memory_limit) and why is a ratio more
  generalizable across pods with different memory limits than an absolute value?
- What is a feature schema, and why do we version it as a JSON artifact
  alongside the model?
```

Tasks:

```text
Study each column in derived_features.csv and write one sentence explaining
  what each feature captures and why it might matter for breach prediction
Implement compute_rolling_average(window_values: list[float]) -> float
Implement compute_slope(window_values: list[float]) -> float
Implement compute_memory_ratio(used: float, limit: float) -> float
Implement compute_future_target(future_values: list[float]) -> float
Assemble build_features(telemetry_window: list[dict]) -> dict
Export feature schema as JSON (feature names, types, descriptions)
Run on historical_telemetry.csv and verify output matches derived_features.csv columns
```

Deliverables:

```text
ml-training/build_features.py
models/feature_schema.json
notebooks/02_feature_engineering.ipynb
```

Learning verification — answer these before moving to Phase 4:

```text
1. Define train-serve skew in one sentence. Give one concrete example from this POC
   where it could silently occur.
2. Why would a rolling slope be more informative than the current memory value alone?
3. What happens at runtime when the rolling window has fewer than N data points
   (the cold start problem)?
4. Why do we export the feature schema alongside the model artifact?
5. If you add one new feature to improve the model, list every other part of the
   system that must be updated.
```

---

### Phase 4 — Training ML Models: What XGBoost Learns and Why

Estimated time:

```text
1.5 hours
```

What you are learning:

```text
How gradient boosting works conceptually.
The difference between a classifier and a regressor, and why we need both here.
How to evaluate each model honestly (and why accuracy is the wrong metric for this problem).
Why a trained model is an artifact, not a script.
What a model card is and why it matters for any model that runs in a real system.
```

The intuition:

```text
XGBoost builds many decision trees sequentially. Each new tree corrects the errors
of the previous ones — this is the "gradient boosting" part. Unlike a single
decision tree (which memorizes) or logistic regression (which assumes linearity),
XGBoost handles complex non-linear feature interactions naturally, which is why
it performs well on tabular data with mixed signal types like our telemetry features.

The classifier outputs a probability: "how likely is a memory breach in the next N seconds?"
The regressor outputs a value: "what will memory usage be in the next N seconds?"
Both together give the system quantitative uncertainty, not just a binary alarm.
```

Nuances and questions to sit with:

```text
- What is the difference between a classifier's output (probability 0.0–1.0)
  and a regressor's output (a continuous value)? How do you threshold a probability
  into a binary decision, and why is that threshold a design choice, not a given?
- What is overfitting, and how does the train/validation split detect it?
- Why is accuracy a misleading metric for imbalanced datasets?
  Which metrics actually matter for breach prediction: precision, recall, F1, AUC-ROC?
  What is the cost of a false negative vs. a false positive in this domain?
- What does it mean to "export" a model? Why is a serialized artifact the boundary
  between training and inference — not a shared Python class?
- What is a model card, and why should it be written by the person who trained
  the model rather than added as an afterthought?
```

Tasks:

```text
Load derived_features.csv and training_labels.csv
Stratified split into train (80%) / validation (20%) sets
Train XGBClassifier for breach probability (binary classification)
Train XGBRegressor for future memory projection (regression)
Evaluate classifier: precision, recall, F1, AUC-ROC on validation set
Evaluate regressor: MAE, RMSE, R² on validation set
Plot feature importances for both models and note which features dominate
Save model artifacts in XGBoost JSON format
Save training_metrics.json with all evaluation numbers
Write model_card.md: what each model predicts, input features, evaluation results,
  known limitations, training data description
```

Deliverables:

```text
models/memory_breach_xgb_classifier.json
models/future_memory_xgb_regressor.json
models/training_metrics.json
models/model_card.md
notebooks/03_model_training.ipynb
```

Learning verification — answer these before moving to Phase 5:

```text
1. Explain gradient boosting in 3–4 sentences without using the phrase "ensemble of trees."
2. If your classifier has 98% accuracy but 10% recall on the breach class, is it useful?
   Why or why not?
3. What is the purpose of the validation set during training? Why not evaluate on training data?
4. Why do we serialize the model to JSON rather than keeping it as a live Python object?
5. What would you change in the training pipeline if breach events were 100x rarer
   than in the current dataset?
```

---

### Phase 5 — Streaming Telemetry: What "Live" Actually Means

Estimated time:

```text
1 hour
```

What you are learning:

```text
The fundamental difference between batch (historical) and streaming (live) data access patterns.
What a WebSocket is and why it is appropriate for bidirectional real-time communication.
How a mock service replicates the behavior of a real Kubernetes telemetry source
without requiring a real cluster.
```

The intuition:

```text
Historical data sits in a file. You can read it all at once, shuffle it, and feed it
to a model on your own schedule.

Live data arrives continuously, one event at a time, with real timing between events.
Your system must react to each event as it arrives — it cannot wait to accumulate
all of it first. This changes everything: buffering strategy, feature computation timing,
inference frequency, and error handling.

The mock app teaches you this access pattern in a controlled, inspectable way —
you know exactly what data it will emit and when. Real Kubernetes telemetry would
not give you that control.
```

Nuances and questions to sit with:

```text
- What is a WebSocket and how is it different from a REST HTTP request?
  Why is WebSocket appropriate for streaming telemetry rather than polling?
- What is a "scenario" in a mock telemetry app? Why do we inject controlled failure
  scenarios rather than random noise?
- What is backpressure, and why does it matter when a fast producer meets a slow consumer?
- Why does the mock app emit telemetry at a realistic rate (one event per second)
  rather than as fast as possible?
- What makes testing a streaming system fundamentally harder than testing a batch system?
```

Tasks:

```text
Create FastAPI mock app skeleton
Create /stream/telemetry WebSocket endpoint (emits one pod metric per second)
Create /stream/logs endpoint (emits app log events)
Create /stream/k8s-events endpoint (emits Kubernetes-style events)
Implement scenario runner with four modes: normal / memory_spike / cpu_spike / error_spike
Inject a controlled memory spike starting at T+30s in the memory_spike scenario
Add a /health endpoint
Manual validation: connect a simple Python WebSocket client and confirm 10 events received
```

Deliverables:

```text
mock-kube-telemetry-app/app/main.py
mock-kube-telemetry-app/app/scenarios/
mock-kube-telemetry-app/app/stream/
```

Learning verification — answer these before moving to Phase 6:

```text
1. Why did we choose WebSocket over polling (repeated HTTP GET) for this stream?
2. What happens to the consumer if the producer emits 100 events per second
   but the consumer can only process 10?
3. How does injecting a known spike at a known time help you validate the ML
   pipeline end-to-end?
4. What would be different about this app if we were reading from a real
   Prometheus scrape endpoint instead?
5. Why does the mock app respect realistic timing intervals rather than emitting
   all events instantaneously?
```

---

### Phase 6 — Ingestion, Buffering, and Runtime Inference: Closing the Train-Serve Gap

Estimated time:

```text
1.5 hours
```

What you are learning:

```text
How a live system ingests streaming data, maintains a rolling window, and produces
the same feature vector the model was trained on — but now using live memory instead
of a CSV file.

This is where train-serve skew becomes concrete and real, not just a theory.
```

The intuition:

```text
During training, you had a complete history in a file. You could compute the rolling
average of the last 30 seconds because all 30 seconds of data existed in the CSV.

At runtime, the last 30 seconds of data exists only in memory — in a circular buffer
that drops old events as new ones arrive. The feature engineering logic is identical,
but the data access pattern is completely different.

Getting this right is what separates a model that works on paper from one that
works in a running system.
```

Nuances and questions to sit with:

```text
- What is a circular buffer (collections.deque with maxlen) and why is it the right
  data structure for a rolling window? Why not a list?
- What is the cold start problem for a rolling-window buffer? What should the system
  do in the first 30 seconds when the buffer is not yet full?
- What is the total latency budget for one prediction cycle?
  (event received → features computed → model inference → prediction emitted)
  Where are the bottlenecks likely to be?
- Why must the feature builder use the exact same computation as build_features.py?
  What happens if even one computation drifts slightly?
- What is the difference between predict() and predict_proba() in XGBoost?
  Why do we want the probability rather than the binary class?
- What is a column-order mismatch bug? How does it occur silently and what does
  it do to model outputs?
```

Tasks:

```text
Implement stream ingestion service (connects to mock WebSocket, receives events)
Implement 30-second rolling buffer (collections.deque with maxlen=30)
Implement runtime feature builder by reusing build_features.py logic directly
Assert feature vector column order matches feature_schema.json at startup (fail fast)
Call XGBClassifier → get breach probability (predict_proba)
Call XGBRegressor → get future memory projection (predict)
Emit prediction event with: timestamp, breach_probability, future_memory_mb,
  raw feature vector, model version
Log each prediction to a local JSONL file for later evaluation
Integration test: run memory_spike scenario → confirm breach_probability rises
  above 0.7 within 60 seconds of spike injection
```

Deliverables:

```text
ingestion/stream_ingestion_service.py
buffer/telemetry_buffer_service.py
features/feature_builder_service.py
prediction/prediction_service.py
```

Learning verification — answer these before moving to Phase 7:

```text
1. Define train-serve skew. Give one specific example from this phase where it
   could occur silently without raising any exception.
2. Why is a deque with maxlen the right data structure here rather than a list
   with a pop(0)?
3. What does the system output during the first 30 seconds before the buffer is full?
   What are two defensible strategies for this cold start period?
4. Why do we log input features alongside every prediction?
5. What is the difference between predict() and predict_proba()? Which do we use
   and why?
```

---

### Phase 7 — The Risk Reasoning Agent: What Makes a Component an Agent?

Estimated time:

```text
1 hour
```

What you are learning:

```text
The precise definition of an "agent" in an AI system.
Why most components in a pipeline are services, not agents.
How to encode risk classification logic that is explainable, auditable,
and not delegated entirely to the LLM.
```

The intuition:

```text
A service does exactly what it is told: it takes an input, applies a fixed
transformation, and returns an output. It does not decide what to do next.

An agent perceives its environment (the prediction, the telemetry state, the
recent history), reasons about that state, and decides what action to take next —
call RAG? Emit an alert? Escalate? Wait?

The Risk Reasoning Agent is the first true decision-making component in this system.
It does not just pass data through. It decides the system's next move.

Notice: we do not ask the LLM to classify risk. The LLM is used for explanation.
Risk classification is a deterministic function with auditable thresholds.
This is a deliberate architectural choice.
```

Nuances and questions to sit with:

```text
- What is the perception → reasoning → action loop that defines an agent?
  Which components in this system satisfy that definition? Which do not?
- Why is the Risk Reasoning Agent implemented as a structured decision function
  rather than asking the LLM to classify risk? What are the failure modes of
  delegating classification to a probabilistic model like an LLM?
- What is a risk level taxonomy (NORMAL / WATCH / HIGH / CRITICAL) and how do
  you choose the thresholds? Who owns that decision in a real system?
- Why does the risk decision output include not just the risk level, but also
  three routing decisions: requires_rag? requires_alert? requires_human_approval?
  What architectural pattern does this represent?
- What is an alert storm? Why is a cooldown window the minimum viable suppression
  mechanism?
- Why is it important to log the full risk decision (inputs + outputs + reasoning)
  for auditability, even in a POC?
```

Tasks:

```text
Implement RiskReasoningAgent class
Implement reason(prediction_event, telemetry_state) → RiskDecision method
Map breach_probability to NORMAL (<0.3) / WATCH (0.3–0.6) / HIGH (0.6–0.85)
  / CRITICAL (>0.85) using named thresholds (not magic numbers)
Add cooldown: suppress repeated decisions of the same risk level within 60 seconds
Emit structured RiskDecision:
  - risk_level: str
  - requires_rag: bool
  - requires_alert: bool
  - requires_human_approval: bool
  - reasoning_summary: str (one-sentence rationale)
  - input_breach_probability: float
  - input_future_memory_mb: float
  - decided_at: datetime
Log full decision with input context
```

Deliverables:

```text
agents/risk_reasoning_agent.py
```

Learning verification — answer these before moving to Phase 8:

```text
1. Give a one-sentence definition of an agent that distinguishes it from a service.
   Name one component in this system that is an agent and one that is not.
2. Why don't we ask the LLM to classify risk level directly?
3. What is an alert storm and how does the 60-second cooldown mechanism prevent it?
4. Why does the risk decision include a reasoning_summary field even though we
   already have the raw breach_probability?
5. If you wanted the risk thresholds to adapt dynamically based on historical
   false positive rates, what would you change?
```

---

### Phase 8 — RAG: Why LLMs Need External Memory

Estimated time:

```text
1 hour
```

What you are learning:

```text
Why a large language model cannot reliably recall your runbooks, past incidents,
or deployment notes from its training parameters alone.
What retrieval-augmented generation is and why it is the dominant pattern for
grounding LLM responses in domain-specific knowledge.
The difference between keyword-based and embedding-based retrieval.
```

The intuition:

```text
An LLM is trained on a large corpus of text. It has general language understanding
and reasoning ability. But it does not know your specific runbooks.

If you ask it "what should we do when pod memory exceeds 90%?", it will generate
a plausible-sounding but potentially fabricated answer — because it is trying to
predict the next likely token, not recall a specific document.

RAG solves this by retrieving relevant documents at query time and injecting them
into the LLM's context window. The LLM is no longer guessing from parametric memory.
It is reasoning over provided, verifiable evidence.

The quality of the retrieved context matters more than the sophistication of the LLM.
```

Nuances and questions to sit with:

```text
- What is the difference between parametric memory (what the LLM learned during
  training) and non-parametric memory (retrieved documents injected at inference time)?
- What is an embedding? Why does converting text to a vector allow semantic similarity
  search rather than just keyword matching?
- What is cosine similarity and why is it used to compare embedding vectors?
- What is the context window of an LLM and why does it constrain how much retrieved
  content you can inject?
- What is the difference between sparse retrieval (BM25, keyword overlap) and dense
  retrieval (embedding vectors)? When would you prefer each?
- What is chunking strategy? Why does splitting by section header produce better
  retrieval than splitting by fixed character count?
```

Tasks:

```text
Load and parse ksg_production_style_synthetic_datasets/ documents:
  runbooks.md, incident_archive.md, deployment_notes.md, app_logs.jsonl
Implement DocumentChunker: split by section header (##), not by fixed character count
Implement KeywordRetriever: TF-IDF or simple token overlap scoring
Implement retrieve(query: str, top_k: int = 3) → List[DocumentChunk]
Return top-k chunks with source, section, and relevance score
Optional: implement EmbeddingRetriever using nomic-embed-text via Ollama
Integration test: query "memory spike pod restart" → confirm a runbook section
  is ranked in top-3 results
```

Deliverables:

```text
rag/rag_retrieval_service.py
rag/document_loader.py
rag/keyword_retriever.py
rag/embedding_retriever.py  (optional)
```

Learning verification — answer these before moving to Phase 9:

```text
1. What is the difference between what the LLM "knows" from training and what RAG provides?
2. Why is embedding-based retrieval more powerful than keyword matching for this use case?
   Give one example where keyword matching fails but embedding retrieval succeeds.
3. What is the context window constraint and how does it limit how many documents
   you can retrieve?
4. Why does splitting by section header produce better retrieval than fixed-character chunks?
5. If a retrieved runbook section is not actually relevant to the current alert,
   what happens to LLM output quality?
```

---

### Phase 9 — LLM Prompt Engineering: Structured Output and Grounding

Estimated time:

```text
1.5 hours
```

What you are learning:

```text
How to construct a prompt that produces reliable, structured, grounded LLM output.
Why prompt engineering is a real engineering discipline with measurable outcomes.
How to handle LLM output unreliability — malformed JSON, hallucination,
excessive verbosity — gracefully in a software system.
```

The intuition:

```text
An LLM generates text probabilistically. Without careful prompting, it will be
verbose, inconsistent, and confident-sounding when wrong.

To use an LLM reliably inside a software system, you must:
  1. Give it a precise system prompt that defines its role and output constraints.
  2. Inject retrieved evidence so it has actual facts to reason from.
  3. Specify the exact JSON output format with field definitions.
  4. Keep temperature low to reduce creative variation.
  5. Have a retry strategy for malformed outputs.

This is not "chatting with an AI." This is engineering a constrained interface
to a probabilistic function.
```

Nuances and questions to sit with:

```text
- What is the difference between a system prompt and a user prompt in a chat-completion API?
  How does each influence LLM behavior differently?
- What is few-shot prompting and why does including one example of the expected JSON
  output in the prompt improve compliance?
- What is temperature in an LLM API call? Why should it be low (0.1–0.3) when you
  need consistent structured output?
- Why do you retry exactly once on invalid JSON rather than indefinitely or never?
- What is hallucination in this context? How does injecting retrieved evidence reduce
  (but not eliminate) it?
- What latency should you expect from a local 7–8B parameter LLM? Why does this matter
  for the system's overall responsiveness and the user's perceived experience?
```

Initial model:

```text
qwen3:8b
```

Tasks:

```text
Implement Ollama API client (POST to /api/chat endpoint)
Implement system prompt template:
  - role: SRE analyst generating an operational alert narrative
  - output constraint: strict JSON only, no surrounding prose
  - output schema: { summary, severity, affected_component, evidence_used,
                     recommended_action, confidence_level }
Implement user prompt template:
  - inject: breach_probability, future_memory_mb, risk_level
  - inject: top-3 retrieved document chunks
  - inject: one example of valid JSON output (few-shot)
Implement JSON response parser with validation
Implement retry: if JSON parsing fails, retry once with an explicit correction prompt
Log per call: model name, prompt token count, response token count, latency_ms,
  json_valid (bool)
Integration test: run HIGH risk scenario → confirm output contains all six
  required fields and is valid JSON
```

Deliverables:

```text
agents/llm_narrative_agent.py
llm/llm_api_client.py
llm/prompt_templates.py
```

Learning verification — answer these before moving to Phase 10:

```text
1. Why does injecting retrieved runbook content into the prompt improve accuracy
   compared to asking the LLM to recall it from training?
2. What does temperature control in an LLM API call do, and what value is appropriate
   for structured output generation?
3. Why retry exactly once on malformed JSON, rather than indefinitely?
4. What is the difference between a "grounded" LLM response and a "hallucinated" one
   in this context? How would you detect hallucination programmatically?
5. What is the typical latency for a 7–8B parameter LLM running locally? How does this
   affect where you place LLM calls in a latency-sensitive system?
```

---

### Phase 10 — Human-in-the-Loop: The Safety Layer

Estimated time:

```text
1 hour
```

What you are learning:

```text
Why automated AI systems that take consequential actions should require human confirmation.
How to design the human approval loop as a first-class architectural concern.
What alert fatigue is and how deduplication addresses it at the system level.
```

The intuition:

```text
A CRITICAL risk decision might recommend restarting a pod or scaling a deployment.
These are irreversible, production-affecting actions.

An AI system that takes such actions autonomously — even with high-confidence
predictions — is dangerous. ML predictions are probabilistic, not certain.
A 0.95 breach probability still means 1 in 20 is a false alarm.

Human-in-the-loop design acknowledges this uncertainty and places a human
as the decision owner for consequential actions. This is not a limitation of AI.
It is responsible system architecture.

And separately: alert fatigue is a real operational problem. An AI system that
generates 200 alerts per hour trains operators to ignore all of them.
```

Nuances and questions to sit with:

```text
- What is the difference between an alert (informational notification) and an
  action (a change to a running system)?
- What is alert fatigue and what is its real operational cost in SRE contexts?
- What is deduplication / alert suppression, and how does a cooldown window
  implement it? What are its failure modes?
- What should happen if the human rejects a recommended action? If they approve it?
  Should both outcomes be logged, and why?
- What is the difference between a "recommended action" (AI-suggested) and an
  "approved action" (human-confirmed)? Why does this distinction matter for
  post-incident audit trails?
- What should happen if no human responds within N seconds? Design the fallback.
```

Tasks:

```text
Implement ActionAlertAgent with emit_alert(risk_decision, narrative) method
Implement alert deduplication: suppress if same risk_level seen within 60 seconds
Construct recommended action payload:
  - action_id (UUID)
  - action_type (scale_up / restart_pod / notify_on_call)
  - requires_human_approval (bool)
  - rationale (str, one sentence from narrative)
  - expires_at (datetime, 5 minutes from emit)
Emit alert event via WebSocket to dashboard
Implement POST /api/actions/{action_id}/approve
Implement POST /api/actions/{action_id}/reject
Log human decision: action_id, decision, decided_by, decided_at
Test: emit two consecutive HIGH risk alerts → confirm only one reaches the dashboard
```

Deliverables:

```text
agents/action_alert_agent.py
schemas/action.py
schemas/feedback.py
```

Learning verification — answer these before moving to Phase 11:

```text
1. Define alert fatigue in one sentence. How does the suppression mechanism reduce it?
2. Why should automated systems require human confirmation before consequential actions
   even when prediction confidence is high?
3. What is the difference between what the AI recommends and what a human approves?
   Why does this distinction matter for audit trails?
4. Why do we log rejected actions, not just approved ones?
5. What would you add if you needed to track whether an approved action actually
   resolved the incident it was triggered for?
```

---

### Phase 11 — React Dashboard: UI as Observability Infrastructure

Estimated time:

```text
1 hour
```

What you are learning:

```text
How a real-time React dashboard differs architecturally from a static one.
What WebSocket-driven UI state management looks like in practice.
Why a dashboard in an agentic AI system is not just a display layer —
it is the observability interface that makes the entire pipeline visible,
debuggable, and trustable.
```

The intuition:

```text
In an agentic AI system, you cannot trust what you cannot see. If you cannot
observe what the model predicted, what evidence RAG retrieved, what the LLM
generated, and what risk level the agent decided — you cannot debug the system
when it behaves unexpectedly.

Every panel in the dashboard represents a different layer of the system's reasoning.
It is not decoration. It is the interface through which you, as the developer and
operator, understand what the system is doing at each step.

The human approval panel exists here — not in a backend admin console — because
it must be immediately visible alongside the evidence that motivated the recommendation.
```

Nuances and questions to sit with:

```text
- Why does a WebSocket-driven UI have a fundamentally different update model
  than a UI that polls a REST endpoint?
- What happens to React performance if you call setState on every incoming WebSocket
  event without batching? How do you handle high-frequency updates correctly?
- What does each dashboard panel reveal about each system layer?
  (telemetry → prediction → risk → RAG → LLM → action → approval)
- Why do we show RAG evidence in the UI rather than hiding it as an internal
  implementation detail?
- Why does the human approval panel show the LLM narrative and retrieved evidence
  alongside the approve/reject buttons?
```

Tasks:

```text
Create React app with a single WebSocket connection hook (reconnects on disconnect)
Implement live telemetry panel: memory usage line chart, CPU usage line chart,
  error rate indicator (last 30 data points)
Implement prediction panel: breach probability gauge (0–1), future memory projection
  chart with current value overlay
Implement risk panel: risk level badge (color-coded), reasoning_summary text,
  cooldown indicator
Implement RAG evidence panel: list of retrieved document chunks with source and
  relevance score
Implement LLM narrative panel: structured display of summary, severity, affected
  component, confidence level, recommended action
Implement action approval panel: approve / reject buttons, action rationale,
  expiry countdown, disabled after decision
Implement system metrics panel: avg prediction latency, avg LLM latency, total
  alerts emitted, JSON validity rate
```

Deliverables:

```text
frontend/src/App.tsx
frontend/src/components/
```

Learning verification — answer these before moving to Phase 12:

```text
1. Why is a WebSocket connection more appropriate than polling for this dashboard?
2. What does each dashboard panel reveal about a different layer of the system?
   Map each panel to the component that generates its data.
3. Why do we show RAG evidence in the UI rather than keeping it internal?
4. What is the purpose of the expiry countdown on the approval panel?
5. How would you add a "replay mode" that feeds a logged past incident through
   the dashboard without re-running the full pipeline?
```

---

### Phase 12 — Evaluation, LLM Comparison, and Learning Consolidation

Estimated time:

```text
1–1.5 hours
```

What you are learning:

```text
How to measure whether a live AI system is actually working.
What LLM evaluation means in a structured-output, grounded context.
How to consolidate and articulate the learning from the entire POC —
because building the system is not the same as understanding it.
```

The intuition:

```text
Evaluation of a live AI system is different from evaluation of a trained model.

Model evaluation: does the model predict correctly on held-out data?
System evaluation: does the full pipeline behave correctly under real conditions?
  - Does breach probability rise when a real spike is injected?
  - Do both LLMs produce valid JSON on the same prompt?
  - Does the agent suppress duplicate alerts correctly?
  - What is the end-to-end latency from spike injection to alert displayed in the UI?

The LEARNING_LOG.md is the most important artifact of this entire POC.
It is the evidence that understanding was gained, not just code was written.
```

Nuances and questions to sit with:

```text
- What runtime signals indicate the ML models are behaving correctly at runtime?
  (Not just on validation data, but in the live pipeline.)
- How do you compare two LLMs on the same prompt fairly? What metrics matter:
  JSON validity rate? Response latency? Semantic faithfulness to retrieved evidence?
- What is the difference between "evaluation" in ML training and "evaluation"
  of a live AI system's runtime behavior?
- What does a learning log capture that code comments and documentation do not?
```

Tasks:

```text
Run full end-to-end pipeline with memory_spike scenario
Collect all prediction events from prediction_log.jsonl
Collect all LLM call records from telemetry_log.jsonl
Compare qwen3:8b vs. one other Ollama model (same HIGH risk context, same prompt):
  - JSON validity rate
  - Average response latency
  - Qualitative differences in reasoning and recommendations
Compute system metrics:
  - Average prediction cycle latency (event → prediction emitted)
  - Average LLM call latency
  - Alert deduplication hit rate
  - JSON validity rate across all LLM calls
Write final_eval_report.json (structured metrics)
Write llm_comparison_report.json (per-model breakdown)
Write LEARNING_LOG.md — one section per phase answering:
  "What did I understand after building this that I did not understand before?"
```

Deliverables:

```text
outputs/reports/final_eval_report.json
outputs/reports/llm_comparison_report.json
LEARNING_LOG.md
```

Learning verification — the LEARNING_LOG.md entries are your answers:

```text
1. Explain the full pipeline in one sentence per stage, without looking at any notes.
2. Where in the pipeline is train-serve skew most likely to occur? How would you detect it?
3. Why does the LLM narrative need RAG evidence to be trustworthy?
4. What distinguishes an agent from a service in this system? Name all three agents.
5. If you were building KubeSage tomorrow using what you learned here, what would
   you keep and what would you redesign?
6. What surprised you most about how the system behaved at runtime vs. how you
   expected it to behave on paper?
```

---

## 22. Final Acceptance Criteria

The POC is successful if:

```text
1. Mock Kube Telemetry App streams telemetry, logs, and events.
2. POC Intelligence App receives and buffers live telemetry.
3. XGBoost classifier and regressor are trained and loaded.
4. Runtime feature vectors are generated from a 30-second rolling window.
5. Prediction Service produces breach probability and future memory projection.
6. Risk Reasoning Agent classifies operational severity.
7. RAG Retrieval Service retrieves relevant evidence when needed.
8. LLM Narrative Agent generates grounded JSON explanation.
9. Action / Alert Agent emits alert and handles human approval flow.
10. React UI displays telemetry, prediction, evidence, narrative, and approval controls.
11. Runtime logs are stored for replay and future retraining.
12. Evaluation report is generated.
13. At least two LLMs are compared on the same alert context.
```

---

## 23. How This Maps to KubeSage

```text
Mock telemetry app       -> real Kubernetes / Prometheus / OpenTelemetry source
Synthetic incidents      -> real incident archive
XGBoost prediction       -> workload risk prediction
RAG docs                 -> runbooks, postmortems, deployment notes
Risk Reasoning Agent     -> KubeSage diagnosis planner
LLM Narrative Agent      -> SRE explanation layer
Action / Alert Agent     -> human-in-the-loop ops workflow
React dashboard          -> KubeSage UI
Runtime archive          -> future training and incident replay
```

---

## 24. How This Maps to F1-AI

```text
Kube telemetry stream       -> live lap/sector/tyre telemetry
Memory breach prediction    -> tyre degradation / lap-time / pit-window prediction
Runbooks/incidents          -> regulations, race notes, historical strategy records
Risk Reasoning Agent        -> strategy reasoning agent
LLM Narrative Agent         -> race strategist explanation
Action / Alert Agent        -> strategy recommendation / human confirmation
Runtime archive             -> race replay and future model improvement
```

---

## 25. Final Summary

This POC is a two-application learning system.

```text
Mock Kube Telemetry App
  -> produces live Kubernetes-style telemetry, logs, events, and spikes

POC Intelligence App
  -> performs real-time ML prediction, RAG grounding, LLM explanation, AI-agent decision flow, alerts, human approval, and evaluation
```

Only three components are decision-making AI agents:

```text
1. Risk Reasoning Agent
2. LLM Narrative Agent
3. Action / Alert Agent
```

Everything else is a service or tool.

The final learning outcome should be:

```text
I understand how trained ML models, RAG, LLMs, and AI agents work together inside a live software system.
```
