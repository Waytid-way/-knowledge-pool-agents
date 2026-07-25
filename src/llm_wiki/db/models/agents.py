"""Agent specification, evaluation, and promotion rows."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Float, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from llm_wiki.db.base import Base, TimestampMixin
from llm_wiki.db.types import JSON_VALUE


class AgentSpecRow(TimestampMixin, Base):
    __tablename__ = "agent_specs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id"],
            ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("tenant_id", "pool_id", "agent_id", "agent_version"),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    agent_version: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    blueprint: Mapped[dict[str, Any]] = mapped_column(JSON_VALUE, nullable=False)
    permissions: Mapped[dict[str, Any]] = mapped_column(JSON_VALUE, nullable=False)


class AgentEvaluationRow(TimestampMixin, Base):
    __tablename__ = "agent_evaluations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id", "agent_id", "agent_version"],
            [
                "agent_specs.tenant_id",
                "agent_specs.pool_id",
                "agent_specs.agent_id",
                "agent_specs.agent_version",
            ],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(128), nullable=False)
    agent_version: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON_VALUE, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class PromotionCandidateRow(TimestampMixin, Base):
    __tablename__ = "promotion_candidates"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id"],
            ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    source_object_id: Mapped[str] = mapped_column(String(128), nullable=False)
    target_pool_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    justification: Mapped[dict[str, Any]] = mapped_column(JSON_VALUE, nullable=False)
