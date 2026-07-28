# Incident Archive

## INC-2026-05-23 — payment-api memory growth after deployment

### Affected service
payment-api in payments namespace.

### Symptoms
- Memory usage increased continuously after deployment.
- Memory slope stayed positive for more than 5 minutes.
- Error rate increased after memory ratio crossed 80%.
- Readiness probe failures appeared before OOMKilled.
- One pod restart occurred after memory limit pressure.

### Root cause
A cache introduced in the payment validation path retained request-scoped objects longer than expected.

### Resolution
Rolled back to previous deployment, reduced batch size, and inspected heap allocation.

---

## INC-2026-05-28 — catalog-api database pool exhaustion

Symptoms: latency p95 increased, DB pool timeout logs appeared, error rate grew, memory stayed stable.
Root cause: database pool max wait timeout was reduced too aggressively.
Resolution: restored previous pool wait timeout and added dashboard alert.

---

## INC-2026-06-02 — checkout-api CPU saturation during pricing rollout

Symptoms: CPU usage spiked, readiness probe failures occurred, latency p95 increased.
Root cause: new pricing path missed cache hits and caused repeated downstream calls.
Resolution: enabled cache and added circuit breaker.
