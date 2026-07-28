# Mock Kube Telemetry App

Simulates a Kubernetes cluster by streaming pod metrics, application logs, and Kubernetes-style events to the POC Intelligence App.

## Phase 1 — Contracts

Stream event schemas live in `schemas/` and are sourced from the shared contract package at `shared/contracts/`:

- `TelemetryEvent` — pod CPU/memory/request metrics
- `AppLogEvent` — structured application logs
- `KubeEvent` — Kubernetes-style operational events

Both applications import the same canonical models so producer and consumer stay aligned.

## Planned endpoints

```text
GET  /health
GET  /scenarios
POST /scenario/start
POST /scenario/stop
WS   /ws/kube-stream
```

## Run contract tests

From the repository root:

```bash
pip install -e ".[dev]"
pytest tests/test_contracts.py -v
```
