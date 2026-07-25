"""Scoped source-document persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_wiki.db.models import DocumentRow


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        tenant_id: str,
        pool_id: str,
        document_id: str,
        project_id: str | None,
        filename: str,
        media_type: str,
        content_hash: str,
        page_count: int,
        status: str,
        storage_uri: str | None = None,
    ) -> DocumentRow:
        row = DocumentRow(
            tenant_id=tenant_id,
            pool_id=pool_id,
            document_id=document_id,
            project_id=project_id,
            filename=filename,
            media_type=media_type,
            content_hash=content_hash,
            page_count=page_count,
            status=status,
            storage_uri=storage_uri,
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def get(
        self, *, tenant_id: str, pool_id: str, document_id: str
    ) -> DocumentRow | None:
        statement = select(DocumentRow).where(
            DocumentRow.tenant_id == tenant_id,
            DocumentRow.pool_id == pool_id,
            DocumentRow.document_id == document_id,
        )
        return await self._session.scalar(statement)
