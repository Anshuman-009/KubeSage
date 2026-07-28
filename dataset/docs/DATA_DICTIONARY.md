# Data Dictionary

## source/historical_telemetry.csv
Production-style synthetic pod/container telemetry at 1-second granularity.

## derived/derived_features.csv
Rolling-window ML features generated from historical telemetry.

## derived/training_labels.csv
Training labels and future targets for XGBoost.

## source/app_logs.jsonl
Structured application logs aligned with telemetry scenarios.

## source/k8s_events.jsonl
Synthetic Kubernetes events aligned with telemetry scenarios.

## source/incident_archive.md
Past incident reports used for RAG evidence.

## source/runbooks.md
Operational guidance used by the Action/Alert Agent.
