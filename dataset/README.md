# KubeSage Production-Style Synthetic Dataset Pack

Generated for `KubeSage`.

This dataset pack is synthetic, but it is designed to behave like a production Kubernetes observability ecosystem. The goal is not to create random dummy data. The goal is to create connected datasets where telemetry, logs, Kubernetes events, deployment changes, incidents, runbooks, labels, and runtime outputs all make sense together.

---

## 1. Purpose

This dataset pack supports the POC:

```text
KubeSage
Real-Time ML + RAG + LLM Alert Intelligence for Kubernetes Telemetry
```

The POC is meant to understand:

```text
1. How historical telemetry becomes ML training data.
2. How XGBoost models predict operational risk.
3. How live telemetry is converted into rolling-window features.
4. How RAG retrieves evidence from logs, events, incidents, deployment notes, and runbooks.
5. How LLMs generate user-understandable alert narratives.
6. How runtime predictions, alerts, outcomes, and human feedback can become future training data.
```

---

## 2. Dataset Contents

```text
source/
  historical_telemetry.csv
  app_logs.jsonl
  k8s_events.jsonl
  incident_archive.md
  runbooks.md
  deployment_notes.md

derived/
  derived_features.csv
  training_labels.csv

runtime/
  telemetry_log.jsonl
  prediction_log.jsonl
  alert_log.jsonl
  outcome_log.jsonl
  human_feedback.jsonl

docs/
  DATA_DICTIONARY.md
```

---

## 3. Dataset Scale

```text
Historical telemetry rows: 10800
Derived feature rows: 10080
Training label rows: 10080
Application log rows: 2329
Kubernetes event rows: 9
```

---

## 4. Scenario Coverage

The dataset contains six production-style service scenarios:

```text
1. payment-api
   Scenario: memory leak after deployment

2. checkout-api
   Scenario: CPU saturation and readiness failures

3. catalog-api
   Scenario: database pool exhaustion

4. auth-api
   Scenario: normal behavior with minor noise

5. order-worker
   Scenario: restart and recovery

6. edge-gateway
   Scenario: traffic surge
```

These scenarios are intentionally connected across telemetry, logs, events, incidents, and runbooks.

Example:

```text
payment-api deployment happens
  ↓
memory usage starts rising
  ↓
latency and error rate increase
  ↓
logs show MEMORY_PRESSURE
  ↓
Kubernetes event shows ReadinessProbeFailed / OOMKilled
  ↓
incident_archive.md has a similar previous incident
  ↓
runbooks.md suggests investigation and safe next actions
```

---

# 5. Dataset Responsibility Map

## 5.1 `source/historical_telemetry.csv`

### Purpose

This is the main source dataset for ML training and simulation.

It represents historical Kubernetes pod/container metrics over time.

### Contains

```text
timestamp
cluster_id
namespace
deployment_name
service_name
pod_name
container_name
node_name
cpu_usage_mcores
cpu_limit_mcores
memory_usage_mb
memory_limit_mb
memory_working_set_mb
network_rx_kbps
network_tx_kbps
disk_read_kbps
disk_write_kbps
request_rate_rps
error_rate_rps
latency_p50_ms
latency_p95_ms
restart_count
pod_phase
ready
deployment_age_minutes
scenario_tag
event_hint
```

### Used by

```text
ML training pipeline
Feature engineering pipeline
Mock Kube Telemetry App
Prediction Agent
Evaluation pipeline
```

### Processing

```text
historical_telemetry.csv
  ↓
rolling-window feature generation
  ↓
derived_features.csv
  ↓
XGBoost model training
```

### Achieves

This dataset teaches the ML model how different telemetry patterns behave before operational failure.

It is used to train:

```text
XGBClassifier
  → predicts whether memory breach is likely

XGBRegressor
  → predicts future memory usage
```

---

## 5.2 `derived/derived_features.csv`

### Purpose

This is the processed ML feature table generated from `historical_telemetry.csv`.

