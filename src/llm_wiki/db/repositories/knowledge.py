"""Scoped canonical Knowledge Object persistence."""

from __future__ import annotations

from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_wiki.db.models import KnowledgeObjectRow


class KnowledgeObjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        tenant_id: str,
        pool_id: str,
        object_id: str,
        object_type: str,
        title: str,
        scope: str,
        project_id: str | None,
        status: str,
        content: dict[str, Any],
        sources: list[dict[str, Any]],
        confidence: float,
        schema_version: str = "1.0",
        embedding: list[float] | None = None,
    ) -> KnowledgeObjectRow:
        row = KnowledgeObjectRow(
            tenant_id=tenant_id,
            pool_id=pool_id,
            object_id=object_id,
            object_type=object_type,
            title=title,
            scope=scope,
            project_id=project_id,
            status=status,
            content=content,
            sources=sources,
            confidence=confidence,
            schema_version=schema_version,
            embedding=embedding,
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def get(
        self,
        *,
        tenant_id: str,
        pool_id: str,
        object_id: str,
    ) -> KnowledgeObjectRow | None:
        statement = select(KnowledgeObjectRow).where(
            KnowledgeObjectRow.tenant_id == tenant_id,
            KnowledgeObjectRow.pool_id == pool_id,
            KnowledgeObjectRow.object_id == object_id,
        )
        return cast(KnowledgeObjectRow | None, await self._session.scalar(statement))

    async def list_by_pool(self, *, tenant_id: str, pool_id: str) -> list[KnowledgeObjectRow]:
        statement = (
            select(KnowledgeObjectRow)
            .where(
                KnowledgeObjectRow.tenant_id == tenant_id,
                KnowledgeObjectRow.pool_id == pool_id,
            )
            .order_by(KnowledgeObjectRow.object_id)
        )
        return list((await self._session.scalars(statement)).all())
