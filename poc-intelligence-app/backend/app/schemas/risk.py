"""Risk Reasoning Agent output contract."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from shared.compat import StrEnum

from shared.contracts.base import CONTRACT_VERSION, StrictModel


class RiskLevel(StrEnum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskDecision(StrictModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    decided_at: str
    pod_name: str

    severity: RiskLevel
    alert_required: bool
    rag_required: bool
    human_approval_required: bool

    reason: str = Field(..., min_length=1)
    evidence_query: Optional[str] = None

    input_breach_probability: float = Field(..., ge=0.0, le=1.0)
    input_future_memory_mb: float = Field(..., ge=0)
