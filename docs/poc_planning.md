# KubeSage

## Real-Time ML + RAG + LLM Alert Intelligence for Kubernetes Telemetry -- Learning POC

---

## 1. Purpose

This POC is a focused 10–12 hour learning experiment designed to understand how a real-time AI intelligence system works when live telemetry, ML prediction, RAG grounding, LLM explanation, WebSocket alerts, and agent-style orchestration come together.

KubeSage is currently a focused learning POC — not yet a full production system.

This POC exists to learn:

1. How historical telemetry/log data becomes ML training data.
2. How XGBoost models are trained, exported, loaded, and used inside a FastAPI application.
3. How live telemetry streams are buffered into rolling windows.
4. How rolling-window features are passed to ML models for prediction and projection.
5. How RAG retrieves supporting operational evidence from runbooks, incidents, and archived logs.
6. How an LLM converts prediction + retrieved evidence into an alert narrative.
7. How WebSocket alerts can be sent to a React interface in near real time.
8. How agent-like components coordinate ML, RAG, LLM, and alerting.
9. How runtime data can be stored for replay, evaluation, and future model improvement.
10. How different locally hosted LLMs behave on the same prediction and context.

---

## 2. Final POC Definition

KubeSage is a FastAPI + React learning system that trains XGBoost models on historical or synthetic Kubernetes-style telemetry, streams live pod metrics through WebSockets, buffers the live stream for a short rolling window, generates ML predictions and future projections, retrieves related evidence from an operational archive using a RAG pipeline, sends prediction + evidence to a local LLM, and displays alerts plus grounded narratives in a React interface.

The system uses agent-style components to simulate a production AI workflow.

---

## 3. High-Level Flow

```text
Historical Data
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

FastAPI Application
        ↓
Live WebSocket Telemetry Stream
        ↓
30-second Rolling Buffer
        ↓
Metrics Aggregator Agent
        ↓
Feature Builder Agent
        ↓
Prediction Agent
        ├── XGBClassifier: breach probability
        └── XGBRegressor: future memory projection
        ↓
Risk Analyzer Agent
        ↓
RAG Retrieval Agent
        ↓
LLM Interface Agent
        ↓
Narrative Agent
        ↓
Alert Agent
        ↓
React UI
        ↓
Evaluation + Runtime Archive
```

---

## 4. What We Are Actually Predicting

We are not only detecting a spike.

We are predicting and projecting operational risk.

### 4.1 Classification Model

Question:

```text
Will this pod breach the memory threshold in the near future?
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

### 4.2 Regression Model

Question:

```text
What will the memory usage be after the prediction horizon?
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

### 4.3 Operational ETA

The model predicts risk and future memory value.

The Risk Analyzer Agent can derive ETA using:

```text
current_memory
memory_limit
current_memory_slope
predicted_memory_30s
breach_threshold
```

Output:

```json
{
  "estimated_seconds_to_threshold": 22,
  "severity": "HIGH"
}
```

---

## 5. Dataset Plan

### 5.1 Primary Approach: Synthetic Dataset

For the first version, use synthetic Kubernetes-style telemetry.

Reason:

* Controlled spike behavior.
* Easy labeling.
* Easy repeatability.
* Good for understanding model behavior.
* No dependency on noisy public data.
* Lets us design exact incident scenarios.

### 5.2 Optional External Dataset Exploration

After synthetic data works, explore public datasets from:

* Kaggle Kubernetes anomaly datasets.
* AIOps failure detection datasets.
* Synthetic Kubernetes/Istio log datasets.
* OpenTelemetry Demo-generated metrics/logs/traces.
* Public log anomaly detection datasets.

External datasets should not block the POC.

The first working version should run fully with synthetic data.

---

## 6. Historical Data Needed

The historical dataset should contain:

### 6.1 Pod Telemetry

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

### 6.2 Kubernetes Events

