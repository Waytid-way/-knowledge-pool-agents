from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SourceRef(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1)
    pages: list[int] = Field(min_length=1)
    element_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_pages(self) -> Self:
        if any(page < 1 for page in self.pages):
            raise ValueError("pages must contain positive page numbers")
        if len(set(self.pages)) != len(self.pages):
            raise ValueError("pages must not contain duplicates")
        return self


class EvidenceItem(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_id: str = Field(min_length=1)
    pool_id: str = Field(min_length=1)
    source: SourceRef
    evidence_type: str = Field(min_length=1)
    payload: dict[str, Any]
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
