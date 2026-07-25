"""Tenant, project, and Knowledge Pool rows."""

from __future__ import annotations

from typing import Any

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from llm_wiki.db.base import Base, TimestampMixin
from llm_wiki.db.types import JSON_VALUE


class TenantRow(TimestampMixin, Base):
    __tablename__ = "tenants"

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class ProjectRow(TimestampMixin, Base):
    __tablename__ = "projects"
    __table_args__ = (
        ForeignKeyConstraint(["tenant_id"], ["tenants.tenant_id"], ondelete="CASCADE"),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")


class KnowledgePoolRow(TimestampMixin, Base):
    __tablename__ = "knowledge_pools"
    __table_args__ = (
        ForeignKeyConstraint(["tenant_id"], ["tenants.tenant_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(
            ["tenant_id", "project_id"],
            ["projects.tenant_id", "projects.project_id"],
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "(scope = 'project' AND project_id IS NOT NULL) OR "
            "(scope <> 'project' AND (scope <> 'global' OR project_id IS NULL))",
            name="scope_project_context",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    project_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    visibility: Mapped[str] = mapped_column(String(32), nullable=False, default="private")
    parent_pool_ids: Mapped[list[str]] = mapped_column(JSON_VALUE, nullable=False, default=list)
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON_VALUE, nullable=False, default=dict
    )