```text
timestamp
pod_name
namespace
event_type
event_reason
event_message
```

Example event reasons:

```text
OOMKilled
CrashLoopBackOff
ImagePullBackOff
ReadinessProbeFailed
LivenessProbeFailed
NodeMemoryPressure
Evicted
DeploymentRollout
ScalingEvent
```

### 6.3 Application Logs

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

Example log patterns:

```text
timeout
connection refused
out of memory
heap pressure
high latency
database pool exhausted
rate limit exceeded
```

### 6.4 Incident Archive

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

### 6.5 Training Labels

For classification:

```text
label_memory_breach_next_30s
label_pod_restart_next_30s
label_error_spike_next_30s
```

For regression:

```text
target_memory_mb_30s
target_memory_ratio_30s
target_cpu_pct_30s
```

For this POC, start with memory prediction only:

```text
label_memory_breach_next_30s
target_memory_mb_30s
target_memory_ratio_30s
```

---

## 7. Feature Engineering Plan

Raw telemetry should not go directly to the model.

The system should generate rolling-window features.

### 7.1 Runtime Window

The live stream is buffered for:

```text
30 seconds
```

Within that buffer, compute:

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

### 7.2 Feature Set

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

### 7.3 Important Learning Rule

The same feature logic must be used in both places:

```text
training pipeline
runtime inference pipeline
```

If training features and runtime features drift apart, model predictions become unreliable.

---

## 8. ML Model Plan

### 8.1 Model Family

Use XGBoost.

Models:

```text
XGBClassifier
XGBRegressor
```

### 8.2 Classifier

Purpose:

```text
Predict whether memory breach is likely in the next 30 seconds.
```

Input:

```text
rolling telemetry features
```

Output:

```json
{
  "breach_probability": 0.87,
  "breach_likely": true
}
```

Metrics:

```text
accuracy
precision
recall
F1 score
confusion matrix
ROC-AUC
feature importance
```

### 8.3 Regressor

Purpose:

```text
Predict future memory value after 30 seconds.
```

Input:

```text
rolling telemetry features
```

Output:

```json
{
  "predicted_memory_mb_30s": 948,
  "predicted_memory_ratio_30s": 0.92
}
```

Metrics:

```text
MAE
RMSE
R2 score
prediction error distribution
```

### 8.4 Model Artifacts

Export:

```text
models/memory_breach_xgb_classifier.json
models/future_memory_xgb_regressor.json
models/feature_schema.json
models/training_metrics.json
models/model_card.md
```

### 8.5 Model Card Contents

```text
model name
model type
training data description
feature list
label definition
evaluation metrics
known limitations
prediction horizon
runtime usage
```

---

## 9. FastAPI Application Plan

The FastAPI app will handle:

```text
WebSocket streaming
live telemetry simulation
rolling buffer management
ML inference
RAG retrieval
LLM calls
alert dispatch
metrics logging
```

### 9.1 API Endpoints

```text
GET  /health
GET  /models/status
POST /train/start
GET  /train/metrics
POST /simulate/start
POST /simulate/stop
GET  /outputs/eval-report
WS   /ws/telemetry
```

### 9.2 WebSocket Event Types

#### Telemetry Event

```json
{
  "type": "telemetry",
  "timestamp": "00:23",
  "pod_name": "payment-api",
  "memory_mb": 720,
  "cpu_pct": 63,
  "error_rate": 4,
  "request_rate": 140,
  "restart_count": 0
}
```

#### Feature Event

```json
{
  "type": "features",
  "timestamp": "00:24",
  "memory_ratio_current": 0.72,
  "memory_slope_10s": 18.2,
  "error_rate_avg_5s": 6
}
```

#### Prediction Event

```json
{
  "type": "prediction",
  "timestamp": "00:31",
  "breach_probability": 0.78,
  "predicted_memory_mb_30s": 930,
  "status": "WATCH"
}
```

#### Alert Event

