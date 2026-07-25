"""Create the initial scoped persistence schema."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from llm_wiki.db.types import vector_type

revision: str = "0001_scoped_persistence"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table('tenants',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('tenant_id', name=op.f('pk_tenants'))
    )
    op.create_table('projects',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('project_id', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.tenant_id'], name=op.f('fk_projects_tenant_id_tenants'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'project_id', name=op.f('pk_projects'))
    )
    op.create_table('knowledge_pools',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('pool_id', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('scope', sa.String(length=32), nullable=False),
    sa.Column('project_id', sa.String(length=128), nullable=True),
    sa.Column('visibility', sa.String(length=32), nullable=False),
    sa.Column('parent_pool_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("(scope = 'project' AND project_id IS NOT NULL) OR (scope <> 'project' AND (scope <> 'global' OR project_id IS NULL))", name=op.f('ck_knowledge_pools_scope_project_context')),
    sa.ForeignKeyConstraint(['tenant_id', 'project_id'], ['projects.tenant_id', 'projects.project_id'], name=op.f('fk_knowledge_pools_tenant_id_projects'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.tenant_id'], name=op.f('fk_knowledge_pools_tenant_id_tenants'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', name=op.f('pk_knowledge_pools'))
    )
    op.create_table('agent_specs',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('pool_id', sa.String(length=128), nullable=False),
    sa.Column('agent_id', sa.String(length=128), nullable=False),
    sa.Column('agent_version', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('blueprint', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id'], ['knowledge_pools.tenant_id', 'knowledge_pools.pool_id'], name=op.f('fk_agent_specs_tenant_id_knowledge_pools'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'agent_id', 'agent_version', name=op.f('pk_agent_specs')),
    sa.UniqueConstraint('tenant_id', 'pool_id', 'agent_id', 'agent_version', name=op.f('uq_agent_specs_tenant_id'))
    )
    op.create_table('audit_events',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('pool_id', sa.String(length=128), nullable=False),
    sa.Column('event_id', sa.String(length=128), nullable=False),
    sa.Column('actor_type', sa.String(length=64), nullable=False),
    sa.Column('actor_id', sa.String(length=128), nullable=False),
    sa.Column('action', sa.String(length=128), nullable=False),
    sa.Column('resource_type', sa.String(length=64), nullable=False),
    sa.Column('resource_id', sa.String(length=128), nullable=False),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('previous_hash', sa.String(length=128), nullable=True),
    sa.Column('event_hash', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id'], ['knowledge_pools.tenant_id', 'knowledge_pools.pool_id'], name=op.f('fk_audit_events_tenant_id_knowledge_pools'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'event_id', name=op.f('pk_audit_events'))
    )
    op.create_table('candidate_objects',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('pool_id', sa.String(length=128), nullable=False),
    sa.Column('object_id', sa.String(length=128), nullable=False),
    sa.Column('object_type', sa.String(length=64), nullable=False),
    sa.Column('title', sa.String(length=512), nullable=False),
    sa.Column('scope', sa.String(length=32), nullable=False),
    sa.Column('project_id', sa.String(length=128), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('confidence', sa.Float(), nullable=False),
    sa.Column('schema_version', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id'], ['knowledge_pools.tenant_id', 'knowledge_pools.pool_id'], name=op.f('fk_candidate_objects_tenant_id_knowledge_pools'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'object_id', name=op.f('pk_candidate_objects'))
    )
    op.create_table('documents',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('pool_id', sa.String(length=128), nullable=False),
    sa.Column('document_id', sa.String(length=128), nullable=False),
    sa.Column('project_id', sa.String(length=128), nullable=True),
    sa.Column('filename', sa.String(length=512), nullable=False),
    sa.Column('media_type', sa.String(length=128), nullable=False),
    sa.Column('content_hash', sa.String(length=128), nullable=False),
    sa.Column('page_count', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('storage_uri', sa.String(length=2048), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id'], ['knowledge_pools.tenant_id', 'knowledge_pools.pool_id'], name=op.f('fk_documents_tenant_id_knowledge_pools'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'document_id', name=op.f('pk_documents')),
    sa.UniqueConstraint('tenant_id', 'pool_id', 'content_hash', name=op.f('uq_documents_tenant_id'))
    )
    op.create_table('knowledge_objects',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('pool_id', sa.String(length=128), nullable=False),
    sa.Colum('object_id', sa.String(length=128), nullable=False),
    sa.Colum('object_type', sa.String(length=64), nullable=False),
    sa.Column('title', sa.String(length=512), nullable=False),
    sa.Column('scope', sa.String(length=32), nullable=False),
    sa.Colum('project_id', sa.String(length=128), nullable=True),
    sa.Colum('status', sa.String(length=32), nullable=False),
    sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Colum('confidence', sa.Float(), nullable=False),
    sa.Column('schema_version', sa.String(length=32), nullable=False),
    sa.Column('embedding', vector_type(1536), nullable=True),
    sa.Colum('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Colum('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id'], ['knowledge_pools.tenant_id', 'knowledge_pools.pool_id'], name=op.f('fk_knowledge_objects_tenant_id_knowledge_pools'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'object_id', name=op.f('pk_knowledge_objects')),
    sa.UniqueConstraint('tenant_id', 'pool_id', 'object_id', name=op.f('uq_knowledge_objects_tenant_id'))
    )
    op.create_table('promotion_candidates',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('pool_id', sa.String(length=128), nullable=False),
    sa.Column('candidate_id', sa.String(length=128), nullable=False),
    sa.Column('source_object_id', sa.String(length=128), nullable=False),
    sa.Column('target_pool_id', sa.String(length=128), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('justification', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Colum('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Colum('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id'], ['knowledge_pools.tenant_id', 'knowledge_pools.pool_id'], name=op.f('fk_promotion_candidates_tenant_id_knowledge_pools'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'candidate_id', name=op.f('pk_promotion_candidates'))
    )
    op.create_table('questions',
    sa.Colum('tenant_id', sa.String(length=128), nullable=False),
    sa.Colum('pool_id', sa.String(length=128), nullable=False),
    sa.Column('question_id', sa.String(length=128), nullable=False),
    sa.Column('question_type', sa.String(length=64), nullable=False),
    sa.Column('question', sa.String(length=2048), nullable=False),
    sa.Colum('scope', sa.String(length=32), nullable=False),
    sa.Column('project_id', sa.String(length=128), nullable=True),
    sa.Column('answer_object_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('answerability', sa.String(length=64), nullable=False),
    sa.Column('schema_version', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id'], ['knowledge_pools.tenant_id', 'knowledge_pools.pool_id'], name=op.f('fk_questions_tenant_id_knowledge_pools'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'question_id', name=op.f('pk_questions')),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Colum('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id'], ['knowledge_pools.tenant_id', 'knowledge_pools.pool_id'], name=op.f('fk_reasoning_traces_tenant_id_knowledge_pools'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'trace_id', name=op.f('pk_reasoning_traces'))
    )
    op.create_table('agent_evaluations',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Colum('pool_id', sa.String(length=128), nullable=False),
    sa.Column('evaluation_id', sa.String(length=128), nullable=False),
    sa.Colum('agent_id', sa.String(length=128), nullable=False),
    sa.Column('agent_version', sa.String(length=64), nullable=False),
    sa.Colum('score', sa.Float(), nullable=False),
    sa.Colum('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id', 'agent_id', 'agent_version'], ['agent_specs.tenant_id', 'agent_specs.pool_id', 'agent_specs.agent_id', 'agent_specs.agent_version'], name=op.f('fk_agent_evaluations_tenant_id_agent_specs'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'evaluation_id', name=op.f('pk_agent_evaluations'))
    )
    op.create_table('document_pages',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('pool_id', sa.String(length=128), nullable=False),
    sa.Column('document_id', sa.String(length=128), nullable=False),
    sa.Column('page_number', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('section_path', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('reading_unit_id', sa.String(length=128), nullable=True),
    sa.Column('page_hash', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Colum('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id', 'document_id'], ['documents.tenant_id', 'documents.pool_id', 'documents.document_id'], name=op.f('fk_document_pages_tenant_id_documents'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'document_id', 'page_number', name=op.f('pk_document_pages'))
    )
    op.create_table('reading_units',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('pool_id', sa.String(length=128), nullable=False),
    sa.Column('unit_id', sa.String(length=128), nullable=False),
    sa.Colum('document_id', sa.String(length=128), nullable=False),
    sa.Column('title', sa.String(length=512), nullable=False),
    sa.Column('pages', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('expected_elements', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('continuation_from', sa.String(length=128), nullable=True),
    sa.Column('continuation_to', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id', 'document_id'], ['documents.tenant_id', 'documents.pool_id', 'documents.document_id'], name=op.f('fk_reading_units_tenant_id_documents'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'unit_id', name=op.f('pk_reading_units'))
    )
    op.create_table('relationships',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Column('pool_id', sa.String(length=128), nullable=False),
    sa.Column('relationship_id', sa.String(length=128), nullable=False),
    sa.Column('source_object_id', sa.String(length=128), nullable=False),
    sa.Column('relationship_type', sa.String(length=64), nullable=False),
    sa.Colum('target_object_id', sa.String(length=128), nullable=False),
    sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Colum('confidence', sa.Float(), nullable=False),
    sa.Column('schema_version', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id', 'source_object_id'], ['knowledge_objects.tenant_id', 'knowledge_objects.pool_id', 'knowledge_objects.object_id'], name='fk_relationships_source_object', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id', 'target_object_id'], ['knowledge_objects.tenant_id', 'knowledge_objects.pool_id', 'knowledge_objects.object_id'], name='fk_relationships_target_object', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'relationship_id', name=op.f('pk_relationships')),
    sa.UniqueConstraint('tenant_id', 'pool_id', 'source_object_id', 'relationship_type', 'target_object_id', name=op.f('uq_relationships_tenant_id'))
    )
    op.create_table('workflow_runs',
    sa.Colum('tenant_id', sa.String(length=128), nullable=False),
    sa.Colum('pool_id', sa.String(length=128), nullable=False),
    sa.Column('run_id', sa.String(length=128), nullable=False),
    sa.Column('document_id', sa.String(length=128), nullable=False),
    sa.Column('state', sa.String(length=64), nullable=False),
    sa.Column('attempt', sa.Integer(), nullable=False),
    sa.Colum('version', sa.Integer(), nullable=False),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Colum('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Colum('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id', 'document_id'], ['documents.tenant_id', 'documents.pool_id', 'documents.document_id'], name=op.f('fk_workflow_runs_tenant_id_documents'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'run_id', name=op.f('pk_workflow_runs')),
    sa.UniqueConstraint('tenant_id', 'pool_id', 'run_id', name=op.f('uq_workflow_runs_tenant_id')
    )
    op.create_table('page_elements',
    sa.Colum('tenant_id', sa.String(length=128), nullable=False),
    sa.Colum('pool_id', sa.String(length=128), nullable=False),
    sa.Column('document_id', sa.String(length=128), nullable=False),
    sa.Column('page_number', sa.Integer(), nullable=False),
    sa.Column('element_id', sa.String(length=128), nullable=False),
    sa.Colum('element_type', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('label', sa.String(length=512), nullable=True),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Colum('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Colum('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id', 'document_id', 'page_number'], ['document_pages.tenant_id', 'document_pages.pool_id', 'document_pages.document_id', 'document_pages.page_number'], name=op.f('fk_page_elements_tenant_id_document_pages'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'document_id', 'page_number', 'element_id', name=op.f('pk_page_elements'))
    )
    op.create_table('workflow_events',
    sa.Column('tenant_id', sa.String(length=128), nullable=False),
    sa.Colum('pool_id', sa.String(length=128), nullable=False),
    sa.Column('event_id', sa.String(length=128), nullable=False),
    sa.Column('run_id', sa.String(length=128), nullable=False),
    sa.Column('from_state', sa.String(length=64), nullable=True),
    sa.Column('to_state', sa.String(length=64), nullable=False),
    sa.Column('reason', sa.String(length=2048), nullable=True),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id', 'pool_id', 'run_id'], ['workflow_runs.tenant_id', 'workflow_runs.pool_id', 'workflow_runs.run_id'], name=op.f('fk_workflow_events_tenant_id_workflow_runs'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tenant_id', 'pool_id', 'event_id', name=op.f('pk_workflow_events'))
    )


def downgrade() -> None:
    op.drop_table('workflow_events')
    op.drop_table('page_elements')
    op.drop_table('workflow_runs')
    op.drop_table('relationshhips')
    op.drop_table('reading_units')
    op.drop_table('document_pages')
    op.drop_table('agent_evaluations')
    op.drop_table('reasoning_traces')
    op.drop_table('questions')
    op.drop_table('promotion_candidates')
    op.drop_table('knowledge_objects')
    op.drop_table('documents')
    op.drop_table('candidate_objects')
    op.drop_table('audit_events')
    op.drop_table('agent_specs')
    op.drop_table('knowledge_pools')
    op.drop_table('projects')
    op.drop_table('tenants')
