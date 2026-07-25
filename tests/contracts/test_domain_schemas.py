from pathlib import Path

import pytest
from pydantic import ValidationError
from scripts.export_schemas import export_schemas

from llm_wiki.domain.agents import AgentResult, TaskEnvelope
from llm_wiki.domain.documents import PageElement, PageManifest, ReadingUnit
from llm_wiki.domain.enums import (
    DocumentStatus,
    ElementStatus,
    KnowledgeStatus,
    PoolScope,
    WorkflowState,
)
from llm_wiki.domain.knowledge import KnowledgeObject, QuestionObject, Relationship
from llm_wiki.domain.pools import KnowledgePool
from llm_wiki.domain.reasoning import ReasoningTrace
from llm_wiki.domain.workflows import WorkflowRun


def test_knowledge_object_requires_pool_and_source() -> None:
    with pytest.raises(ValidationError):
        KnowledgeObject(
            object_id="ko_1",
            object_type="concept",
            title="Token rotation",
            status=KnowledgeStatus.EXPLICIT,
            content={"summary": "Rotate after use"},
        )


def test_project_object_requires_project_id() -> None:
    with pytest.raises(ValidationError, match="project_id is required"):
        KnowledgeObject(
            object_id="ko_1",
            object_type="concept",
            title="Token rotation",
            pool_id="project-alpha",
            scope=PoolScope.PROJECT,
            status=KnowledgeStatus.EXPLICIT,
            content={"summary": "Rotate after use"},
            sources=[{"document_id": "doc_1", "pages": [1]}],
        )


def test_global_object_rejects_project_id() -> None:
    with pytest.raises(ValidationError, match="project_id is not allowed"):
        KnowledgeObject(
            object_id="ko_1",
            object_type="concept",
            title="Token rotation",
            pool_id="global",
            scope=PoolScope.GLOBAL,
            project_id="alpha",
            status=KnowledgeStatus.EXPLICIT,
            content={"summary": "Rotate after use"},
            sources=[{"document_id": "doc_1", "pages": [1]}],
        )


def test_source_pages_must_be_positive_and_unique() -> None:
    with pytest.raises(ValidationError):
        KnowledgeObject(
            object_id="ko_1",
            object_type="concept",
            title="Token rotation",
            pool_id="global",
            scope=PoolScope.GLOBAL,
            status=KnowledgeStatus.EXPLICIT,
            content={"summary": "Rotate after use"},
            sources=[{"document_id": "doc_1", "pages": [1, 1]}],
        )


def test_contracts_are_immutable() -> None:
    obj = KnowledgeObject(
        object_id="ko_1",
        object_type="concept",
        title="Token rotation",
        pool_id="global",
        scope=PoolScope.GLOBAL,
        status=KnowledgeStatus.EXPLICIT,
        content={"summary": "Rotate after use"},
        sources=[{"document_id": "doc_1", "pages": [1]}],
    )
    with pytest.raises(ValidationError):
        obj.title = "Changed"  # type: ignore[misc]


def test_project_pool_requires_project_id() -> None:
    with pytest.raises(ValidationError, match="project_id is required"):
        KnowledgePool(pool_id="project-alpha", name="Alpha", scope=PoolScope.PROJECT)


def test_page_manifest_and_reading_unit_validate_page_ranges() -> None:
    element = PageElement(
        element_id="p1-heading-1",
        element_type="heading",
        status=ElementStatus.DISCOVERED,
    )
    manifest = PageManifest(
        document_id="doc_1",
        page_number=1,
        document_status=DocumentStatus.REGISTERED,
        elements=[element],
    )
    unit = ReadingUnit(
        unit_id="unit_1",
        document_id="doc_1",
        title="Introduction",
        pages=[1],
        expected_elements={"heading": 1},
    )
    assert manifest.page_number == unit.pages[0]


def test_relationship_question_and_reasoning_trace_are_evidence_backed() -> None:
    relationship = Relationship(
        relationship_id="rel_1",
        source_object_id="ko_1",
        relationship_type="supports",
        target_object_id="ko_2",
        sources=[{"document_id": "doc_1", "pages": [2]}],
    )
    question = QuestionObject(
        question_id="q_1",
        question_type="causal",
        question="Why rotate tokens?",
        pool_id="global",
        scope=PoolScope.GLOBAL,
        answer_object_ids=["ko_1"],
        sources=[{"document_id": "doc_1", "pages": [2]}],
    )
    trace = ReasoningTrace(
        trace_id="trace_1",
        task_id="task_1",
        facts=["The document mandates rotation."],
        rules=["Canonical facts require evidence."],
        hypotheses=[],
        decision="Create an explicit knowledge object.",
        outcome="accepted",
        source_refs=[{"document_id": "doc_1", "pages": [2]}],
    )
    assert relationship.sources == question.sources == trace.source_refs


def test_task_envelope_and_result_bind_agent_and_pool_permissions() -> None:
    task = TaskEnvelope(
        task_id="task_1",
        run_id="run_1",
        agent_id="extractor",
        agent_version="1.0.0",
        input={"document_id": "doc_1"},
        allowed_read_pools=["global", "project-alpha"],
        allowed_write_pools=["project-alpha:candidate"],
        required_output_schema="knowledge-object.schema.json",
    )
    result = AgentResult(
        task_id="task_1",
        agent_id="extractor",
        agent_version="1.0.0",
        status="completed",
        outputs=[{"object_id": "ko_1"}],
        metrics={"objects_created": 1},
    )
    assert task.task_id == result.task_id


def test_workflow_run_rejects_direct_publication_from_registered_state() -> None:
    with pytest.raises(ValidationError, match="cannot jump directly"):
        WorkflowRun(
            run_id="run_1",
            document_id="doc_1",
            pool_id="project-alpha",
            current_state=WorkflowState.DOCUMENT_REGISTERED,
            requested_state=WorkflowState.PUBLISHED,
        )


def test_exported_schemas_match_committed_files(tmp_path: Path) -> None:
    export_schemas(tmp_path)
    committed = Path("schemas")
    assert sorted(path.name for path in tmp_path.glob("*.schema.json")) == sorted(
        path.name for path in committed.glob("*.schema.json")
    )
    for generated in tmp_path.glob("*.schema.json"):
        assert generated.read_bytes() == (committed / generated.name).read_bytes()