```json
{
  "type": "alert",
  "timestamp": "00:35",
  "severity": "HIGH",
  "message": "payment-api is likely to breach memory threshold soon."
}
```

#### RAG Context Event

```json
{
  "type": "rag_context",
  "timestamp": "00:36",
  "retrieved_docs": [
    "incident_2026_05_23_memory_growth.md",
    "runbook_memory_spike.md"
  ]
}
```

#### LLM Narrative Event

```json
{
  "type": "llm_narrative",
  "timestamp": "00:39",
  "model": "qwen3:8b",
  "response": {
    "alert_title": "Payment API memory breach risk",
    "severity": "HIGH",
    "prediction_summary": "The pod has an 87% probability of breaching memory threshold.",
    "likely_cause": "Memory is rising rapidly after a recent deployment.",
    "recommended_actions": [
      "Check recent deployment changes",
      "Inspect memory usage across replicas",
      "Prepare rollback if the trend continues"
    ]
  }
}
```

---

## 10. Agent Plan

This POC will use agent-style components.

These are not all LLM agents.

Most of them are deterministic agents with clear responsibilities.

### 10.1 Telemetry Simulator Agent

Responsibility:

```text
Generate live Kubernetes-style telemetry events.
```

Behavior:

```text
0–20s: normal workload
21–35s: gradual memory growth
36–50s: dummy memory spike
51–60s: sustained high memory pressure
```

Output:

```text
TelemetryEvent
```

### 10.2 Metrics Aggregator Agent

Responsibility:

```text
Maintain a rolling 30-second telemetry buffer.
```

Tasks:

```text
store latest telemetry
maintain sliding window
calculate raw window stats
pass window to feature builder
```

Output:

```text
TelemetryWindow
```

### 10.3 Feature Builder Agent

Responsibility:

```text
Convert telemetry windows into ML-ready feature vectors.
```

Tasks:

```text
calculate rolling averages
calculate slopes
calculate ratios
calculate error-rate movement
validate feature schema
```

Output:

```text
FeatureVector
```

### 10.4 Prediction Agent

Responsibility:

```text
Load XGBoost models and run inference.
```

Models:

```text
XGBClassifier
XGBRegressor
```

Tasks:

```text
predict breach probability
predict future memory value
attach model version
log inference latency
```

Output:

```text
PredictionResult
```

### 10.5 Risk Analyzer Agent

Responsibility:

```text
Convert ML outputs into operational severity.
```

Rules:

```text
probability >= 0.85 and predicted_ratio >= 0.90 -> CRITICAL
probability >= 0.75 and predicted_ratio >= 0.85 -> HIGH
probability >= 0.55 -> WATCH
else -> NORMAL
```

Output:

```text
RiskAssessment
```

### 10.6 RAG Retrieval Agent

Responsibility:

```text
Retrieve supporting context from operational archive.
```

Triggered only when:

```text
severity == HIGH or CRITICAL
```

Retrieves from:

```text
runbooks
incident notes
archived log summaries
Kubernetes event explanations
deployment notes
```

Output:

```text
RetrievedContext
```

### 10.7 LLM Interface Agent

Responsibility:

```text
Call the selected local LLM through API.
```

Available models:

```text
llama3:latest
qwen3:8b
qwen3:4b
qwen2.5:latest
gpt-oss:20b
llama3.2:3b
```

Embedding model:

```text
nomic-embed-text:latest
```

Tasks:

```text
build prompt
select model
call API
apply timeout
parse JSON
retry once if invalid JSON
log latency
```

Output:

```text
LLMRawResponse
```

### 10.8 Narrative Agent

Responsibility:

```text
Transform ML prediction + RAG context into grounded alert narrative.
```

Rules:

```text
do not invent causes
use retrieved evidence
mention uncertainty
recommend practical next steps
return strict JSON
```

Output:

```text
LLMExplanation
```

