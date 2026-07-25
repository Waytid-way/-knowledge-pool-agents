from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from llm_wiki.db.models import (
    DocumentPageRow,
    DocumentRow,
    KnowledgeObjectRow,
    KnowledgePoolRow,
    ProjectRow,
    PromotionCandidateRow,
    ReadingUnitRow,
    TenantRow,
)
from llm_wiki.db.repositories.knowledge import KnowledgeObjectRepository
from llm_wiki.db.repositories.workflows import WorkflowRunRepository

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def database_url() -> str:
    value = os.getenv("LLM_WIKI_TEST_DATABASE_URL")
    if not value:
        pytest.skip("LLM_WIKI_TEST_DATABASE_URL is required for PostgreSQL integration tests")
    return value


@pytest.fixture(scope="module", autouse=True)
def migrated_database(database_url: str) -> Iterator[None]:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")
    yield
    command.downgrade(config, "base")


@pytest_asyncio.fixture
async def db_session(database_url: str) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(database_url)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        async with factory() as session:
            yield session
        await transaction.rollback()
    await engine.dispose()


async def seed_scope(session: AsyncSession) -> None:
    session.add_all(
        [
            TenantRow(tenant_id="tenant-a", name="Tenant A"),
            TenantRow(tenant_id="tenant-b", name="Tenant B"),
        ]
    )
    await session.flush()

    session.add_all(
        [
            ProjectRow(tenant_id="tenant-a", project_id="alpha", name="Alpha"),
            ProjectRow(tenant_id="tenant-b", project_id="alpha", name="Alpha"),
        ]
    )
    await session.flush()

    session.add_all(
        [
            KnowledgePoolRow(
                tenant_id="tenant-a",
                pool_id="project-alpha",
                name="Project Alpha",
                scope="project",
                project_id="alpha",
                visibility="private",
                parent_pool_ids=[],
            ),
            KnowledgePoolRow(
                tenant_id="tenant-b",
                pool_id="project-alpha",
                name="Different Tenant Alpha",
                scope="project",
                project_id="alpha",
                visibility="private",
                parent_pool_ids=[],
            ),
        ]
    )
    await session.flush()


@pytest.mark.asyncio
async def test_repository_never_returns_another_tenant_object(db_session: AsyncSession) -> None:
    await seed_scope(db_session)
    repository = KnowledgeObjectRepository(db_session)
    await repository.add(
        tenant_id="tenant-b",
        pool_id="project-alpha",
        object_id="shared-id",
        object_type="concept",
        title="Tenant B object",
        scope="project",
        project_id="alpha",
        status="explicit",
        content={"value": "secret"},
        sources=[{"document_id": "doc-b", "pages": [1], "element_ids": []}],
        confidence=1.0,
    )

    result = await repository.get(
        tenant_id="tenant-a",
        pool_id="project-alpha",
        object_id="shared-id",
    )

    assert result is None


@pytest.mark.asyncio
async def test_same_object_id_is_isolated_by_tenant(db_session: AsyncSession) -> None:
    await seed_scope(db_session)
    repository = KnowledgeObjectRepository(db_session)

    for tenant_id, title in [("tenant-a", "A"), ("tenant-b", "B")]:
        await repository.add(
            tenant_id=tenant_id,
            pool_id="project-alpha",
            object_id="same-object",
            object_type="concept",
            title=title,
            scope="project",
            project_id="alpha",
            status="explicit",
            content={"tenant": tenant_id},
            sources=[{"document_id": f"doc-{tenant_id}", "pages": [1], "element_ids": []}],
            confidence=1.0,
        )

    rows = (await db_session.scalars(select(KnowledgeObjectRow))).all()
    assert {(row.tenant_id, row.object_id) for row in rows} == {
        ("tenant-a", "same-object"),
        ("tenant-b", "same-object"),
    }


@pytest.mark.asyncio
async def test_workflow_transition_uses_optimistic_version(db_session: AsyncSession) -> None:
    await seed_scope(db_session)
    db_session.add(
        DocumentRow(
            tenant_id="tenant-a",
            pool_id="project-alpha",
            document_id="doc-a",
            project_id="alpha",
            filename="doc.pdf",
            media_type="application/pdf",
            content_hash="hash-a",
            page_count=1,
            status="registered",
        )
    )
    await db_session.flush()
    repository = WorkflowRunRepository(db_session)
    await repository.add(
        tenant_id="tenant-a",
        pool_id="project-alpha",
        run_id="run-a",
        document_id="doc-a",
        state="document_registered",
    )

    updated = await repository.transition(
        tenant_id="tenant-a",
        pool_id="project-alpha",
        run_id="run-a",
        expected_version=1,
        state="profiled",
    )
    stale = await repository.transition(
        tenant_id="tenant-a",
        pool_id="project-alpha",
        run_id="run-a",
        expected_version=1,
        state="failed",
    )

    assert updated is not None
    assert updated.version == 2
    assert updated.state == "profiled"
    assert stale is None


@pytest.mark.asyncio
async def test_promotion_target_pool_must_exist_in_same_tenant(
    db_session: AsyncSession,
) -> None:
    await seed_scope(db_session)
    db_session.add(
        PromotionCandidateRow(
            tenant_id="tenant-a",
            pool_id="project-alpha",
            candidate_id="promotion-a",
            source_object_id="object-a",
            target_pool_id="missing-pool",
            status="candidate",
            justification={},
        )
    )

    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_page_cannot_reference_reading_unit_from_another_document(
    db_session: AsyncSession,
) -> None:
    await seed_scope(db_session)
    db_session.add_all(
        [
            DocumentRow(
                tenant_id="tenant-a",
                pool_id="project-alpha",
                document_id="doc-a",
                project_id="alpha",
                filename="a.pdf",
                media_type="application/pdf",
                content_hash="hash-a",
                page_count=1,
                status="registered",
            ),
            DocumentRow(
                tenant_id="tenant-a",
                pool_id="project-alpha",
                document_id="doc-b",
                project_id="alpha",
                filename="b.pdf",
                media_type="application/pdf",
                content_hash="hash-b",
                page_count=1,
                status="registered",
            ),
        ]
    )
    await db_session.flush()
    db_session.add(
        ReadingUnitRow(
            tenant_id="tenant-a",
            pool_id="project-alpha",
            unit_id="unit-b",
            document_id="doc-b",
            title="B unit",
            pages=[1],
            expected_elements={},
        )
    )
    await db_session.flush()
    db_session.add(
        DocumentPageRow(
            tenant_id="tenant-a",
            pool_id="project-alpha",
            document_id="doc-a",
            page_number=1,
            status="discovered",
            section_path=[],
            reading_unit_id="unit-b",
        )
    )

    with pytest.raises(IntegrityError):
        await db_session.flush()
