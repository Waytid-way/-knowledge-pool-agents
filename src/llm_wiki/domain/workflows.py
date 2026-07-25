from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import WorkflowState


_ALLOWED_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.DOCUMENT_REGISTERED: {
        WorkflowState.PROFILED,
        WorkflowState.FAILED,
        WorkflowState.QUARANTINED,
    },
    WorkflowState.PROFILED: {
        WorkflowState.STRUCTURE_MAPPED,
        WorkflowState.NEEDS_HUMAN_REVIEW,
        WorkflowState.FAILED,
    },
    WorkflowState.STRUCTURE_MAPPED: {
        WorkflowState.READING_UNITS_CREATED,
        WorkflowState.NEEDS_REPROCESSING,
        WorkflowState.FAILED,
    },
    WorkflowState.READING_UNITS_CREATED: {
        WorkflowState.OBJECTS_EXTRACTED,
        WorkflowState.NEEDS_REPROCESSING,
        WorkflowState.FAILED,
    },
    WorkflowState.OBJECTS_EXTRACTED: {
        WorkflowState.OBJECTS_NORMALIZED,
        WorkflowState.NEEDS_REPROCESSING,
        WorkflowState.FAILED,
    },
    WorkflowState.OBJECTS_NORMALIZED: {
        WorkflowState.GRAPH_BUILT,
        WorkflowState.NEEDS_HUMAN_REVIEW,
        WorkflowState.FAILED,
    },
    WorkflowState.GRAPH_BUILT: {
        WorkflowState.COVERAGE_VERIFIED,
        WorkflowState.NEEDS_REPROCESSING,
        WorkflowState.FAILED,
    },
    WorkflowState.COVERAGE_VERIFIED: {
        WorkflowState.WIKI_COMPOSED,
        WorkflowState.NEEDS_REPROCESSING,
        WorkflowState.NEEDS_HUMAN_REVIEW,
        WorkflowState.FAILED,
    },
    WorkflowState.WIKI_COMPOSED: {
        WorkflowState.PUBLISHED,
        WorkflowState.NEEDS_HUMAN_REVIEW,
        WorkflowState.FAILED,
    },
}


class WorkflowRun(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    run_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    pool_id: str = Field(min_length=1)
    current_state: WorkflowState
    requested_state: WorkflowState
    attempt: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_transition(self) -> Self:
        allowed = _ALLOWED_TRANSITIONS.get(self.current_state, set())
        if self.requested_state not in allowed:
            if self.requested_state is WorkflowState.PUBLISHED:
                raise ValueError("workflow cannot jump directly to published")
            raise ValueError(
                f"transition from {self.current_state} to {self.requested_state} is not allowed"
            )
        return self
