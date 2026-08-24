# ADR-0001 — Canonical ERP Analytical Architecture

**Status:** Accepted

## Context
The project must be demonstrable with a fictitious ERP while remaining extensible toward real ERPs without coupling the agentic layer to proprietary schemas.

## Decision
The application operates on a **Canonical ERP Data Model** in PostgreSQL. Domain repositories/services depend on this canonical contract. Future real ERP integrations map source systems into the canonical analytical layer through adapters/integration processes.

## Consequences
- Core development is reproducible and public-safe.
- Agent/tools remain ERP-agnostic.
- Future adapters absorb source-specific mappings.
- A replicated/analytical store is preferred before direct agent access to transactional ERP systems.
