from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import UniqueConstraint
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


def test_initial_migration_is_frozen_and_does_not_use_live_metadata() -> None:
    migration = Path("alembic/versions/0001_scoped_persistence.py").read_text()

    assert "Base.metadata" not in migration
    assert "create_all" not in migration
    assert "drop_all" not in migration
    assert migration.count("op.create_table(") == 18
    assert migration.count("op.drop_table(") == 18


def test_promotion_target_pool_is_tenant_scoped() -> None:
    from llm_wiki.db import models as _models  # noqa: F401
    from llm_wiki.db.base import Base

    table = Base.metadata.tables["promotion_candidates"]
    constraints = {constraint.name: constraint for constraint in table.foreign_key_constraints}
    target = constraints["fk_promotion_candidates_target_pool"]

    assert [column.name for column in target.columns] == ["tenant_id", "target_pool_id"]
    assert [element.target_fullname for element in target.elements] == [
        "knowledge_pools.tenant_id",
        "knowledge_pools.pool_id",
    ]


def test_document_page_reading_unit_reference_preserves_document_scope() -> None:
    from llm_wiki.db import models as _models  # noqa: F401
    from llm_wiki.db.base import Base

    pages = Base.metadata.tables["document_pages"]
    constraint = next(
        item
        for item in pages.foreign_key_constraints
        if item.name == "fk_document_pages_reading_unit"
    )
    assert [column.name for column in constraint.columns] == [
        "tenant_id",
        "pool_id",
        "document_id",
        "reading_unit_id",
    ]
    assert [element.target_fullname for element in constraint.elements] == [
        "reading_units.tenant_id",
        "reading_units.pool_id",
        "reading_units.document_id",
        "reading_units.unit_id",
    ]

    reading_units = Base.metadata.tables["reading_units"]
    unique_columns = {
        tuple(column.name for column in item.columns)
        for item in reading_units.constraints
        if isinstance(item, UniqueConstraint)
    }
    assert ("tenant_id", "pool_id", "document_id", "unit_id") in unique_columns
