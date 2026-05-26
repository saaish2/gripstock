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

