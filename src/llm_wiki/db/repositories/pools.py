"""Scoped Knowledge Pool persistence."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_wiki.db.models import KnowledgePoolRow


class KnowledgePoolRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        tenant_id: str,
        pool_id: str,
        name: str,
        scope: str,
        project_id: str | None,
        visibility: str,
        parent_pool_ids: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> KnowledgePoolRow:
        row = KnowledgePoolRow(
            tenant_id=tenant_id,
            pool_id=pool_id,
            name=name,
            scope=scope,
            project_id=project_id,
            visibility=visibility,
            parent_pool_ids=parent_pool_ids,
            metadata_payload=metadata or {},
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def get(self, *, tenant_id: str, pool_id: str) -> KnowledgePoolRow | None:
        statement = select(KnowledgePoolRow).where(
            KnowledgePoolRow.tenant_id == tenant_id,
            KnowledgePoolRow.pool_id == pool_id,
        )
        return await self._session.scalar(statement)
