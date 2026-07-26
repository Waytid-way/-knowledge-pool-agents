"""Enforce cross-pool and reading-unit scope integrity."""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_scope_integrity"
down_revision: str | None = "0001_scoped_persistence"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_reading_units_document_unit",
        "reading_units",
        ["tenant_id", "pool_id", "document_id", "unit_id"],
    )
    op.create_foreign_key(
        "fk_document_pages_reading_unit",
        "document_pages",
        "reading_units",
        ["tenant_id", "pool_id", "document_id", "reading_unit_id"],
        ["tenant_id", "pool_id", "document_id", "unit_id"],
    )
    op.create_foreign_key(
        "fk_promotion_candidates_target_pool",
        "promotion_candidates",
        "knowledge_pools",
        ["tenant_id", "target_pool_id"],
        ["tenant_id", "pool_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_promotion_candidates_target_pool",
        "promotion_candidates",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_document_pages_reading_unit",
        "document_pages",
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_reading_units_document_unit",
        "reading_units",
        type_="unique",
    )
