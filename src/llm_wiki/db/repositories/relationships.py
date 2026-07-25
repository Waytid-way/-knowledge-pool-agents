"""Scoped knowledge-graph relationship persistence."""

from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_wiki.db.models import RelationshipRow


class RelationshipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        tenant_id: str,
        pool_id: str,
        relationship_id: str,
        source_object_id: str,
        relationship_type: str,
        target_object_id: str,
        sources: list[dict[str, Any]],
        confidence: float,
        schema_version: str = "1.0",
    ) -> RelationshipRow:
        row = RelationshipRow(
            tenant_id=tenant_id,
            pool_id=pool_id,
            relationship_id=relationship_id,
            source_object_id=source_object_id,
            relationship_type=relationship_type,
            target_object_id=target_object_id,
            sources=sources,
            confidence=confidence,
            schema_version=schema_version,
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def list_for_object(
        self, *, tenant_id: str, pool_id: str, object_id: str
    ) -> list[RelationshipRow]:
        statement = (
            select(RelationshipRow)
            .where(
                RelationshipRow.tenant_id == tenant_id,
                RelationshipRow.pool_id == pool_id,
                or_(
                    RelationshipRow.source_object_id == object_id,
                    RelationshipRow.target_object_id == object_id,
                ),
            )
            .order_by(RelationshipRow.relationship_id)
        )
        return list((await self._session.scalars(statement)).all())
