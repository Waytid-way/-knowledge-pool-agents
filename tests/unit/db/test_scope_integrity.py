from pathlib import Path

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint

from llm_wiki.db import models as _models  # noqa: F401
from llm_wiki.db.base import Base


def _foreign_key(table_name: str, constraint_name: str) -> ForeignKeyConstraint:
    table = Base.metadata.tables[table_name]
    for constraint in table.constraints:
        if isinstance(constraint, ForeignKeyConstraint) and constraint.name == constraint_name:
            return constraint
    raise AssertionError(f"missing foreign key {constraint_name}")


def test_promotion_target_pool_is_tenant_scoped() -> None:
    constraint = _foreign_key(
        "promotion_candidates",
        "fk_promotion_candidates_target_pool",
    )
    assert [column.name for column in constraint.columns] == ["tenant_id", "target_pool_id"]
    assert [element.target_fullname for element in constraint.elements] == [
        "knowledge_pools.tenant_id",
        "knowledge_pools.pool_id",
    ]


def test_page_reading_unit_reference_preserves_document_scope() -> None:
    constraint = _foreign_key("document_pages", "fk_document_pages_reading_unit")
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


def test_reading_unit_target_columns_are_unique() -> None:
    table = Base.metadata.tables["reading_units"]
    unique_columns = {
        tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("tenant_id", "pool_id", "document_id", "unit_id") in unique_columns


def test_initial_migration_is_frozen_and_model_independent() -> None:
    migration = Path("alembic/versions/0001_scoped_persistence.py").read_text()
    assert "_FROZEN_DDL" in migration
    assert "Base.metadata" not in migration
    assert "llm_wiki.db.models" not in migration
