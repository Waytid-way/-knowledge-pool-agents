"""Append-only audit event rows."""

from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from llm_wiki.db.base import Base, TimestampMixin
from llm_wiki.db.types import JSON_VALUE


class AuditEventRow(TimestampMixin, Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id"],
            ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    actor_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(128), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON_VALUE, nullable=False, default=dict)
    previous_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    event_hash: Mapped[str] = mapped_column(String(128), nullable=False)
