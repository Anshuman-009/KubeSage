"""Kubernetes-style cluster event."""

from typing import Literal

from pydantic import Field

from shared.contracts.base import CONTRACT_VERSION, StrictModel


class KubeEvent(StrictModel):
    type: Literal["kube_event"] = "kube_event"
    contract_version: str = Field(default=CONTRACT_VERSION)
    timestamp: str
    pod_name: str
    reason: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
