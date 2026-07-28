"""Recommended action contract for human-in-the-loop workflows."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from shared.compat import StrEnum

from shared.contracts.base import CONTRACT_VERSION, StrictModel


class ActionType(StrEnum):
    SCALE_UP = "scale_up"
    RESTART_POD = "restart_pod"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    NOTIFY_ON_CALL = "notify_on_call"
    CREATE_TICKET = "create_ticket"


class ActionStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ActionEvent(StrictModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    action_id: str
    created_at: str
    pod_name: str
    action_type: ActionType
    recommended_action: str = Field(..., min_length=1)
    rationale: str = Field(..., min_length=1)
    requires_human_approval: bool
    status: ActionStatus = ActionStatus.PENDING
    expires_at: Optional[str] = None