The model should not learn directly from raw telemetry rows. It should learn from rolling-window features.

### Contains

```text
feature_id
timestamp
pod_name
service_name
namespace
scenario_tag
memory_current_mb
memory_limit_mb
memory_ratio_current
memory_avg_5s
memory_avg_10s
memory_avg_30s
memory_slope_5s
memory_slope_10s
memory_slope_30s
memory_std_30s
cpu_current_mcores
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
latency_p95_current
latency_p95_avg_30s
latency_p95_slope_10s
restart_count
deployment_age_minutes
recent_deployment_flag
```

### Used by

```text
XGBoost training
Runtime feature contract validation
Prediction Agent
Evaluation Agent
```

### Processing

```text
historical_telemetry.csv
  ↓
compute rolling averages
compute slopes
compute ratios
compute recent deployment flags
  ↓
derived_features.csv
```

### Achieves

This dataset converts raw telemetry into ML-ready signals.

Example:

```text
Raw memory value:
memory_usage_mb = 850

Useful production feature:
memory_slope_10s = rapidly increasing
memory_ratio_current = 0.83
recent_deployment_flag = true
```

This helps the model learn patterns like:

```text
High memory ratio + positive memory slope + recent deployment = high memory risk
```

---

## 5.3 `derived/training_labels.csv`

### Purpose

This file contains the labels and future targets required for supervised ML training.

### Contains

```text
feature_id
timestamp
pod_name
service_name
label_memory_breach_next_30s
target_memory_mb_30s
target_memory_ratio_30s
actual_breach_within_30s
first_breach_second_offset
```

### Used by

```text
XGBClassifier training
XGBRegressor training
Model evaluation
Future retraining comparison
```

### Processing

```text
historical_telemetry.csv
  ↓
look ahead 30 seconds
  ↓
create breach labels and future memory targets
  ↓
training_labels.csv
```

### Achieves

This file defines what the ML models are learning.

Classifier target:

```text
label_memory_breach_next_30s
```

Meaning:

```text
Will memory cross 90% of its limit in the next 30 seconds?
```

Regressor target:

```text
target_memory_mb_30s
```

Meaning:

```text
What will memory usage be 30 seconds from now?
```

---

## 5.4 `source/app_logs.jsonl`

### Purpose

This file contains structured application logs aligned with telemetry behavior.

It is mainly used for RAG evidence and LLM explanation.

### Contains

```text
timestamp
cluster_id
namespace
service_name
pod_name
container_name
log_level
message
error_type
trace_id
request_id
latency_ms
scenario_tag
```

### Used by

```text
RAG Evidence Agent
Risk Reasoning Agent
LLM Narrative Agent
Diagnosis flow
```

### Processing

```text
app_logs.jsonl
  ↓
filter by service / timestamp / error_type
  ↓
summarize or chunk logs
  ↓
retrieve relevant evidence during high-risk prediction
```

### Achieves

This dataset helps answer:

```text
Why might this prediction be happening?
```

Example:

```text
ML says:
payment-api has high memory breach probability.

RAG retrieves log:
heap usage rising after deployment; GC pressure increasing.

LLM explains:
The prediction is supported by app logs showing memory pressure after deployment.
```

---

## 5.5 `source/k8s_events.jsonl`

### Purpose

This file contains Kubernetes-style events aligned with telemetry and logs.

It provides cluster-level symptom context.

### Contains

```text
timestamp
cluster_id
namespace
service_name
pod_name
event_type
event_reason
event_message
severity
```

Example event reasons:

```text
DeploymentRollout
ReadinessProbeFailed
OOMKilled
ConfigMapUpdated
HighErrorRate
CrashLoopBackOff
TrafficSurge
```

### Used by

```text
RAG Evidence Agent
Risk Reasoning Agent
LLM Narrative Agent
Action / Alert Agent
```

### Processing

```text
k8s_events.jsonl
  ↓
normalize event reason
  ↓
align with telemetry timestamp
  ↓
retrieve as supporting evidence
```

