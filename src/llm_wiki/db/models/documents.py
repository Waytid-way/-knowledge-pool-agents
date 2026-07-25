"""Source document, page, element, and reading-unit rows."""

from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKeyConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from llm_wiki.db.base import Base, TimestampMixin
from llm_wiki.db.types import JSON_VALUE


class DocumentRow(TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id"],
            ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("tenant_id", "pool_id", "content_hash"),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    project_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    media_type: Mapped[str] = mapped_column(String(128), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class DocumentPageRow(TimestampMixin, Base):
    __tablename__ = "document_pages"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id", "document_id"],
            ["documents.tenant_id", "documents.pool_id", "documents.document_id"],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    page_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    section_path: Mapped[list[str]] = mapped_column(JSON_VALUE, nullable=False, default=list)
    reading_unit_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    page_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)


class PageElementRow(TimestampMixin, Base):
    __tablename__ = "page_elements"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id", "document_id", "page_number"],
            [
                "document_pages.tenant_id",
                "document_pages.pool_id",
                "document_pages.document_id",
                "document_pages.page_number",
            ],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    page_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    element_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    element_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    label: Mapped[str | None] = mapped_column(String(512), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON_VALUE, nullable=False, default=dict)


class ReadingUnitRow(TimestampMixin, Base):
    __tablename__ = "reading_units"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id", "document_id"],
            ["documents.tenant_id", "documents.pool_id", "documents.document_id"],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    unit_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    pages: Mapped[list[int]] = mapped_column(JSON_VALUE, nullable=False)
    expected_elements: Mapped[dict[str, int]] = mapped_column(
        JSON_VALUE, nullable=False, default=dict
    )
    continuation_from: Mapped[str | None] = mapped_column(String(128), nullable=True)
    continuation_to: Mapped[str | None] = mapped_column(String(128), nullable=True)
