from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import KnowledgeStatus, PoolScope
from .evidence import SourceRef


class KnowledgeObject(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    object_id: str = Field(min_length=1)
    object_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    pool_id: str = Field(min_length=1)
    scope: PoolScope
    project_id: str | None = None
    status: KnowledgeStatus
    content: dict[str, Any]
    sources: list[SourceRef] = Field(min_length=1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if self.scope is PoolScope.PROJECT and not self.project_id:
            raise ValueError("project_id is required for project scope")
        if self.scope is PoolScope.GLOBAL and self.project_id is not None:
            raise ValueError("project_id is not allowed for global scope")
        return self


class Relationship(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    relationship_id: str = Field(min_length=1)
    source_object_id: str = Field(min_length=1)
    relationship_type: str = Field(min_length=1)
    target_object_id: str = Field(min_length=1)
    sources: list[SourceRef] = Field(min_length=1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def reject_self_relationship(self) -> Self:
        if self.source_object_id == self.target_object_id:
            raise ValueError("a relationship must connect different objects")
        return self


class QuestionObject(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    question_id: str = Field(min_length=1)
    question_type: str = Field(min_length=1)
    question: str = Field(min_length=1)
    pool_id: str = Field(min_length=1)
    scope: PoolScope
    project_id: str | None = None
    answer_object_ids: list[str] = Field(min_length=1)
    sources: list[SourceRef] = Field(min_length=1)
    answerability: str = "fully_answerable"

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if self.scope is PoolScope.PROJECT and not self.project_id:
            raise ValueError("project_id is required for project scope")
        if self.scope is PoolScope.GLOBAL and self.project_id is not None:
            raise ValueError("project_id is not allowed for global scope")
        if len(set(self.answer_object_ids)) != len(self.answer_object_ids):
            raise ValueError("answer_object_ids must not contain duplicates")
        return self
