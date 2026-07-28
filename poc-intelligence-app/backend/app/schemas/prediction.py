"""ML prediction output contract."""

from pydantic import Field, model_validator

from shared.contracts.base import CONTRACT_VERSION, StrictModel


class ModelVersions(StrictModel):
    classifier: str
    regressor: str


class PredictionEvent(StrictModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    timestamp: str
    pod_name: str
    prediction_horizon: str = "next_30_seconds"

    breach_probability: float = Field(..., ge=0.0, le=1.0)
    breach_likely: bool
    predicted_memory_mb_30s: float = Field(..., ge=0)
    predicted_memory_ratio_30s: float = Field(..., ge=0)

    model_versions: ModelVersions

    @model_validator(mode="after")
    def validate_breach_likely(self) -> "PredictionEvent":
        expected = self.breach_probability >= 0.5
        if self.breach_likely != expected:
            raise ValueError("breach_likely must match breach_probability >= 0.5")
        return self