### 10.9 Alert Agent

Responsibility:

```text
Send alerts and narratives to React UI through WebSocket.
```

Tasks:

```text
emit prediction event
emit alert event
emit RAG event
emit LLM explanation event
avoid duplicate alert spam
```

Output:

```text
WebSocket messages
```

### 10.10 Evaluation Agent

Responsibility:

```text
Log and evaluate ML, RAG, LLM, and streaming behavior.
```

Tracks:

```text
ML latency
prediction quality
RAG latency
retrieved document quality
LLM latency
JSON validity
groundedness
actionability
WebSocket delivery latency
end-to-end alert latency
```

Output:

```text
final_eval_report.json
```

---

## 11. RAG Pipeline Plan

### 11.1 RAG Purpose

RAG is not used to predict.

RAG is used to support and ground the prediction.

The ML model says:

```text
This pod is likely to breach memory threshold.
```

The RAG system retrieves:

```text
Which past incidents, logs, runbooks, or operational notes support this finding?
```

The LLM then explains:

```text
Why the alert matters, what evidence supports it, and what an engineer should check next.
```

### 11.2 RAG Sources

Use local Markdown files first.

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

### 11.3 RAG Index

For the first version:

```text
Option A: keyword retrieval
Option B: embedding retrieval using nomic-embed-text
```

Recommended:

```text
Start with keyword retrieval.
Then add embedding retrieval.
Then compare both.
```

### 11.4 RAG Query Builder

The query should be generated from the structured ML/risk output.

Input:

```json
{
  "pod_name": "payment-api",
  "severity": "HIGH",
  "top_signals": [
    "memory_slope_10s",
    "memory_ratio_current",
    "error_rate_avg_5s",
    "recent_deployment_flag"
  ]
}
```

Generated query:

```text
payment-api high memory slope memory breach high error rate recent deployment possible memory leak
```

### 11.5 Retrieved Context Shape

```json
{
  "retrieved_docs": [
    {
      "doc_id": "incident_2026_05_23_memory_growth",
      "title": "Memory growth after deployment",
      "score": 0.86,
      "snippet": "payment-api showed rapid memory growth after deployment..."
    },
    {
      "doc_id": "runbook_memory_spike",
      "title": "Memory Spike Runbook",
      "score": 0.81,
      "snippet": "Check memory slope, recent rollout, heap growth, and replica imbalance..."
    }
  ]
}
```

### 11.6 RAG Metrics

```text
retrieval_latency_ms
top_k_docs
retrieval_scores
expected_doc_found
context_size_chars
context_size_tokens_approx
```

---

## 12. LLM Usage Plan

### 12.1 LLM Role

The LLM should not predict.

The LLM should:

```text
explain the prediction
use RAG evidence
summarize risk
recommend actions
mention uncertainty
format output for UI
```

### 12.2 Models Available

```text
llama3:latest
qwen3:8b
qwen3:4b
qwen2.5:latest
gpt-oss:20b
llama3.2:3b
```

### 12.3 Embedding Model

```text
nomic-embed-text:latest
```

### 12.4 Suggested Model Roles

```text
qwen3:8b        -> default narrative model
qwen3:4b        -> faster lightweight explanation
qwen2.5         -> fallback general model
llama3          -> baseline comparison
llama3.2:3b     -> low-latency quick alert summary
gpt-oss:20b     -> heavier final analysis
qwen3-coder     -> optional log/code/config explanation
nomic-embed     -> RAG embeddings
```

### 12.5 LLM Prompt Contract

Input:

```json
{
  "live_telemetry": {},
  "feature_vector": {},
  "prediction": {},
  "risk_assessment": {},
  "retrieved_context": []
}
```

Output:

```json
{
  "alert_title": "",
  "severity": "",
  "prediction_summary": "",
  "evidence_used": [],
  "likely_cause": "",
  "recommended_actions": [],
  "confidence": "",
  "uncertainty": ""
}
```

