"""LLM Narrative Agent output contract."""

from pydantic import Field

from shared.contracts.base import CONTRACT_VERSION, StrictModel

from .risk import RiskLevel


class LlmNarrative(StrictModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    alert_title: str = Field(..., min_length=1)
    severity: RiskLevel
    prediction_summary: str = Field(..., min_length=1)
    evidence_used: list[str]
    likely_cause: str = Field(..., min_length=1)
    recommended_actions: list[str] = Field(..., min_length=1)
    requires_human_approval: bool
    confidence: str = Field(..., min_length=1)
    uncertainty: str = Field(..., min_length=1)
