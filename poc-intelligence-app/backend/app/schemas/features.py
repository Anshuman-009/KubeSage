"""Rolling-window feature vector for ML training and runtime inference."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from shared.contracts.base import CONTRACT_VERSION, StrictModel


class FeatureVector(StrictModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    timestamp: str
    pod_name: str
    service_name: str
    namespace: str
    scenario_tag: Optional[str] = None

    memory_current_mb: float = Field(..., ge=0)
    memory_limit_mb: float = Field(..., gt=0)
    memory_ratio_current: float = Field(..., ge=0)
    memory_avg_5s: float = Field(..., ge=0)
    memory_avg_10s: float = Field(..., ge=0)
    memory_avg_30s: float = Field(..., ge=0)
    memory_slope_5s: float
    memory_slope_10s: float
    memory_slope_30s: float
    memory_std_30s: float = Field(..., ge=0)

    cpu_current_mcores: float = Field(..., ge=0)
    cpu_avg_5s: float = Field(..., ge=0)
    cpu_avg_10s: float = Field(..., ge=0)
    cpu_avg_30s: float = Field(..., ge=0)
    cpu_slope_10s: float

    error_rate_current: float = Field(..., ge=0)
    error_rate_avg_5s: float = Field(..., ge=0)
    error_rate_avg_30s: float = Field(..., ge=0)
    error_rate_slope_10s: float

    request_rate_current: float = Field(..., ge=0)
    request_rate_avg_30s: float = Field(..., ge=0)
    request_rate_slope_10s: float

    latency_p95_current: float = Field(..., ge=0)
    latency_p95_avg_30s: float = Field(..., ge=0)
    latency_p95_slope_10s: float

    restart_count: int = Field(..., ge=0)
    deployment_age_minutes: int = Field(..., ge=0)
    recent_deployment_flag: int = Field(..., ge=0, le=1)