### 12.6 LLM Metrics

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

## 13. React Interface Plan

Keep the UI simple but useful.

### 13.1 Pages / Panels

Single page dashboard:

```text
Live Telemetry Panel
Prediction Panel
Alert Panel
RAG Evidence Panel
LLM Narrative Panel
Metrics Panel
```

### 13.2 UI Behavior

The UI connects to:

```text
/ws/telemetry
```

It displays events progressively:

```text
Telemetry received
Feature vector generated
Prediction generated
Alert triggered
RAG evidence retrieved
LLM narrative generated
Final metrics updated
```

### 13.3 Important UI Learning

The alert should appear before the LLM explanation if needed.

Reason:

```text
ML alert is fast.
RAG + LLM explanation may take longer.
```

So the user should see:

```text
Immediate alert first.
Narrative explanation second.
```

This mimics real production behavior.

---

## 14. Runtime Data Storage and Future Learning Loop

Live inputs should not disappear after inference.

Every live stream event should be stored for future use.

### 14.1 Runtime Archive

Store:

```text
outputs/runtime/telemetry_log.jsonl
outputs/runtime/feature_log.jsonl
outputs/runtime/prediction_log.jsonl
outputs/runtime/rag_log.jsonl
outputs/runtime/llm_log.jsonl
outputs/runtime/alert_log.jsonl
outputs/runtime/outcome_log.jsonl
```

### 14.2 Why Store Live Inputs?

Because live data becomes future training data.

The loop is:

```text
live telemetry
    ↓
prediction made
    ↓
alert emitted
    ↓
actual outcome observed
    ↓
prediction correctness measured
    ↓
dataset updated
    ↓
future retraining
```

### 14.3 Outcome Labeling

After a stream run ends, we can label:

```text
Did memory actually cross threshold?
When did it cross?
Was alert early?
Was alert late?
Was alert false positive?
Was LLM explanation grounded?
```

Example:

```json
{
  "run_id": "run_001",
  "predicted_breach": true,
  "actual_breach": true,
  "predicted_at_second": 34,
  "actual_breach_second": 47,
  "lead_time_seconds": 13,
  "false_positive": false
}
```

### 14.4 Future Retraining

The future retraining dataset can include:

```text
original historical data
new telemetry logs
feature vectors
predictions
actual outcomes
human feedback
```

This is the real learning loop.

The LLM does not magically learn from the stream.

The system improves when:

```text
runtime data is stored
outcomes are labeled
features are regenerated
models are retrained
evaluation improves
```

---

## 15. Metrics Plan

### 15.1 ML Training Metrics

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

### 15.2 Runtime ML Metrics

```text
inference_latency_ms
breach_probability
predicted_memory_mb_30s
prediction_status
detection_second
actual_breach_second
lead_time_seconds
```

### 15.3 RAG Metrics

```text
retrieval_latency_ms
retrieved_doc_count
retrieval_scores
expected_doc_found
context_length
```

### 15.4 LLM Metrics

```text
model_name
latency_ms
json_valid
retry_count
groundedness_score
actionability_score
hallucination_flag
```

### 15.5 WebSocket Metrics

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

### 15.6 End-to-End Metrics

```text
spike_start_second
ml_detection_second
alert_emit_second
rag_complete_second
llm_complete_second
total_explanation_latency_ms
```

---

## 16. Project Folder Structure

