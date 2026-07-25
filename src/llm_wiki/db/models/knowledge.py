"""Candidate, canonical, relationship, question, and reasoning rows."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Float, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from llm_wiki.db.base import Base, TimestampMixin
from llm_wiki.db.types import JSON_VALUE, vector_type


class CandidateObjectRow(TimestampMixin, Base):
    __tablename__ = "candidate_objects"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id"],
            ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    object_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    object_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    project_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSON_VALUE, nullable=False)
    sources: Mapped[list[dict[str, Any]]] = mapped_column(JSON_VALUE, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")


class KnowledgeObjectRow(TimestampMixin, Base):
    __tablename__ = "knowledge_objects"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id"],
            ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("tenant_id", "pool_id", "object_id"),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    object_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    object_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    project_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSON_VALUE, nullable=False)
    sources: Mapped[list[dict[str, Any]]] = mapped_column(JSON_VALUE, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")
    embedding: Mapped[list[float] | None] = mapped_column(vector_type(1536), nullable=True)


class RelationshipRow(TimestampMixin, Base):
    __tablename__ = "relationships"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id", "source_object_id"],
            [
                "knowledge_objects.tenant_id",
                "knowlede_objects.pool_id",
                "knowledge_objects.object_id",
            ],
            ondelete="CASCADE",
            name="fk_relationships_source_object",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "pool_id", "target_object_id"],
            [
                "knowledge_objects.tenant_id",
                "knowledge_objects.pool_id",
                "knowledge_objects.object_id",
            ],
            ondelete="CASCADE",
            name="fk_relationships_target_object",
        ),
        UniqueConstraint(
            "tenant_id",
            "pool_id",
            "source_object_id",
            "relationship_type",
            "target_object_id",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    relationship_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    source_object_id: Mapped[str] = mapped_column(String(128), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_object_id: Mapped[str] = mapped_column(String(128), nullable=False)
    sources: Mapped[list[dict[str, Any]]] = mapped_column(JSON_VALUE, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")


class QuestionRow(TimestampMixin, Base):
    __tablename__ = "questions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id"],
            ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    question_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    question_type: Mapped[str] = mapped_column(String(64), nullable=False)
    question: Mapped[str] = mapped_column(String(2048), nullable=False)
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    project_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    answer_object_ids: Mapped[list[str]] = mapped_column(JSON_VALUE, nullable=False)
    sources: Mapped[list[dict[str, Any]]] = mapped_column(JSON_VALUE, nullable=False)
    answerability: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0")


class ReasoningTraceRow(TimestampMixin, Base):
    __tablename__ = "reasoning_traces"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "pool_id"],
            ["knowledge_pools.tenant_id", "knowledge_pools.pool_id"],
            ondelete="CASCADE",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pool_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(128), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(128), nullable=False)
    agent_version: Mapped[str] = mapped_column(String(64), nullable=False)
    reasoning_modes: Mapped[list[str]] = mapped_column(JSON_VALUE, nullable=False)
    facts: Mapped[list[str]] = mapped_column(JSON_VALUE, nullable=False, default=list)
    rules: Mapped[list[str]] = mapped_column(JSON_VALUE, nullable=False, default=list)
    hypotheses: Mapped[list[str]] = mapped_column(JSON_VALUE, nullable=False, default=list)
    decisions: Mapped[list[str]] = mapped_column(JSON_VALUE, nullable=False, default=list)
    outcome: Mapped[str] = mapped_column(String(2048), nullable=False)
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON_VALUE, nullable=False, default=dict
    )
