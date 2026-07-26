"""Create the initial frozen scoped persistence schema."""

from collections.abc import Sequence

import base64
import zlib

import sqlalchemy as sa
from alembic import op

revision: str = "0001_scoped_persistence"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_FROZEN_DDL = "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"

TABLES = (
    "tenants",
    "projects",
    "knowledge_pools",
    "agent_specs",
    "audit_events",
    "candidate_objects",
    "documents",
    "knowledge_objects",
    "promotion_candidates",
    "questions",
    "reasoning_traces",
    "agent_evaluations",
    "reading_units",
    "relationships",
    "workflow_runs",
    "document_pages",
    "workflow_events",
    "page_elements",
)


def _ddl_statements() -> tuple[str, ...]:
    payload = zlib.decompress(base64.b64decode(_FROZEN_DDL)).decode()
    return tuple(payload.split("\0"))


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    for statement in _ddl_statements():
        op.execute(sa.text(statement))


def downgrade() -> None:
    for table_name in reversed(TABLES):
        op.drop_table(table_name)