```text
KubeSage/
  README.md

  data/
    historical/
      synthetic_pod_telemetry.csv
    live/
      spike_scenario_01.jsonl

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

  models/
    memory_breach_xgb_classifier.json
    future_memory_xgb_regressor.json
    feature_schema.json
    training_metrics.json
    model_card.md

  backend/
    app/
      main.py

      simulator/
        telemetry_simulator.py

      agents/
        telemetry_simulator_agent.py
        metrics_aggregator_agent.py
        feature_builder_agent.py
        prediction_agent.py
        risk_analyzer_agent.py
        rag_retrieval_agent.py
        llm_interface_agent.py
        narrative_agent.py
        alert_agent.py
        evaluation_agent.py

      ml/
        generate_synthetic_data.py
        build_features.py
        train_classifier.py
        train_regressor.py
        model_loader.py

      rag/
        document_loader.py
        keyword_retriever.py
        embedding_retriever.py
        query_builder.py

      schemas/
        telemetry.py
        features.py
        prediction.py
        risk.py
        rag.py
        llm.py
        alert.py

      websocket/
        connection_manager.py
        event_types.py

      services/
        metrics_logger.py
        runtime_archive.py
        config.py

  frontend/
    package.json
    src/
      App.tsx
      components/
        LiveTelemetryPanel.tsx
        PredictionPanel.tsx
        AlertPanel.tsx
        RagEvidencePanel.tsx
        LlmNarrativePanel.tsx
        MetricsPanel.tsx

  outputs/
    runtime/
      telemetry_log.jsonl
      feature_log.jsonl
      prediction_log.jsonl
      rag_log.jsonl
      llm_log.jsonl
      alert_log.jsonl
      outcome_log.jsonl
    reports/
      final_eval_report.json
      llm_comparison_report.json
```

---

## 17. 10–12 Hour Roadmap

---

### Phase 1 — Architecture and Contracts

Estimated time:

```text
1 hour
```

Tasks:

```text
Create repo/folder structure
Define event contracts
Define ML feature schema
Define prediction output schema
Define alert schema
Define LLM output schema
Create README skeleton
```

Deliverables:

```text
schemas/telemetry.py
schemas/features.py
schemas/prediction.py
schemas/alert.py
README.md
```

Acceptance criteria:

```text
Every agent knows what input it receives and what output it produces.
```

---

### Phase 2 — Synthetic Historical Data

Estimated time:

```text
1 hour
```

Tasks:

```text
Generate synthetic pod telemetry
Generate normal traffic pattern
Generate memory spike pattern
Generate post-deployment memory growth pattern
Generate high CPU but stable memory pattern
Generate error-rate spike pattern
Create labels for breach prediction
Create targets for future memory regression
```

Deliverables:

```text
data/historical/synthetic_pod_telemetry.csv
```

Acceptance criteria:

```text
Dataset contains enough normal and abnormal patterns for model training.
```

---

### Phase 3 — Feature Engineering

Estimated time:

```text
1 hour
```

Tasks:

```text
Build feature generator
Compute rolling averages
Compute slopes
Compute ratios
Compute future labels
Save feature schema
Validate training/runtime feature consistency
```

Deliverables:

```text
backend/app/ml/build_features.py
models/feature_schema.json
```

Acceptance criteria:

```text
Given telemetry rows, the system generates model-ready feature rows.
```

---

### Phase 4 — Train XGBoost Models

Estimated time:

```text
1.5 hours
```

Tasks:

```text
Train XGBClassifier for memory breach prediction
Train XGBRegressor for future memory projection
Evaluate classifier metrics
Evaluate regressor metrics
Save model artifacts
Save training metrics
Create basic model card
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
Models can be loaded and used independently for inference.
```

---

### Phase 5 — FastAPI + WebSocket Live Stream

Estimated time:

```text
1 hour
```

Tasks:

```text
Create FastAPI app
Create WebSocket endpoint
Create telemetry simulator
Stream one telemetry event per second
Inject dummy spike during the stream
Send telemetry to UI/client
```

Deliverables:

```text
backend/app/main.py
backend/app/simulator/telemetry_simulator.py
backend/app/websocket/connection_manager.py
```

Acceptance criteria:

```text
A WebSocket client receives live telemetry events for one minute.
```

---

### Phase 6 — Agent Pipeline Without RAG/LLM

Estimated time:

