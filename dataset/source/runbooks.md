# Runbooks

## Memory Spike / Possible Memory Leak
Use when memory ratio is high, memory slope is positive, and memory growth follows a recent deployment.
Checks: compare memory growth across replicas, check deployment age, review MEMORY_PRESSURE logs, check OOMKilled events, inspect heap/object allocation.
Safe actions: notify service owner, increase alert severity, prepare rollback recommendation, prepare temporary scaling recommendation.
Human approval required: rollback, restart pod, change memory limit, scale production deployment.

## OOMKilled Response
Confirm restart count, check memory ratio before restart, check gradual vs sudden growth, check recent deployment.
Safe actions: retrieve previous pod logs, summarize incident, recommend rollback or memory-limit review.

## High CPU / Readiness Probe Failure
Check CPU saturation duration, compare request rate and latency, inspect dependency call logs, check rollout notes.
Human approval required: scale deployment, rollback deployment, restart pod.
