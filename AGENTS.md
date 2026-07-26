# AGENTS.md

This file applies to the entire repository unless a more specific `AGENTS.md` exists in a subdirectory.

## Mission

Build a production-oriented, scoped, auditable, multimodal PDF-to-knowledge platform. The system uses deterministic orchestration around probabilistic Agents, converts source evidence into Knowledge Objects, verifies coverage and provenance, and publishes project-aware Wiki views through a 7+1 Agent architecture.

The implementation plan is the primary roadmap:

`docs/superpowers/plans/2026-07-26-llm-wiki-greenfield-implementation-plan.md`

Always read the active GitHub Issue and the relevant tests before changing code. Do not infer requirements that are absent from the plan, issue, contracts, or tests.

## Non-negotiable architecture invariants

1. PDF understanding is modality-first. OCR is a fallback, not the primary ingestion path.
2. Every Knowledge Object carries an explicit `tenant_id`, `pool_id`, lifecycle status, provenance, and source references.
3. Authorization occurs before retrieval and before model-context construction.
4. Never trust a tenant, project, pool, permission, workflow state, or publication decision supplied by a model.
5. Agents propose candidate outputs. Deterministic services own validation, permissions, workflow state, promotion, canonicalization, and publication.
6. Project Knowledge may inherit Global Knowledge but never flows into Global automatically.
7. Global writes require an explicit promotion workflow and governance approval.
8. Canonical facts require source evidence. Unsupported conclusions remain labeled `inferred`.
9. Workflows and Agent actions must be idempotent, traceable, and replay-safe.
10. No change may weaken tenant isolation, project isolation, citation coverage, auditability, or deterministic quality gates for throughput.
11. Initial graph storage uses PostgreSQL adjacency tables. Do not introduce a graph database without an approved architecture decision.
12. Initial publication produces versioned Markdown and JSON. A rich frontend is out of scope until explicitly scheduled.

## Knowledge Pool rules

Knowledge scope precedence is deterministic:

1. Task / Session
2. Project
3. Domain
4. Organization
5. Global

More specific knowledge may specialize or override broader knowledge without deleting or mutating the broader record.

Supported explicit relationships include:

- `extends`
- `specializes`
- `overrides`
- `exception_to`
- `contradicts`
- `supersedes`
- `inherits`

Agents may read multiple authorized pools but may write only to their explicitly authorized candidate pool. Denied scopes must not leak through results, counts, error details, traces, cache keys, or timing-dependent shortcuts.

All retrieval and Agent-context construction must consume a deterministic Context Package produced after identity, authorization, project context, pool resolution, and write-scope validation.

## 7+1 Agent architecture

- Agent 0 — Agent Foundry
- Agent 1 — Document Profiler
- Agent 2 — Structural Mapper
- Agent 3 — Multimodal Knowledge Extractor
- Agent 4 — Knowledge Normalizer
- Agent 5 — Relationship and Question Builder
- Agent 6 — Coverage and Evidence Verifier
- Agent 7 — Wiki Composer and Publisher

Do not move deterministic policy, authorization, validation, or publication gates into prompts. Agent Foundry produces declarative blueprints only until activation governance is implemented.

## Reasoning modes

Use the seven reasoning modes deliberately and state the relevant modes in substantial PR descriptions:

- **Deductive:** schemas, authorization, invariants, and publish gates
- **Inductive:** corpus metrics, calibration, routing quality, and drift
- **Abductive:** failure diagnosis, missing-evidence hypotheses, and capability gaps
- **Modal:** workflow states, retries, compensation, and terminal guarantees
- **Fuzzy:** confidence, ambiguity, risk, and human-review thresholds
- **Dialectical:** conflicting claims, scoped overrides, and architecture trade-offs
- **Informal:** evidence quality, assumptions, citations, and reviewer explanations

Fuzzy scores may rank or escalate already-authorized information. They must never grant access or replace deterministic policy.

## Development workflow

Use Superpowers Subagent-Driven Development task by task.

For every behavior change:

1. Read the active Issue, plan section, existing contracts, and adjacent tests.
2. Write a failing test that demonstrates the required behavior or regression.
3. Confirm the test fails for the expected reason.
4. Implement the smallest correct change.
5. Run the focused test until it passes.
6. Run the broader relevant suite.
7. Refactor only while tests remain green.
8. Review the diff for isolation, provenance, migration, and audit risks.
9. Commit a single coherent unit of work.
10. Open a draft PR unless explicitly instructed otherwise.

Keep one planned task per branch and PR. Avoid unrelated formatting, dependency upgrades, or broad refactors.

Branch naming:

`agent/<short-description>`

Commit messages should be terse and describe the completed change.

## Required commands

Install dependencies:

```bash
uv sync --all-extras
```

Run static checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

Run tests:

```bash
uv run pytest -q
```

Run PostgreSQL integration tests:

```bash
uv run pytest tests/integration/db -v
```

Verify migrations:

```bash
uv run alembic upgrade head
uv run alembic downgrade base
uv run alembic upgrade head
```

Equivalent Make targets are available through `make lint`, `make test`, `make test-integration`, `make migrate`, and `make migrate-down`.

Do not claim a check passed unless it was run and its result was observed. Report environment limitations explicitly.

## Testing requirements

Every security or scope boundary requires both positive and negative tests.

At minimum, preserve or add tests for:

- same identifiers isolated across tenants
- same identifiers isolated across projects and pools
- forged tenant, project, and pool identifiers
- denied reads returning no data and no observable metadata
- unauthorized Global writes
- deterministic inheritance and override precedence
- stale workflow versions
- migration upgrade, downgrade, and re-upgrade
- source and citation requirements for canonical knowledge
- idempotency for repeated workflow and repository operations

Integration tests must exercise PostgreSQL constraints rather than reproducing them only in Python assertions.

## Database and migration rules

- Repository reads and writes require explicit tenant and Knowledge Pool context.
- Prefer composite keys and foreign keys that include tenant and scope columns.
- Scope safety must be enforced by database constraints where practical.
- Never edit an applied historical migration to follow current ORM metadata.
- Historical migrations must contain frozen, explicit DDL and must not call `Base.metadata.create_all()` or `Base.metadata.drop_all()`.
- Schema changes require a new Alembic revision with a dependency-safe downgrade.
- Migration round-trip validation is required before merge.
- Do not add unscoped repository methods as convenience shortcuts.

## Evidence, provenance, and audit

No source means no canonical fact.

Preserve the distinction between:

- source evidence
- structured evidence
- candidate knowledge
- canonical knowledge
- hypotheses
- decisions
- published claims

Every Agent execution must record facts, rules, hypotheses, decisions, and outcome. Authorization and pool-resolution decisions must be auditable without exposing denied data.

Do not silently merge contradictory claims. Preserve conflict, scope, provenance, and lifecycle state.

## Pull request expectations

A PR description should include:

- the Issue or plan task implemented
- what changed and why
- affected architecture invariants
- reasoning modes used
- security and isolation considerations
- migrations added or changed
- tests and commands actually run
- deferred work and known limitations

Before marking a PR ready for review, verify:

- Ruff lint passes
- Ruff formatting passes
- mypy passes
- focused and full tests pass
- PostgreSQL integration tests pass when applicable
- Alembic upgrade/downgrade/re-upgrade passes when applicable
- no unresolved major review findings remain
- the branch is based on current `main`

## Anti-patterns

Do not:

- use an LLM as the policy engine
- treat correlation as causation
- present fuzzy confidence as probability or authorization
- hide trade-offs behind vague language
- return only a final answer without traceable evidence
- add OCR-first ingestion
- allow unrestricted Agent-to-Agent communication
- allow self-modifying orchestration policies
- couple the core to one model vendor
- auto-promote Project Knowledge to Global
- expose cross-project or cross-tenant information through diagnostics

## Current execution sequence

Follow the numbered task sequence in the implementation plan. Tasks 1–3 established the foundation and scoped persistence. The next planned capability is tracked in GitHub Issue #8: Knowledge Pool inheritance and authorization-before-retrieval.

Verify Issue status before beginning work because repository priorities may change.