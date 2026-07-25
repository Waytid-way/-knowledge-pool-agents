"""Scoped durable-workflow persistence with optimistic versioning."""

from __future__ import annotations

from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_wiki.db.models import WorkflowRunRow


class WorkflowRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        tenant_id: str,
        pool_id: str,
        run_id: str,
        document_id: str,
        state: str,
        attempt: int = 1,
        payload: dict[str, Any] | None = None,
    ) -> WorkflowRunRow:
        row = WorkflowRunRow(
            tenant_id=tenant_id,
            pool_id=pool_id,
            run_id=run_id,
            document_id=document_id,
            state=state,
            attempt=attempt,
            version=1,
            payload=payload or {},
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def get(self, *, tenant_id: str, pool_id: str, run_id: str) -> WorkflowRunRow | None:
        statement = select(WorkflowRunRow).where(
            WorkflowRunRow.tenant_id == tenant_id,
            WorkflowRunRow.pool_id == pool_id,
            WorkflowRunRow.run_id == run_id,
        )
        return cast(WorkflowRunRow | None, await self._session.scalar(statement))

    async def transition(
        self,
        *,
        tenant_id: str,
        pool_id: str,
        run_id: str,
        expected_version: int,
        state: str,
    ) -> WorkflowRunRow | None:
        statement = (
            select(WorkflowRunRow)
            .where(
                WorkflowRunRow.tenant_id == tenant_id,
                WorkflowRunRow.pool_id == pool_id,
                WorkflowRunRow.run_id == run_id,
                WorkflowRunRow.version == expected_version,
            )
            .with_for_update()
        )
        row = await self._session.scalar(statement)
        if row is None:
            return None
        row.state = state
        row.version += 1
        await self._session.flush()
        return row
