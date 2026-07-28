"""Contract validation tests for Phase 1 schemas."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.action import ActionEvent, ActionStatus, ActionType
from app.schemas.alert import AlertEvent
from app.schemas.app_log import AppLogEvent
from app.schemas.features import FeatureVector
from app.schemas.feedback import HumanFeedbackDecision, HumanFeedbackEvent
from app.schemas.kube_event import KubeEvent
from app.schemas.llm import LlmNarrative
from app.schemas.prediction import PredictionEvent
from app.schemas.risk import RiskDecision, RiskLevel
from app.schemas.telemetry import TelemetryEvent


def test_telemetry_event_validates_known_good_payload() -> None:
    event = TelemetryEvent.model_validate(
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
            "deployment_age_minutes": 12,
        }
    )
    assert event.type == "telemetry"
    assert event.memory_mb == 842


def test_app_log_event_validates_known_good_payload() -> None:
    event = AppLogEvent.model_validate(
        {
            "type": "app_log",
            "timestamp": "00:33",
            "pod_name": "payment-api-7d9f",
            "level": "ERROR",
            "message": "request timeout while calling ledger-service",
            "trace_id": "trace-001",
            "latency_ms": 2300,
        }
    )
    assert event.level.value == "ERROR"


def test_kube_event_validates_known_good_payload() -> None:
    event = KubeEvent.model_validate(
        {
            "type": "kube_event",
            "timestamp": "00:42",
            "pod_name": "payment-api-7d9f",
            "reason": "OOMKilled",
            "message": "Container was terminated due to memory pressure",
        }
    )
    assert event.reason == "OOMKilled"


def test_feature_vector_validates_known_good_payload() -> None:
    features = FeatureVector.model_validate(
        {
            "timestamp": "2026-07-13T09:00:30+00:00",
            "pod_name": "auth-api-6d1a0",
            "service_name": "auth-api",
            "namespace": "auth",
            "scenario_tag": "normal_with_small_noise",
            "memory_current_mb": 214.12,
            "memory_limit_mb": 512,
            "memory_ratio_current": 0.418203125,
            "memory_avg_5s": 212.56,
            "memory_avg_10s": 211.148,
            "memory_avg_30s": 211.1383333333333,
            "memory_slope_5s": 0.589,
            "memory_slope_10s": 0.1056969696969707,
            "memory_slope_30s": 0.1511167964404859,
            "memory_std_30s": 7.914321842702952,
            "cpu_current_mcores": 158.44,
            "cpu_avg_5s": 193.058,
            "cpu_avg_10s": 180.799,
            "cpu_avg_30s": 184.36433333333332,
            "cpu_slope_10s": 3.0599393939393984,
            "error_rate_current": 0.0,
            "error_rate_avg_5s": 0.07,
            "error_rate_avg_30s": 0.06466666666666666,
            "error_rate_slope_10s": -0.019878787878787874,
            "request_rate_current": 76.85,
            "request_rate_avg_30s": 77.823,
            "request_rate_slope_10s": -0.6546666666666643,
            "latency_p95_current": 120.39,
            "latency_p95_avg_30s": 114.46866666666666,
            "latency_p95_slope_10s": -0.15218181818181648,
            "restart_count": 0,
            "deployment_age_minutes": 1470,
            "recent_deployment_flag": 0,
        }
    )
    assert features.pod_name == "auth-api-6d1a0"


def test_prediction_event_validates_known_good_payload() -> None:
    prediction = PredictionEvent.model_validate(
        {
            "timestamp": "2026-07-13T09:09:00+00:00",
            "pod_name": "payment-api-7d9f",
            "breach_probability": 0.86,
            "breach_likely": True,
            "predicted_memory_mb_30s": 940,
            "predicted_memory_ratio_30s": 0.91,
            "model_versions": {
                "classifier": "memory-breach-xgb-v1",
                "regressor": "future-memory-xgb-v1",
            },
        }
    )
    assert prediction.breach_likely is True


def test_risk_decision_validates_known_good_payload() -> None:
    decision = RiskDecision.model_validate(
        {
            "decided_at": "2026-07-13T09:09:05+00:00",
            "pod_name": "payment-api-7d9f",
            "severity": "HIGH",
            "alert_required": True,
            "rag_required": True,
            "human_approval_required": False,
            "reason": "High breach probability and projected memory ratio above warning threshold",
            "evidence_query": "payment-api high memory slope high error rate recent deployment",
            "input_breach_probability": 0.86,
            "input_future_memory_mb": 940,
        }
    )
    assert decision.severity == RiskLevel.HIGH


def test_llm_narrative_validates_known_good_payload() -> None:
    narrative = LlmNarrative.model_validate(
        {
            "alert_title": "Payment API memory breach risk",
            "severity": "HIGH",
            "prediction_summary": "86% breach probability; projected memory 940MB in 30s.",
            "evidence_used": ["incident_2026_05_23_memory_growth.md"],
            "likely_cause": "Possible memory growth after recent deployment",
            "recommended_actions": ["Check recent deployment changes"],
            "requires_human_approval": False,
            "confidence": "medium-high",
            "uncertainty": "Based on synthetic POC telemetry.",
        }
    )
    assert narrative.severity == RiskLevel.HIGH


def test_alert_action_and_feedback_validate_known_good_payloads() -> None:
    alert = AlertEvent.model_validate(
        {
            "alert_id": "alert-001",
            "emitted_at": "2026-07-13T09:09:06+00:00",
            "pod_name": "payment-api-7d9f",
            "severity": "HIGH",
            "alert_title": "Payment API memory breach risk",
            "prediction_summary": "86% breach probability.",
        }
    )
    action = ActionEvent.model_validate(
        {
            "action_id": "action-001",
            "created_at": "2026-07-13T09:09:07+00:00",
            "pod_name": "payment-api-7d9f",
            "action_type": "scale_up",
            "recommended_action": "Scale payment-api from 2 to 4 replicas",
            "rationale": "Memory pressure rising.",
            "requires_human_approval": True,
            "status": "pending",
        }
    )
    feedback = HumanFeedbackEvent.model_validate(
        {
            "action_id": "action-001",
            "decision": "approve",
            "decided_by": "oncall-engineer",
            "decided_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    assert alert.severity == RiskLevel.HIGH
    assert action.action_type == ActionType.SCALE_UP
    assert feedback.decision == HumanFeedbackDecision.APPROVE


def test_stream_contracts_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        TelemetryEvent.model_validate(
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
                "deployment_age_minutes": 12,
                "unexpected_field": True,
            }
        )


def test_producer_and_consumer_share_identical_telemetry_contract() -> None:
    import schemas as producer_schemas

    payload = {
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
        "deployment_age_minutes": 12,
    }
    assert producer_schemas.TelemetryEvent is TelemetryEvent
    assert (
        producer_schemas.TelemetryEvent.model_validate(payload).model_dump()
        == TelemetryEvent.model_validate(payload).model_dump()
    )