### Achieves

This dataset connects raw metrics to Kubernetes behavior.

Example:

```text
Telemetry:
memory is rising

Logs:
memory pressure increasing

K8s event:
ReadinessProbeFailed

Later event:
OOMKilled
```

This gives the LLM stronger evidence than metrics alone.

---

## 5.6 `source/deployment_notes.md`

### Purpose

This file contains synthetic deployment/change history.

Production failures often happen after deployments or config changes, so this file gives the system change context.

### Contains

```text
deployment timestamp
service name
namespace
version
change summary
risk note
watch signals
```

### Used by

```text
RAG Evidence Agent
Risk Reasoning Agent
LLM Narrative Agent
Action / Alert Agent
```

### Processing

```text
deployment_notes.md
  ↓
chunk by deployment section
  ↓
retrieve when recent_deployment_flag is true
```

### Achieves

This dataset helps answer:

```text
Did something change before the risk appeared?
```

Example:

```text
payment-api v2.3.1 deployed
  ↓
new payment validation cache enabled
  ↓
memory starts rising
  ↓
RAG retrieves deployment note
  ↓
LLM says recent deployment may be related, but marks uncertainty
```

---

## 5.7 `source/incident_archive.md`

### Purpose

This file contains historical incident reports.

It provides past-case evidence for RAG.

### Contains

```text
incident id
affected service
symptoms
observed signals
root cause
resolution
recommended detection logic
```

### Used by

```text
RAG Evidence Agent
LLM Narrative Agent
Risk Reasoning Agent
Evaluation Agent
```

### Processing

```text
incident_archive.md
  ↓
chunk by incident
  ↓
embed or keyword-index each incident
  ↓
retrieve similar incident for current alert
```

### Achieves

This dataset helps the system say:

```text
This resembles a previous incident.
```

Example:

```text
Current prediction:
payment-api memory breach likely.

Retrieved incident:
INC-2026-05-23 payment-api memory growth after deployment.

LLM narrative:
This pattern resembles INC-2026-05-23, where memory growth after deployment led to OOMKilled.
```

---

## 5.8 `source/runbooks.md`

### Purpose

This file contains operational guidance.

It tells the Action / Alert Agent and LLM what actions are safe to recommend.

### Contains

```text
memory spike runbook
OOMKilled response
high CPU / readiness probe failure
checks
safe actions
human approval required actions
```

### Used by

```text
Action / Alert Agent
LLM Narrative Agent
RAG Evidence Agent
Human approval flow
```

### Processing

```text
runbooks.md
  ↓
chunk by runbook section
  ↓
retrieve relevant action guidance
  ↓
LLM formats next steps
```

### Achieves

This dataset prevents the LLM from inventing actions.

Example:

```text
Safe action:
retrieve logs, notify service owner, prepare rollback recommendation

Human approval required:
rollback deployment, restart pod, scale production deployment
```

---

# 6. Runtime Dataset Responsibilities

The runtime files are placeholders initially. They will be generated by the POC application during live runs.

---

## 6.1 `runtime/telemetry_log.jsonl`

### Purpose

Stores live telemetry received from the Mock Kube Telemetry App.

### Produced by

```text
Stream Ingestion Service
```

### Used for

```text
debugging
replay
future training
runtime evaluation
```

---

## 6.2 `runtime/prediction_log.jsonl`

### Purpose

Stores every ML prediction made during live execution.

### Produced by

```text
Prediction Agent
Risk Reasoning Agent
```

### Contains

```text
timestamp
pod_name
breach_probability
predicted_memory_mb_30s
severity
model_version
inference_latency_ms
```

### Used for

```text
prediction evaluation
model comparison
future retraining
```

---

## 6.3 `runtime/alert_log.jsonl`

### Purpose

Stores alerts emitted to the React UI.

### Produced by

```text
Action / Alert Agent
```

### Contains

```text
timestamp
pod_name
severity
alert_title
alert_message
recommended_action
human_approval_required
```

### Used for

