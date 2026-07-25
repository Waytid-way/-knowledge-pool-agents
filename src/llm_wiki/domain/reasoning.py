from pydantic import BaseModel, ConfigDict, Field

from .enums import ReasoningMode
from .evidence import SourceRef


class ReasoningTrace(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    trace_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    modes: list[ReasoningMode] = Field(default_factory=list)
    facts: list[str]
    rules: list[str]
    hypotheses: list[str]
    decision: str = Field(min_length=1)
    outcome: str = Field(min_length=1)
    source_refs: list[SourceRef] = Field(min_length=1)
