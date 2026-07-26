from __future__ import annotations

import inspect
from typing import Any

import pytest
from sqlalchemy.dialects import postgresql

from llm_wiki.db.repositories.knowledge import KnowledgeObjectRepository


class CapturingSession:
    def __init__(self) -> None:
        self.statement: Any | None = None

    async def scalar(self, statement: Any) -> None:
        self.statement = statement
        return None


@pytest.mark.asyncio
async def test_knowledge_get_always_filters_tenant_and_pool() -> None:
    session = CapturingSession()
    repository = KnowledgeObjectRepository(session)  # type: ignore[arg-type]

    result = await repository.get(
        tenant_id="tenant-a",
        pool_id="project-alpha",
        object_id="object-1",
    )

    assert result is None
    assert session.statement is not None
    compiled = session.statement.compile(dialect=postgresql.dialect())
    sql = str(compiled)
    assert "knowledge_objects.tenant_id" in sql
    assert "knowledge_objects.pool_id" in sql
    assert "knowledge_objects.object_id" in sql
    assert set(compiled.params.values()) == {"tenant-a", "project-alpha", "object-1"}


def test_repository_get_cannot_be_called_without_scope_context() -> None:
    signature = inspect.signature(KnowledgeObjectRepository.get)
    parameters = signature.parameters

    assert parameters["tenant_id"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["pool_id"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["object_id"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["tenant_id"].default is inspect.Parameter.empty
    assert parameters["pool_id"].default is inspect.Parameter.empty


def test_metadata_contains_all_planned_persistence_tables() -> None:
    from llm_wiki.db import models as _models  # noqa: F401
    from llm_wiki.db.base import Base

    expected = {
        "tenants",
        "projects",
        "knowledge_pools",
        "documents",
        "document_pages",
        "page_elements",
        "reading_units",
        "candidate_objects",
        "knowledge_objects",
        "relationships",
        "questions",
        "reasoning_traces",
        "workflow_runs",
        "workflow_events",
        "agent_specs",
        "agent_evaluations",
        "promotion_candidates",
        "audit_events",
    }

    assert expected == set(Base.metadata.tables)


def test_scoped_tables_always_include_tenant_and_pool_columns() -> None:
    from llm_wiki.db import models as _models  # noqa: F401
    from llm_wiki.db.base import Base

    unscoped = {"tenants", "projects"}
    for table_name, table in Base.metadata.tables.items():
        if table_name in unscoped:
            continue
        assert "tenant_id" in table.c, table_name
        assert "pool_id" in table.c, table_name


def test_unique_constraints_never_drop_tenant_context() -> None:
    from sqlalchemy import UniqueConstraint

    from llm_wiki.db import models as _models  # noqa: F401
    from llm_wiki.db.base import Base

    for table in Base.metadata.tables.values():
        for constraint in table.constraints:
            if isinstance(constraint, UniqueConstraint):
                assert "tenant_id" in {column.name for column in constraint.columns}, table.name


def test_all_repository_write_methods_require_tenant_and_pool_context() -> None:
    from llm_wiki.db.repositories import (
        AuditRepository,
        DocumentRepository,
        KnowledgeObjectRepository,
        KnowledgePoolRepository,
        RelationshipRepository,
        WorkflowRunRepository,
    )

    write_methods = [
        AuditRepository.append,
        DocumentRepository.add,
        KnowledgeObjectRepository.add,
        KnowledgePoolRepository.add,
        RelationshipRepository.add,
        WorkflowRunRepository.add,
        WorkflowRunRepository.transition,
    ]

    for method in write_methods:
        parameters = inspect.signature(method).parameters
        for name in ("tenant_id", "pool_id"):
            parameter = parameters[name]
            assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, method.__qualname__
            assert parameter.default is inspect.Parameter.empty, method.__qualname__


def test_relationship_foreign_keys_target_canonical_object_table() -> None:
    from llm_wiki.db import models as _models  # noqa: F401
    from llm_wiki.db.base import Base

    table = Base.metadata.tables["relationships"]
    targets = {
        element.target_fullname
        for constraint in table.foreign_key_constraints
        for element in constraint.elements
    }

    assert targets == {
        "knowledge_objects.tenant_id",
        "knowledge_objects.pool_id",
        "knowledge_objects.object_id",
    }
