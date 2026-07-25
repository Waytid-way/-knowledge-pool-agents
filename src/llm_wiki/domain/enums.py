from enum import StrEnum


class PoolScope(StrEnum):
    GLOBAL = "global"
    ORGANIZATION = "organization"
    DOMAIN = "domain"
    PROJECT = "project"
    TASK = "task"


class KnowledgeStatus(StrEnum):
    EXPLICIT = "explicit"
    DERIVED = "derived"
    INFERRED = "inferred"
    UNCERTAIN = "uncertain"
    CONFLICTED = "conflicted"


class DocumentStatus(StrEnum):
    REGISTERED = "registered"
    STORED = "stored"
    PROFILING = "profiling"
    PROFILED = "profiled"
    PROCESSING = "processing"
    VERIFIED = "verified"
    FAILED = "failed"
    QUARANTINED = "quarantined"


class ElementStatus(StrEnum):
    DISCOVERED = "discovered"
    QUEUED = "queued"
    PROCESSING = "processing"
    PROCESSED = "processed"
    PARTIALLY_PROCESSED = "partially_processed"
    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"


class WorkflowState(StrEnum):
    DOCUMENT_REGISTERED = "document_registered"
    PROFILED = "profiled"
    STRUCTURE_MAPPED = "structure_mapped"
    READING_UNITS_CREATED = "reading_units_created"
    OBJECTS_EXTRACTED = "objects_extracted"
    OBJECTS_NORMALIZED = "objects_normalized"
    GRAPH_BUILT = "graph_built"
    COVERAGE_VERIFIED = "coverage_verified"
    WIKI_COMPOSED = "wiki_composed"
    PUBLISHED = "published"
    NEEDS_REPROCESSING = "needs_reprocessing"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    FAILED = "failed"
    QUARANTINED = "quarantined"


class ReasoningMode(StrEnum):
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    MODAL = "modal"
    FUZZY = "fuzzy"
    DIALECTICAL = "dialectical"
    INFORMAL = "informal"
