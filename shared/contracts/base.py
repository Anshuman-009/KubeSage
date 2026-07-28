"""Base contract utilities shared across both applications."""

from pydantic import BaseModel, ConfigDict

CONTRACT_VERSION = "1.0.0"


class StrictModel(BaseModel):
    """Reject unknown fields at application boundaries."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
