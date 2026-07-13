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

## 21. 10–12 Hour Roadmap

---

### Phase 1 — Architecture and Contracts

Estimated time:

```text
1 hour
```

Tasks:

```text
Create two-app folder structure
Define telemetry event contract
Define app log event contract
Define Kubernetes event contract
Define feature schema
Define prediction schema
Define risk decision schema
Define LLM narrative schema
Define alert/action schema
```

Deliverables:

```text
mock-kube-telemetry-app/schemas/
poc-intelligence-app/backend/app/schemas/
README.md
```

Acceptance criteria:

```text
Both applications agree on event contracts.
```

---

### Phase 2 — Synthetic Historical Data and Training Dataset

Estimated time:

```text
1 hour
```

Tasks:

```text
Generate historical synthetic pod telemetry
Generate normal workload
Generate memory leak pattern
Generate CPU spike pattern
Generate error spike pattern
Generate post-deployment memory growth
Create memory breach labels
Create future memory targets
```

Deliverables:

```text
poc-intelligence-app/data/historical/synthetic_pod_telemetry.csv
```

Acceptance criteria:

```text
Dataset contains normal and abnormal patterns for model training.
```

---

### Phase 3 — Feature Engineering

Estimated time:

```text
1 hour
```

Tasks:

```text
Build shared feature generation logic
Compute rolling averages
Compute slopes
Compute memory ratios
Compute future targets
Export feature schema
```

Deliverables:

```text
ml-training/build_features.py
models/feature_schema.json
```

Acceptance criteria:

```text
The same feature contract can be used for training and runtime inference.
```

---

### Phase 4 — Train XGBoost Models

Estimated time:

```text
1.5 hours
```

Tasks:

```text
Train XGBClassifier for breach probability
Train XGBRegressor for future memory projection
Evaluate classifier
Evaluate regressor
Save model artifacts
Save model metrics
Create model card
```

Deliverables:

```text
models/memory_breach_xgb_classifier.json
models/future_memory_xgb_regressor.json
models/training_metrics.json
models/model_card.md
```

Acceptance criteria:

```text
POC Intelligence App can load models and run inference.
```

---

### Phase 5 — Mock Kube Telemetry App

Estimated time:

```text
1 hour
```

Tasks:

```text
Create FastAPI mock app
Create telemetry stream endpoint
Create log stream
Create Kubernetes event stream
Create scenario runner
Inject dummy memory spike
```

Deliverables:

```text
mock-kube-telemetry-app/app/main.py
mock-kube-telemetry-app/app/scenarios/
mock-kube-telemetry-app/app/stream/
```

Acceptance criteria:

```text
Mock app streams live Kubernetes-style telemetry for one scenario.
```

---

### Phase 6 — POC Ingestion + Buffer + Prediction

Estimated time:

```text
1.5 hours
```

Tasks:

```text
Connect POC app to mock stream
Store raw telemetry
Maintain 30-second rolling buffer
Build runtime feature vector
Call Prediction Service
Emit prediction event to UI
```

Deliverables:

```text
ingestion/stream_ingestion_service.py
buffer/telemetry_buffer_service.py
features/feature_builder_service.py
prediction/prediction_service.py
```

Acceptance criteria:

```text
During a live spike, the POC app produces breach probability and future memory projection.
```

---

### Phase 7 — Risk Reasoning Agent

Estimated time:

```text
1 hour
```

Tasks:

```text
Implement Risk Reasoning Agent
Classify NORMAL/WATCH/HIGH/CRITICAL
Decide whether RAG is required
Decide whether alert is required
Decide whether human approval is required
Emit risk decision event
```

Deliverables:

```text
agents/risk_reasoning_agent.py
```

Acceptance criteria:

```text
Risk Reasoning Agent makes structured decisions from ML prediction and telemetry state.
```

---

### Phase 8 — RAG Retrieval Service

Estimated time:

```text
1 hour
```

Tasks:

```text
Create local runbooks
Create incident notes
Create deployment notes
Implement document loader
Implement keyword retriever
Optionally implement embedding retriever with nomic-embed-text
Return retrieved context to Risk Reasoning / Narrative flow
```

Deliverables:

```text
rag/rag_retrieval_service.py
rag/document_loader.py
rag/keyword_retriever.py
rag/embedding_retriever.py
```

Acceptance criteria:

```text
HIGH or CRITICAL risk decisions retrieve supporting evidence.
```

---

### Phase 9 — LLM Narrative Agent

Estimated time:

```text
1.5 hours
```

Tasks:

```text
Connect to local LLM API
Create prompt contract
Send prediction + risk decision + RAG evidence to LLM
Return strict JSON explanation
Retry once on invalid JSON
Log LLM latency and quality signals
```

Initial model:

```text
qwen3:8b
```

Deliverables:

```text
agents/llm_narrative_agent.py
llm/llm_api_client.py
llm/prompt_templates.py
```

Acceptance criteria:

```text
The system generates a grounded user-readable explanation for a high-risk event.
```

---

### Phase 10 — Action / Alert Agent + Human Approval

Estimated time:

```text
1 hour
```

Tasks:

```text
Implement Action / Alert Agent
Emit alert events
Suppress duplicate alerts
Prepare recommended actions
Mark actions requiring human approval
Handle approve/reject from UI
Log approval decision
```

Deliverables:

```text
agents/action_alert_agent.py
schemas/action.py
schemas/feedback.py
```

Acceptance criteria:

```text
The UI receives alert + recommended action, and human approval/rejection is logged.
```

---

### Phase 11 — React Dashboard

Estimated time:

```text
1 hour
```

Tasks:

```text
Create React dashboard
Connect to POC WebSocket
Show live telemetry
Show prediction/projection
Show risk reasoning
Show RAG evidence
Show LLM narrative
Show action approval panel
Show metrics
```

Deliverables:

```text
frontend/src/App.tsx
frontend/src/components/
```

Acceptance criteria:

```text
User can visually observe the full telemetry -> prediction -> reasoning -> RAG -> LLM -> alert flow.
```

---

### Phase 12 — Evaluation, LLM Comparison, and Wrap-Up

Estimated time:

```text
1–1.5 hours
```

Tasks:

```text
Log all runtime events
Generate final evaluation report
Compare at least two LLMs on same context
Measure latency and JSON validity
Write learning log
Write mapping to KubeSage and F1-AI
```

Deliverables:

```text
outputs/reports/final_eval_report.json
outputs/reports/llm_comparison_report.json
LEARNING_LOG.md
```

Acceptance criteria:

```text
The POC produces measurable outputs and a clear learning summary.
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