```text
1.5 hours
```

Tasks:

```text
Implement Metrics Aggregator Agent
Implement Feature Builder Agent
Implement Prediction Agent
Implement Risk Analyzer Agent
Implement Alert Agent
Connect agents in sequence
Emit prediction and alert events over WebSocket
```

Deliverables:

```text
agents/metrics_aggregator_agent.py
agents/feature_builder_agent.py
agents/prediction_agent.py
agents/risk_analyzer_agent.py
agents/alert_agent.py
```

Acceptance criteria:

```text
During the dummy spike, the system emits prediction and alert events.
```

---

### Phase 7 — RAG Pipeline

Estimated time:

```text
1.5 hours
```

Tasks:

```text
Create local runbooks
Create incident notes
Create deployment risk notes
Implement document loader
Implement keyword retriever
Implement RAG query builder
Optionally implement embedding retriever with nomic-embed-text
Log retrieved documents and retrieval scores
```

Deliverables:

```text
docs/
backend/app/rag/document_loader.py
backend/app/rag/keyword_retriever.py
backend/app/rag/query_builder.py
backend/app/agents/rag_retrieval_agent.py
```

Acceptance criteria:

```text
A HIGH or CRITICAL prediction retrieves relevant supporting documents.
```

---

### Phase 8 — LLM Interface and Narrative Agent

Estimated time:

```text
1.5 hours
```

Tasks:

```text
Connect to local LLM API
Create prompt template
Send telemetry + prediction + RAG context to LLM
Parse strict JSON response
Retry once on invalid JSON
Emit LLM explanation to WebSocket
```

Initial model:

```text
qwen3:8b
```

Deliverables:

```text
agents/llm_interface_agent.py
agents/narrative_agent.py
schemas/llm.py
```

Acceptance criteria:

```text
The React UI receives a grounded LLM narrative after the ML alert.
```

---

### Phase 9 — React Interface

Estimated time:

```text
1 hour
```

Tasks:

```text
Create simple React app
Connect to WebSocket
Display live telemetry
Display risk score
Display prediction details
Display alert
Display retrieved evidence
Display LLM explanation
Display basic runtime metrics
```

Deliverables:

```text
frontend/src/App.tsx
frontend/src/components/
```

Acceptance criteria:

```text
A user can visually observe the full pipeline from telemetry to alert narrative.
```

---

### Phase 10 — Evaluation and Runtime Archive

Estimated time:

```text
1 hour
```

Tasks:

```text
Log telemetry events
Log feature vectors
Log predictions
Log RAG retrievals
Log LLM responses
Log alerts
Generate final evaluation report
Track detection delay
Track LLM latency
Track RAG latency
Track WebSocket event count
```

Deliverables:

```text
outputs/runtime/*.jsonl
outputs/reports/final_eval_report.json
```

Acceptance criteria:

```text
Each run produces a measurable report.
```

---

### Phase 11 — LLM Comparison Experiment

Estimated time:

```text
1 hour
```

Tasks:

```text
Run same prediction + same RAG context through multiple local models
Compare latency
Compare JSON validity
Compare groundedness
Compare actionability
Compare hallucination tendency
```

Models:

```text
qwen3:8b
qwen3:4b
qwen2.5:latest
llama3:latest
llama3.2:3b
gpt-oss:20b
```

Deliverables:

```text
outputs/reports/llm_comparison_report.json
```

Acceptance criteria:

```text
We know which local model is best for fast alerts, detailed explanations, and strict JSON output.
```

---

### Phase 12 — Learning Log and Wrap-Up

Estimated time:

```text
30–45 minutes
```

Tasks:

```text
Update README
Write what worked
Write what failed
Write what was learned about ML
Write what was learned about RAG
Write what was learned about LLMs
Write the production roadmap
Write how this maps to F1-AI
```

Deliverables:

```text
README.md
LEARNING_LOG.md
```

