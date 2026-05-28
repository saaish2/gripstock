# Architecture

Gripstock is a layered FastAPI service. Each request flows top-to-bottom and
the dependencies only point downward, which keeps business rules isolated from
both the web framework and the database driver.

```
HTTP request
   │
   ▼
routers/         FastAPI endpoint groups — parse input, enforce RBAC,
   │             serialise responses. No business logic.
   ▼
services/        Business logic and invariants. Orchestrates repositories,
   │             raises typed domain errors, writes audit entries.
   ▼
repositories/    Data access. Owns all query construction (filters, soft
   │             deletes, overlap detection). Returns ORM objects.
   ▼
models/          SQLAlchemy ORM entities + reusable mixins.
   ▼
database         SQLite (dev/test) or PostgreSQL (prod) via SQLAlchemy.
```

## Module map

| Layer        | Module                | Responsibility                              |
|--------------|-----------------------|---------------------------------------------|
| Config       | `app/config.py`       | Env-driven settings singleton               |
| Logging      | `app/logging.py`      | Structured logging + request-id context     |
| Errors       | `app/errors.py`       | Domain error hierarchy + HTTP translation   |
| Security     | `app/security.py`     | Password hashing, token + API-key handling  |
| Pricing      | `app/services/pricing.py` | Pure rental pricing engine              |
| Reservations | `app/services/reservations.py` | Availability + lifecycle           |
| Billing      | `app/services/billing.py` | Invoices, payments, late fees           |
| Operations   | `app/services/operations.py` | Checkout/checkin, damage, maintenance |
| Workers      | `app/workers/`        | Overdue + late-fee sweeps, webhook dispatch |

## Core state machines

### Reservation

```
pending ──confirm──▶ confirmed ──checkout──▶ picked_up ──checkin──▶ returned
   │                    │                        │
 cancel               cancel / no_show       (past due)
   ▼                    ▼                        ▼
cancelled           cancelled / no_show       overdue ──checkin──▶ returned
```

### Asset

```
available ⇄ reserved ──▶ checked_out ──▶ available
    │                        │
    ├──▶ in_maintenance ──▶ available
    └──▶ retired (terminal)        lost ──▶ available
```

### Invoice

```
draft ──issue──▶ issued ──▶ partially_paid ──▶ paid
                   │              │
                   └──▶ overdue ◀─┘
draft / issued / partially_paid / overdue ──void──▶ void
```

Allowed transitions are encoded as adjacency tables in `app/enums.py`; the
service layer rejects any move not present there with an `InvalidStateError`.

## Availability detection

Two half-open intervals `[a_start, a_end)` and `[b_start, b_end)` overlap iff
`a_start < b_end and b_start < a_end`. `ReservationRepository.overlapping_line_ids`
applies exactly this predicate, scoped to reservations in a *blocking* status
(pending, confirmed, picked_up, overdue), so cancelled and returned rentals
free their inventory immediately.

## Idempotency

`POST /orders` accepts an `Idempotency-Key` header. The first success is
persisted; replays with the same key return the stored response verbatim,
making order creation safe to retry without double-booking.
