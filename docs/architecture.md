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