Acceptance criteria:

```text
The POC can become a blog/article draft.
```

---

## 18. Things That Were Missing From the Initial Description

The original description was strong, but these items should be explicitly added:

### 18.1 Feature Contract

We need a strict feature schema.

Without this, training and runtime inference may drift.

### 18.2 Model Card

We should document:

```text
what the model predicts
what data it was trained on
what features it uses
what its limitations are
```

### 18.3 Outcome Logging

We need to record actual outcomes after prediction.

Otherwise, the model cannot improve later.

### 18.4 Evaluation Metrics

We should not only show alerts.

We should measure:

```text
ML quality
RAG quality
LLM quality
WebSocket latency
end-to-end latency
```

### 18.5 RAG Trigger Policy

RAG should not run on every telemetry event.

It should run only when:

```text
severity == HIGH or CRITICAL
```

### 18.6 LLM Output Contract

The LLM must return strict JSON.

The UI should not parse free-form paragraphs.

### 18.7 Duplicate Alert Control

The Alert Agent should avoid sending the same alert repeatedly every second.

Add cooldown:

```text
same pod + same alert type -> suppress duplicate for 15 seconds
```

### 18.8 Runtime Archive

Live telemetry should be stored for:

```text
replay
debugging
future training
comparison experiments
```

### 18.9 Human Feedback Placeholder

Add optional feedback field:

```text
was_alert_useful: true/false
operator_notes: ""
```

This prepares the future human-in-the-loop design.

---

## 19. Final Acceptance Criteria

The POC is successful if:

```text
1. Historical synthetic telemetry is generated.
2. XGBoost classifier and regressor are trained.
3. Model artifacts are exported.
4. FastAPI loads the models successfully.
5. WebSocket streams live telemetry for one minute.
6. The system buffers the last 30 seconds of telemetry.
7. Feature Builder Agent creates runtime feature vectors.
8. Prediction Agent produces breach probability and future memory projection.
9. Risk Analyzer Agent raises HIGH or CRITICAL severity during spike.
10. RAG Retrieval Agent retrieves relevant runbooks/incidents.
11. LLM returns a grounded JSON explanation.
12. React UI displays telemetry, prediction, evidence, and narrative.
13. Runtime logs are saved.
14. Final evaluation report is generated.
15. At least two LLMs are compared on the same alert context.
```

---

## 20. Production Roadmap

This POC establishes the foundation for production KubeSage.

```text
POC telemetry simulator     -> real Prometheus/OpenTelemetry/Kubernetes metrics
synthetic incidents         -> real incident archive
XGBoost prediction          -> workload risk prediction
RAG docs                    -> runbooks, postmortems, deployment notes
LLM narrative               -> SRE assistant explanation
React dashboard             -> KubeSage UI
runtime archive             -> future training and incident replay
```

---

## 21. How This Maps to F1-AI

The same pattern maps to F1-AI.

```text
pod telemetry               -> lap/sector/tyre telemetry
memory breach prediction    -> lap degradation / pit window prediction
runbooks/incidents          -> race strategy notes / regulations / historical races
Kube alert narrative        -> race strategy explanation
WebSocket stream            -> live race timing stream
runtime archive             -> race replay and model improvement
```

Example F1 version:

```text
Live lap stream
  ↓
30-second/lap-window feature builder
  ↓
XGBoost lap-time or tyre-deg model
  ↓
Strategy risk analyzer
  ↓
RAG over track notes and regulations
  ↓
LLM race strategist narrative
```

---

## 22. Final Summary

This POC is not just a small demo.

It is the bridge between:

```text
ML training
real-time inference
RAG grounding
LLM explanation
agent orchestration
WebSocket delivery
runtime evaluation
future retraining
```

The final learning outcome should be:

```text
I understand how intelligence enters a live software system.
```

This is the correct foundation for evolving KubeSage into a production system and for applying the same pattern to F1-AI.
