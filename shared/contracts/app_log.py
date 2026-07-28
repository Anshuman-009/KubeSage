"""Structured application log event."""

from typing import Literal

from pydantic import Field

from shared.compat import StrEnum

from shared.contracts.base import CONTRACT_VERSION, StrictModel


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AppLogEvent(StrictModel):
    type: Literal["app_log"] = "app_log"
    contract_version: str = Field(default=CONTRACT_VERSION)
    timestamp: str
    pod_name: str
    level: LogLevel
    message: str = Field(..., min_length=1)
    trace_id: str
    latency_ms: float = Field(..., ge=0)
