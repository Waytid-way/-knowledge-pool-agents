"""Create the initial frozen scoped persistence schema."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_scoped_persistence"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


class FrozenVector(sa.types.UserDefinedType[object]):
    """Frozen pgvector DDL type for this historical revision."""

    cache_ok = True

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def get_col_spec(self, **_: object) -> str:
        return f"VECTOR({self.dimensions})"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "tenants",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("tenant_id", name="pk_tenants"),
    )
    op.create_table(
        "projects",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("project_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.tenant_id"], name="fk_projects_tenant_id_tenants", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "project_id", name="pk_projects"),
    )
    op.create_table(
        "knowledge_pools",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("project_id", sa.String(length=128), nullable=True),
        sa.Column("visibility", sa.String(length=32), nullable=False),
        sa.Column("parent_pool_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("(scope = 'project' AND project_id IS NOT NULL) OR (scope <> 'project' AND (scope <> 'global' OR project_id IS NULL))", name="ck_knowledge_pools_scope_project_context"),
        sa.ForeignKeyConstraint(["tenant_id", "project_id"], ["projects.tenant_id", "projects.project_id"], name="fk_knowledge_pools_tenant_id_projects", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.tenant_id"], name="fk_knowledge_pools_tenant_id_tenants", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", name="pk_knowledge_pools"),
    )
    op.create_table(
        "agent_specs",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("agent_id", sa.String(length=128), nullable=False),
        sa.Column("agent_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("blueprint", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("permissions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id"], ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"], name="fk_agent_specs_tenant_id_knowledge_pools", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "agent_id", "agent_version", name="pk_agent_specs"),
        sa.UniqueConstraint("tenant_id", "pool_id", "agent_id", "agent_version", name="uq_agent_specs_tenant_id"),
    )
    op.create_table(
        "audit_events",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("event_id", sa.String(length=128), nullable=False),
        sa.Column("actor_type", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=128), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("previous_hash", sa.String(length=128), nullable=True),
        sa.Column("event_hash", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id"], ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"], name="fk_audit_events_tenant_id_knowledge_pools", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "event_id", name="pk_audit_events"),
    )
    op.create_table(
        "candidate_objects",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("object_id", sa.String(length=128), nullable=False),
        sa.Column("object_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("project_id", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sources", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id"], ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"], name="fk_candidate_objects_tenant_id_knowledge_pools", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "object_id", name="pk_candidate_objects"),
    )
    op.create_table(
        "documents",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("document_id", sa.String(length=128), nullable=False),
        sa.Column("project_id", sa.String(length=128), nullable=True),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("media_type", sa.String(length=128), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("storage_uri", sa.String(length=2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id"], ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"], name="fk_documents_tenant_id_knowledge_pools", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "document_id", name="pk_documents"),
        sa.UniqueConstraint("tenant_id", "pool_id", "content_hash", name="uq_documents_tenant_id"),
    )
    op.create_table(
        "knowledge_objects",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("object_id", sa.String(length=128), nullable=False),
        sa.Column("object_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("project_id", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sources", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("embedding", FrozenVector(1536), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id"], ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"], name="fk_knowledge_objects_tenant_id_knowledge_pools", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "object_id", name="pk_knowledge_objects"),
        sa.UniqueConstraint("tenant_id", "pool_id", "object_id", name="uq_knowledge_objects_tenant_id"),
    )
    op.create_table(
        "promotion_candidates",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("candidate_id", sa.String(length=128), nullable=False),
        sa.Column("source_object_id", sa.String(length=128), nullable=False),
        sa.Column("target_pool_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("justification", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id"], ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"], name="fk_promotion_candidates_source_pool", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id", "target_pool_id"], ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"], name="fk_promotion_candidates_target_pool"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "candidate_id", name="pk_promotion_candidates"),
    )
    op.create_table(
        "questions",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("question_id", sa.String(length=128), nullable=False),
        sa.Column("question_type", sa.String(length=64), nullable=False),
        sa.Column("question", sa.String(length=2048), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("project_id", sa.String(length=128), nullable=True),
        sa.Column("answer_object_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sources", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("answerability", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id"], ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"], name="fk_questions_tenant_id_knowledge_pools", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "question_id", name="pk_questions"),
    )
    op.create_table(
        "reasoning_traces",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("trace_id", sa.String(length=128), nullable=False),
        sa.Column("task_id", sa.String(length=128), nullable=False),
        sa.Column("agent_id", sa.String(length=128), nullable=False),
        sa.Column("agent_version", sa.String(length=64), nullable=False),
        sa.Column("reasoning_modes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("facts", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rules", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("hypotheses", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("decisions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("outcome", sa.String(length=2048), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id"], ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"], name="fk_reasoning_traces_tenant_id_knowledge_pools", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "trace_id", name="pk_reasoning_traces"),
    )
    op.create_table(
        "agent_evaluations",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("evaluation_id", sa.String(length=128), nullable=False),
        sa.Column("agent_id", sa.String(length=128), nullable=False),
        sa.Column("agent_version", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id", "agent_id", "agent_version"], ["agent_specs.tenant_id", "agent_specs.pool_id", "agent_specs.agent_id", "agent_specs.agent_version"], name="fk_agent_evaluations_tenant_id_agent_specs", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "evaluation_id", name="pk_agent_evaluations"),
    )
    op.create_table(
        "reading_units",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("unit_id", sa.String(length=128), nullable=False),
        sa.Column("document_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("pages", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("expected_elements", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("continuation_from", sa.String(length=128), nullable=True),
        sa.Column("continuation_to", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id", "document_id"], ["documents.tenant_id", "documents.pool_id", "documents.document_id"], name="fk_reading_units_tenant_id_documents", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "unit_id", name="pk_reading_units"),
        sa.UniqueConstraint("tenant_id", "pool_id", "document_id", "unit_id", name="uq_reading_units_tenant_id"),
    )
    op.create_table(
        "relationships",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("relationship_id", sa.String(length=128), nullable=False),
        sa.Column("source_object_id", sa.String(length=128), nullable=False),
        sa.Column("relationship_type", sa.String(length=64), nullable=False),
        sa.Column("target_object_id", sa.String(length=128), nullable=False),
        sa.Column("sources", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id", "source_object_id"], ["knowledge_objects.tenant_id", "knowledge_objects.pool_id", "knowledge_objects.object_id"], name="fk_relationships_source_object", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id", "target_object_id"], ["knowledge_objects.tenant_id", "knowledge_objects.pool_id", "knowledge_objects.object_id"], name="fk_relationships_target_object", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "relationship_id", name="pk_relationships"),
        sa.UniqueConstraint("tenant_id", "pool_id", "source_object_id", "relationship_type", "target_object_id", name="uq_relationships_tenant_id"),
    )
    op.create_table(
        "workflow_runs",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("run_id", sa.String(length=128), nullable=False),
        sa.Column("document_id", sa.String(length=128), nullable=False),
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id", "document_id"], ["documents.tenant_id", "documents.pool_id", "documents.document_id"], name="fk_workflow_runs_tenant_id_documents", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "run_id", name="pk_workflow_runs"),
        sa.UniqueConstraint("tenant_id", "pool_id", "run_id", name="uq_workflow_runs_tenant_id"),
    )
    op.create_table(
        "document_pages",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("document_id", sa.String(length=128), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("section_path", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reading_unit_id", sa.String(length=128), nullable=True),
        sa.Column("page_hash", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id", "document_id", "reading_unit_id"], ["reading_units.tenant_id", "reading_units.pool_id", "reading_units.document_id", "reading_units.unit_id"], name="fk_document_pages_reading_unit"),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id", "document_id"], ["documents.tenant_id", "documents.pool_id", "documents.document_id"], name="fk_document_pages_tenant_id_documents", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "document_id", "page_number", name="pk_document_pages"),
    )
    op.create_table(
        "workflow_events",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("event_id", sa.String(length=128), nullable=False),
        sa.Column("run_id", sa.String(length=128), nullable=False),
        sa.Column("from_state", sa.String(length=64), nullable=True),
        sa.Column("to_state", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.String(length=2048), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id", "run_id"], ["workflow_runs.tenant_id", "workflow_runs.pool_id", "workflow_runs.run_id"], name="fk_workflow_events_tenant_id_workflow_runs", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "event_id", name="pk_workflow_events"),
    )
    op.create_table(
        "page_elements",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("pool_id", sa.String(length=128), nullable=False),
        sa.Column("document_id", sa.String(length=128), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("element_id", sa.String(length=128), nullable=False),
        sa.Column("element_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=512), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id", "pool_id", "document_id", "page_number"], ["document_pages.tenant_id", "document_pages.pool_id", "document_pages.document_id", "document_pages.page_number"], name="fk_page_elements_tenant_id_document_pages", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "pool_id", "document_id", "page_number", "element_id", name="pk_page_elements"),
    )


def downgrade() -> None:
    op.drop_table("page_elements")
    op.drop_table("workflow_events")
    op.drop_table("document_pages")
    op.drop_table("workflow_runs")
    op.drop_table("relationships")
    op.drop_table("reading_units")
    op.drop_table("agent_evaluations")
    op.drop_table("reasoning_traces")
    op.drop_table("questions")
    op.drop_table("promotion_candidates")
    op.drop_table("knowledge_objects")
    op.drop_table("documents")
    op.drop_table("candidate_objects")
    op.drop_table("audit_events")
    op.drop_table("agent_specs")
    op.drop_table("knowledge_pools")
    op.drop_table("projects")
    op.drop_table("tenants")
