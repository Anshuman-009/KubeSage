"""Human approval / rejection feedback contract."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from shared.compat import StrEnum

from shared.contracts.base import CONTRACT_VERSION, StrictModel


class HumanFeedbackDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"


class HumanFeedbackEvent(StrictModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    action_id: str
    decision: HumanFeedbackDecision
    decided_by: str = Field(..., min_length=1)
    decided_at: str
    notes: Optional[str] = None