```text
alert audit trail
duplicate alert control
operator review
```

---

## 6.4 `runtime/outcome_log.jsonl`

### Purpose

Stores what actually happened after a prediction.

### Produced by

```text
Evaluation Agent
```

### Contains

```text
run_id
pod_name
predicted_breach
actual_breach
predicted_at_second
actual_breach_second
lead_time_seconds
false_positive
false_negative
```

### Used for

```text
model evaluation
future labeling
future retraining
```

---

## 6.5 `runtime/human_feedback.jsonl`

### Purpose

Stores human/operator feedback.

### Produced by

```text
React UI
Human review flow
Action / Alert Agent
```

### Contains

```text
alert_id
was_alert_useful
was_recommendation_correct
operator_notes
approved_action
rejected_action
```

### Used for

```text
human-in-the-loop learning
agent evaluation
future dataset improvement
```

---

# 7. End-to-End Dataset Flow

```text
source/historical_telemetry.csv
      ↓
derived/derived_features.csv
      ↓
derived/training_labels.csv
      ↓
Train XGBClassifier + XGBRegressor
      ↓
Export model artifacts
      ↓

Mock Kube Telemetry App
      ↓
runtime/telemetry_log.jsonl
      ↓
30-sec live buffer
      ↓
runtime feature vector
      ↓
Prediction Agent
      ↓
runtime/prediction_log.jsonl
      ↓
Risk Reasoning Agent
      ↓
If HIGH / CRITICAL:
      ↓
RAG Evidence Agent retrieves from:
  - source/app_logs.jsonl
  - source/k8s_events.jsonl
  - source/deployment_notes.md
  - source/incident_archive.md
  - source/runbooks.md
      ↓
LLM Narrative Agent
      ↓
Action / Alert Agent
      ↓
runtime/alert_log.jsonl
      ↓
React UI
      ↓
Human feedback
      ↓
runtime/human_feedback.jsonl
      ↓
Evaluation Agent
      ↓
runtime/outcome_log.jsonl
      ↓
Future retraining dataset
```

---

# 8. Cursor Implementation Guidance

Cursor should treat the datasets as follows:

## ML Training Inputs

Use:

```text
derived/derived_features.csv
derived/training_labels.csv
```

Join on:

```text
feature_id
```

Train:

```text
XGBClassifier
  input: derived_features.csv
  target: label_memory_breach_next_30s

XGBRegressor
  input: derived_features.csv
  target: target_memory_mb_30s
```

---

## Runtime Simulation Input

Use:

```text
source/historical_telemetry.csv
```

The Mock Kube App can replay rows from this file as live telemetry.

Recommended replay behavior:

```text
one row per second
filter by selected scenario_tag
stream by timestamp order
```

---

## RAG Inputs

Use:

```text
source/app_logs.jsonl
source/k8s_events.jsonl
source/deployment_notes.md
source/incident_archive.md
source/runbooks.md
```

Chunk/index them by:

```text
service_name
timestamp
scenario_tag
incident id
runbook section
event_reason
```

---

## Runtime Outputs

Write to:

```text
runtime/telemetry_log.jsonl
runtime/prediction_log.jsonl
runtime/alert_log.jsonl
runtime/outcome_log.jsonl
runtime/human_feedback.jsonl
```

---

# 9. What This Dataset Pack Achieves

This dataset pack gives the POC a production-shaped learning environment.

It supports:

```text
1. ML training from historical telemetry.
2. Real-time prediction from live telemetry replay.
3. Risk reasoning from prediction + thresholds.
4. RAG grounding from logs, events, deployment notes, incidents, and runbooks.
5. LLM narrative generation.
6. Human approval simulation.
7. Runtime audit logging.
8. Future model improvement through outcome and feedback logs.
```

The key idea:

```text
Telemetry teaches the model.
Logs and events explain symptoms.
Deployment notes explain recent changes.
Incidents provide historical evidence.
Runbooks provide action guidance.
Runtime logs create the next training cycle.
```
