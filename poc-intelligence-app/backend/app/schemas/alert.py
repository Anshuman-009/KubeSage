"""Alert event emitted to UI and runtime archive."""

from pydantic import Field

from shared.contracts.base import CONTRACT_VERSION, StrictModel

from .risk import RiskLevel


class AlertEvent(StrictModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    alert_id: str
    emitted_at: str
    pod_name: str
    severity: RiskLevel
    alert_title: str = Field(..., min_length=1)
    prediction_summary: str = Field(..., min_length=1)
    suppressed_duplicate: bool = False
