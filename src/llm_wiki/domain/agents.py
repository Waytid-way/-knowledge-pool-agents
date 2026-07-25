from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TaskEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    task_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    agent_version: str = Field(min_length=1)
    input: dict[str, Any]
    allowed_read_pools: list[str] = Field(min_length=1)
    allowed_write_pools: list[str] = Field(min_length=1)
    required_output_schema: str = Field(min_length=1)
    attempt: int = Field(default=1, ge=1)
    max_attempts: int = Field(default=3, ge=1)

    @model_validator(mode="after")
    def validate_attempts_and_pools(self) -> "TaskEnvelope":
        if self.attempt > self.max_attempts:
            raise ValueError("attempt cannot exceed max_attempts")
        if len(set(self.allowed_read_pools)) != len(self.allowed_read_pools):
            raise ValueError("allowed_read_pools must not contain duplicates")
        if len(set(self.allowed_write_pools)) != len(self.allowed_write_pools):
            raise ValueError("allowed_write_pools must not contain duplicates")
        return self


class AgentResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    task_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    agent_version: str = Field(min_length=1)
    status: Literal["completed", "completed_with_concerns", "needs_context", "blocked"]
    outputs: list[dict[str, Any]] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    follow_up_requests: list[str] = Field(default_factory=list)
    metrics: dict[str, int | float] = Field(default_factory=dict)
