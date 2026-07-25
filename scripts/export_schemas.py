from __future__ import annotations

import argparse
import json
from pathlib import Path

from pydantic import BaseModel

from llm_wiki.domain.agents import AgentResult, TaskEnvelope
from llm_wiki.domain.documents import PageElement, PageManifest, ReadingUnit, SourceDocument
from llm_wiki.domain.evidence import EvidenceItem, SourceRef
from llm_wiki.domain.knowledge import KnowledgeObject, QuestionObject, Relationship
from llm_wiki.domain.pools import KnowledgePool
from llm_wiki.domain.reasoning import ReasoningTrace
from llm_wiki.domain.workflows import WorkflowRun

SCHEMAS: dict[str, type[BaseModel]] = {
    "agent-result.schema.json": AgentResult,
    "evidence-item.schema.json": EvidenceItem,
    "knowledge-object.schema.json": KnowledgeObject,
    "knowledge-pool.schema.json": KnowledgePool,
    "page-element.schema.json": PageElement,
    "page-manifest.schema.json": PageManifest,
    "question-object.schema.json": QuestionObject,
    "reading-unit.schema.json": ReadingUnit,
    "reasoning-trace.schema.json": ReasoningTrace,
    "relationship.schema.json": Relationship,
    "source-document.schema.json": SourceDocument,
    "source-ref.schema.json": SourceRef,
    "task-envelope.schema.json": TaskEnvelope,
    "workflow-run.schema.json": WorkflowRun,
}


def _schema_bytes(model: type[BaseModel]) -> bytes:
    payload = json.dumps(model.model_json_schema(), indent=2, sort_keys=True)
    return f"{payload}\n".encode()


def export_schemas(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, model in sorted(SCHEMAS.items()):
        (output_dir / filename).write_bytes(_schema_bytes(model))


def check_schemas(output_dir: Path) -> list[str]:
    drift: list[str] = []
    expected_names = set(SCHEMAS)
    actual_names = {path.name for path in output_dir.glob("*.schema.json")}
    drift.extend(f"missing:{name}" for name in sorted(expected_names - actual_names))
    drift.extend(f"unexpected:{name}" for name in sorted(actual_names - expected_names))
    for filename, model in sorted(SCHEMAS.items()):
        path = output_dir / filename
        if path.exists() and path.read_bytes() != _schema_bytes(model):
            drift.append(f"changed:{filename}")
    return drift


def main() -> int:
    parser = argparse.ArgumentParser(description="Export deterministic Pydantic JSON Schemas")
    parser.add_argument("--output", type=Path, default=Path("schemas"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        drift = check_schemas(args.output)
        if drift:
            for item in drift:
                print(item)
            return 1
        return 0

    export_schemas(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
