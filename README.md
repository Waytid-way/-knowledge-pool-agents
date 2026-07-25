# llm-wiki

A scoped, auditable, multimodal PDF-to-knowledge platform built around deterministic orchestration, Knowledge Pools, and a 7+1 Agent architecture.

## Current status

The repository is in the deterministic-foundation phase. The implementation plan lives at `docs/superpowers/plans/2026-07-26-llm-wiki-greenfield-implementation-plan.md`.

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker with Compose v2

## Local setup

```bash
cp .env.example .env
make install
make up
make lint
make test
```

Stop and remove local infrastructure with:

```bash
make down
```

The Temporal `auto-setup` image is used only for the local development loop. Production deployment design is deferred to the production-hardening release.
