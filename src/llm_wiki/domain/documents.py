from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import DocumentStatus, ElementStatus, PoolScope


class SourceDocument(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1)
    pool_id: str = Field(min_length=1)
    scope: PoolScope
    project_id: str | None = None
    filename: str = Field(min_length=1)
    media_type: str = "application/pdf"
    content_hash: str = Field(min_length=1)
    page_count: int = Field(ge=1)
    status: DocumentStatus = DocumentStatus.REGISTERED

    @model_validator(mode="after")
    def validate_scope(self) -> "SourceDocument":
        if self.scope is PoolScope.PROJECT and not self.project_id:
            raise ValueError("project_id is required for project scope")
        if self.scope is PoolScope.GLOBAL and self.project_id is not None:
            raise ValueError("project_id is not allowed for global scope")
        return self


class PageElement(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    element_id: str = Field(min_length=1)
    element_type: str = Field(min_length=1)
    status: ElementStatus
    label: str | None = None


class PageManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    document_status: DocumentStatus
    section_path: list[str] = Field(default_factory=list)
    elements: list[PageElement] = Field(default_factory=list)
    reading_unit_id: str | None = None


class ReadingUnit(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    unit_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    pages: list[int] = Field(min_length=1)
    expected_elements: dict[str, int] = Field(default_factory=dict)
    continuation_from: str | None = None
    continuation_to: str | None = None

    @model_validator(mode="after")
    def validate_pages(self) -> "ReadingUnit":
        if any(page < 1 for page in self.pages):
            raise ValueError("pages must contain positive page numbers")
        if len(set(self.pages)) != len(self.pages):
            raise ValueError("pages must not contain duplicates")
        if self.pages != sorted(self.pages):
            raise ValueError("pages must be sorted")
        if any(count < 0 for count in self.expected_elements.values()):
            raise ValueError("expected element counts must be non-negative")
        return self
