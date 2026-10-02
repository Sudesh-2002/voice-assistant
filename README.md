# Ledger — CQRS + Event Sourcing Banking System

A distributed banking ledger built in Spring Boot to demonstrate production-grade **CQRS** and **Event Sourcing** patterns: an append-only event store as the single source of truth, Kafka-driven eventually-consistent read models, snapshotting, a transactional outbox, idempotent APIs, and circuit-breaker-protected resilience.

## Architecture

```
                    ┌─────────────────┐
                    │   REST Clients   │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
     ┌─────────────────┐           ┌──────────────────┐
     │   COMMAND SIDE    │           │    QUERY SIDE     │
     │  (writes)          │           │   (reads)          │
     │                     │           │                    │
     │  Account Aggregate  │           │  Projections:      │
     │  - open/deposit/    │           │  - account_summary  │
     │    withdraw         │           │  - transaction_hist │
     │  - business rules   │           │                    │
     └─────────┬───────────┘           └────────▲───────────┘
               │                                  │
               ▼                                  │
     ┌─────────────────────┐          ┌──────────┴──────────┐
     │   EVENT STORE (PG)    │          │  Kafka Consumer       │
     │   append-only,         │          │  (idempotent           │
     │   optimistic locking   │          │   projector)           │
     └─────────┬───────────────┘          └──────────▲──────────┘
               │                                        │
               ▼                                        │
     ┌─────────────────────┐                  ┌────────┴────────┐
     │  Transactional Outbox │─────publishes──▶│  Kafka Topic     │
     │  (same DB transaction │   (scheduled     │  account-events  │
     │   as event write)      │    poller)       └─────────────────┘
     └─────────────────────┘
```

**Core principle:** the event store is the only source of truth. Every read model is disposable and can be rebuilt from scratch by replaying the event log — proven by a dedicated `/api/admin/projections/rebuild` endpoint.

## Why this project is hard

Most CRUD portfolio projects update a row and call it done. This one deliberately confronts the problems that make distributed systems hard in practice:

| Problem | Solution implemented |
|---|---|
| Two writers racing to update the same aggregate | Optimistic concurrency via a DB unique constraint on `(aggregate_id, sequence_number)` |
| Rebuilding state without a "current state" table | Event replay — aggregates are reconstructed by folding their full event history |
| Replay getting slow as history grows | Snapshotting every N events; load path becomes "latest snapshot + events since" |
| Read model falling out of sync with writes | Kafka-based async projection, idempotent by design (version-guarded upserts) |
| Losing an event between DB commit and Kafka publish | Transactional outbox pattern — event store write and outbox write are one atomic transaction |
| A client retrying a timed-out request | Idempotency-Key header, enforced via a DB-backed reservation table |
| Kafka going down and cascading failures | Resilience4j circuit breaker around the outbox publisher |
| A message that keeps failing to project | Dead-letter handling on both the outbox (publish side) and the Kafka consumer (projection side) |

## Tech Stack

- **Java 17**, **Spring Boot 3**
- **PostgreSQL** — event store, snapshots, outbox, read models (Flyway-managed schema)
- **Apache Kafka** (KRaft mode) — async event propagation between write and read sides
- **Resilience4j** — circuit breaker for Kafka publishing
- **Micrometer + Prometheus + Grafana** — metrics and dashboards (command throughput, outbox backlog, dead-letter counts)
- **springdoc-openapi** — live Swagger UI
- **Docker Compose** — Postgres, Kafka, Kafka UI, Prometheus, Grafana, and the app itself
- **JUnit 5, AssertJ, Awaitility** — unit and integration tests, including replay-correctness and eventual-consistency assertions

## Getting Started

### Prerequisites
- Java 17+
- Maven
- Docker Desktop

### Run locally

```bash
docker compose up -d --build
```

This brings up Postgres, Kafka, Kafka UI (`localhost:8081`), Prometheus (`localhost:9090`), Grafana (`localhost:3000`, admin/admin), and the app itself (`localhost:8080`).

Or, to run the app outside Docker against the containerized infra:

```bash
docker compose up -d postgres kafka
mvn spring-boot:run
```

### API docs

Swagger UI: `http://localhost:8080/swagger-ui.html`

### Example flow

```bash
# open an account (idempotency key required on all command endpoints)
curl -X POST http://localhost:8080/api/accounts \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{"accountId":"acc-1","ownerName":"Sudesh","openingBalance":100.00}'

# deposit
curl -X POST http://localhost:8080/api/accounts/acc-1/deposit \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{"amount":50.00,"reference":"salary"}'

# read the projection (eventually consistent — usually near-instant locally)
curl http://localhost:8080/api/accounts/acc-1/summary

# full transaction history
curl http://localhost:8080/api/accounts/acc-1/transactions

# rebuild every read model from the event store, from scratch
curl -X POST http://localhost:8080/api/admin/projections/rebuild
```

## Observability

Metrics exposed at `/actuator/prometheus`, including:

- `ledger_commands_processed_total` / `ledger_commands_rejected_total`
- `ledger_command_latency` — end-to-end command processing time
- `ledger_outbox_backlog` — unpublished outbox rows (the key signal for "is the read side keeping up")
- `ledger_outbox_published_total` / `ledger_outbox_dead_lettered_total`

Import these into Grafana against the Prometheus data source (`http://prometheus:9090`) for live dashboards.

## Project Structure

```
src/main/java/com/sudesh/ledger/
├── command/           # write side: aggregate, commands, events, command service, REST controllers
├── query/              # read side: projections, projector, rebuild service, REST controllers
├── eventstore/         # append-only event store, snapshots, transactional outbox
├── config/              # Kafka, Resilience4j, OpenAPI, scheduling config
└── shared/              # cross-cutting: error handling, idempotency, metrics, envelopes
```

## Testing

```bash
mvn test
```

Covers:
- Pure domain logic (aggregate command handling, no Spring context)
- Event store append + optimistic concurrency rejection
- Snapshot-plus-replay producing identical state to full replay
- Projection eventual consistency and full rebuild-from-event-store correctness
- Idempotency key deduplication under retry
- Global error handling → correct HTTP status mapping

## Known Trade-offs / Next Steps

- Currently a modular monolith (command and query sides share a deployable) — a natural extension is splitting them into two genuinely separate services communicating only via Kafka.
- No `Transfer` command spanning two aggregates yet — adding one would introduce the Saga pattern for cross-aggregate consistency.
- Local dev integration tests depend on `docker compose up` being run first; migrating to Testcontainers would make `mvn test` fully self-contained.


---

Built as a portfolio project to demonstrate CQRS, Event Sourcing, and distributed-systems patterns in a realistic domain (banking) rather than a toy example.
