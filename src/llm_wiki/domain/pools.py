from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import PoolScope


class KnowledgePool(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    pool_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    scope: PoolScope
    project_id: str | None = None
    parent_pool_ids: list[str] = Field(default_factory=list)
    visibility: str = "private"

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if self.scope is PoolScope.PROJECT and not self.project_id:
            raise ValueError("project_id is required for project scope")
        if self.scope is PoolScope.GLOBAL and self.project_id is not None:
            raise ValueError("project_id is not allowed for global scope")
        if self.pool_id in self.parent_pool_ids:
            raise ValueError("a pool cannot inherit from itself")
        if len(set(self.parent_pool_ids)) != len(self.parent_pool_ids):
            raise ValueError("parent_pool_ids must not contain duplicates")
        return self
