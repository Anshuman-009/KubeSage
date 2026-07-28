# Deployment Notes

## 2026-07-13 09:04 UTC — payment-api v2.3.1
- Namespace: payments
- Change type: application rollout
- Change summary: enabled new payment validation cache and increased batch size.
- Risk note: previous cache-related changes have caused heap growth when request volume increases.
- Watch signals: memory slope, latency p95, error rate, restart count.

## 2026-07-13 09:05:30 UTC — checkout-api v2.3.1
- Namespace: checkout
- Change type: application rollout
- Change summary: new checkout pricing path enabled.
- Risk note: CPU saturation possible if pricing calls are not cached.

## 2026-07-13 09:04:50 UTC — catalog-api config update
- Namespace: catalog
- Change type: ConfigMap update
- Change summary: database pool max wait reduced from 2000 ms to 700 ms.
- Risk note: short wait timeout may produce DB_POOL_EXHAUSTION under traffic.
