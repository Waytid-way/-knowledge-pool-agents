# llm-wiki Greenfield Implementation Plan

> **Execution mode:** Use Superpowers Subagent-Driven Development task-by-task. Every feature follows TDD: failing test, minimal implementation, passing test, review, then commit.

## Goal

Build a production-oriented `llm-wiki` platform that ingests large PDFs through PDF-native multimodal models, converts them into scoped and auditable Knowledge Objects, verifies coverage, and publishes project-aware Wiki views through a 7+1 Agent architecture.

## Architecture

The platform uses a deterministic orchestration core around probabilistic Agents. PostgreSQL stores transactional state, scoped Knowledge Objects, relationships, embeddings, audit events, and workflow metadata. S3-compatible storage holds PDFs and rendered artifacts. Temporal coordinates durable workflows and retries. Agents operate through strict task contracts, read from resolved Knowledge Pools, and write only to authorized candidate stores.

## Global constraints

- PDF understanding is modality-first; OCR is not the primary ingestion path.
- Every Knowledge Object carries `pool_id`, provenance, lifecycle status, and source references.
- Project Knowledge may inherit Global Knowledge, but never flows into Global automatically.
- Pool authorization occurs before retrieval and before model-context construction.
- Agents propose; deterministic services own validation, permissions, workflow state, promotion, and publication.
- Canonical facts require source evidence; unsupported conclusions remain labeled `inferred`.
- Agent Foundry creates declarative Agent Blueprints only in the first production release.
- Global writes require a promotion workflow and explicit governance approval.
- Workflows and Agent actions are idempotent, traceable, and replay-safe.
- Initial graph storage uses PostgreSQL adjacency tables; a dedicated graph database is deferred.
- Initial Wiki publication produces versioned Markdown and JSON; a rich frontend is deferred.
- No task may weaken isolation, citation coverage, auditability, or deterministic quality gates for throughput.

## Seven reasoning modes

| Mode | Responsibility |
|---|---|
| Deductive | Schemas, authorization, invariants, and publish gates |
| Inductive | Corpus metrics, calibration, routing quality, and drift |
| Abductive | Failure diagnosis, missing-evidence hypotheses, and capability gaps |
| Modal | Workflow states, retries, compensation, and terminal guarantees |
| Fuzzy | Confidence, ambiguity, risk, and human-review thresholds |
| Dialectical | Conflicting claims, scoped overrides, and architecture trade-offs |
| Informal | Evidence quality, assumptions, citations, and reviewer explanations |

## Delivery releases

1. **R0 — Deterministic foundation:** repository, contracts, persistence, Knowledge Pools, security boundaries.
2. **R1 — Ingestion kernel:** document storage, model gateway, durable workflow, Agent runtime.
3. **R2 — Core Agents:** Agents 1–7 with candidate-only writes and verification gates.
4. **R3 — Retrieval and Wiki:** scoped context resolution, question graph, Markdown publication.
5. **R4 — Capability evolution:** Agent Foundry, Capability Graph, promotion, and evaluation.
6. **R5 — Production hardening:** adversarial tests, observability, deployment, and rollback.

## Task sequence

1. Bootstrap the monorepo and developer feedback loop.
2. Define domain contracts and JSON Schemas.
3. Implement persistence, migrations, and repository boundaries.
4. Build Knowledge Pools, inheritance, and authorization-before-retrieval.
5. Implement document registration and S3-compatible storage.
6. Create the provider-neutral PDF-native model gateway contract.
7. Implement the durable ingestion state machine with Temporal.
8. Build the Agent runtime, registry, permissions, and reasoning trace.
9. Implement Agent 1 — Document Profiler.
10. Implement Agent 2 — Structural Mapper and Semantic Reading Units.
11. Implement Agent 3 — Multimodal Knowledge Extractor.
12. Implement Agent 4 — Knowledge Normalizer.
13. Implement Agent 5 — Relationship, Question, and Reasoning Graph Builder.
14. Implement Agent 6 — Coverage and Evidence Verifier.
15. Implement Agent 7 — Scoped Wiki Composer and Publisher.
16. Implement scoped retrieval and Context Package construction.
17. Implement Agent 0 — Agent Foundry and Capability Graph.
18. Add the seven Reasoning Executors as reusable capabilities.
19. Expose API and CLI workflows with explicit project context.
20. Add security controls and adversarial test suites.
21. Add immutable audit, observability, and reasoning-mode metrics.
22. Build the evaluation harness, golden corpus, and promotion gates.
23. Package deployment, migrations, backup, restore, and rollback.

## First usable vertical slice

The first architecture proof includes Tasks 1–11, 14–16, and 19:

1. Register one PDF under Project Alpha.
2. Store the source in MinIO.
3. Profile and structurally map every page.
4. Extract candidate objects with fixture-backed PDF-modality responses.
5. Verify physical, structural, and citation coverage.
6. Search using Project Alpha plus Global Knowledge.
7. Publish a versioned Markdown Wiki.
8. Prove Project Beta cannot retrieve Alpha objects.

## Completion gates

- Physical page coverage equals `1.0` on the golden corpus.
- Citation coverage equals `1.0`.
- Cross-project leakage count equals `0`.
- Unauthorized Global writes equal `0`.
- Every published Wiki claim traces to source pages.
- Every Agent execution records facts, rules, hypotheses, decisions, and outcome.
- No workflow can jump directly to `PUBLISHED`.
- No model-supplied permission or Pool ID is trusted.
- Project-specific conflicts remain visible and are not merged into Global Knowledge.
- Agent Foundry may produce a Blueprint but cannot activate it.
- Backup and restore verification succeeds.

## Deferred decisions

- Dedicated graph database.
- Rich web authoring UI.
- Executable code generation by Agent Foundry.
- Automatic Project-to-Global promotion.
- OCR-first extraction.
- Unrestricted Agent-to-Agent communication.
- Self-modifying orchestration policies.
- Vendor-specific model coupling in the core.
- Cross-organization shared pools.
