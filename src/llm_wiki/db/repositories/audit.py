"""Append-only scoped audit persistence."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_wiki.db.models import AuditEventRow


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def append(
        self,
        *,
        tenant_id: str,
        pool_id: str,
        event_id: str,
        actor_type: str,
        actor_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any],
        previous_hash: str | None,
        event_hash: str,
    ) -> AuditEventRow:
        row = AuditEventRow(
            tenant_id=tenant_id,
            pool_id=pool_id,
            event_id=event_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            previous_hash=previous_hash,
            event_hash=event_hash,
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def list_for_resource(
        self,
        *,
        tenant_id: str,
        pool_id: str,
        resource_type: str,
        resource_id: str,
    ) -> list[AuditEventRow]:
        statement = (
            select(AuditEventRow)
            .where(
                AuditEventRow.tenant_id == tenant_id,
                AuditEventRow.pool_id == pool_id,
                AuditEventRow.resource_type == resource_type,
                AuditEventRow.resource_id == resource_id,
            )
            .order_by(AuditEventRow.created_at, AuditEventRow.event_id)
        )
        return list((await self._session.scalars(statement)).all())
