"""Live pod telemetry event streamed from Mock Kube Telemetry App."""

from typing import Literal

from pydantic import Field

from shared.contracts.base import CONTRACT_VERSION, StrictModel


class TelemetryEvent(StrictModel):
    type: Literal["telemetry"] = "telemetry"
    contract_version: str = Field(default=CONTRACT_VERSION)
    timestamp: str
    namespace: str
    pod_name: str
    container_name: str
    memory_mb: float = Field(..., ge=0)
    memory_limit_mb: float = Field(..., gt=0)
    cpu_pct: float = Field(..., ge=0, le=100)
    request_rate: float = Field(..., ge=0)
    error_rate: float = Field(..., ge=0)
    restart_count: int = Field(..., ge=0)
    deployment_age_minutes: int = Field(..., ge=0)
