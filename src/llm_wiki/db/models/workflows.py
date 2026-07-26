"""Durable workflow state and event rows."""

from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKeyConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from llm_wiki.db.base import Base, TimestampMixin
from llm_wiki.db.types import JSON_VALUE


class WorkflowRunRow(TimestampMixin, Base):
    __tablename__ = "workflow_runs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id", "document_id"],
            ["documents.tenant_id", "documents.pool_id", "documents.document_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("tenant_id", "pool_id", "run_id"),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(64), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON_VALUE, nullable=False, default=dict)


class WorkflowEventRow(TimestampMixin, Base):
    __tablename__ = "workflow_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id", "run_id"],
            ["workflow_runs.tenant_id", "workflow_runs.pool_id", "workflow_runs.run_id"],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(128), nullable=False)
    from_state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    to_state: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON_VALUE, nullable=False, default=dict)
