# Gripstock

Gripstock is an equipment-rental operations platform for **film & video
production rental houses**. It tracks gear inventory, reserves it for shoots,
checks it out and back in with condition inspections, prices and invoices the
rental, and handles damage, maintenance, and late fees — the day-to-day
machinery of a busy rental counter.

It is a FastAPI service backed by SQLAlchemy and Alembic, organised into clean
layers (routers → services → repositories → models) so business rules live in
one place and stay testable.

## Features

- **Inventory & catalog** — categories, individual assets with barcodes,
  serial numbers, and rate cards, plus reusable kits (bundles).
- **Reservations** — availability conflict detection over overlapping windows,
  a full lifecycle state machine, rescheduling, and cancellation that releases
  held inventory.
- **Pricing engine** — daily/weekly/monthly tier decomposition, seasonal
  multipliers, customer and bundle discounts, and refundable deposits.
- **Orders & invoicing** — draft orders from confirmed reservations, invoice
  generation, partial payments, void rules, and late-fee accrual.
- **Checkout / check-in** — condition inspections, automatic damage reports,
  and routing of damaged gear into maintenance.
- **Maintenance work orders** — labour/parts costs and asset status handling.
- **Platform concerns** — RBAC (admin/manager/agent/viewer), audit logging,
  API keys, webhooks with retry/backoff, and idempotent order creation.
- **Reporting** — inventory utilisation, revenue, overdue exposure, dashboards.
- **Background sweeps** — overdue reservations and late-fee accrual.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Create the schema and load demo data
gripstock initdb
gripstock seed

# Run the API
uvicorn app.main:app --reload
```

Open <http://localhost:8000/docs> for the interactive API documentation.

Default seeded admin: `admin@gripstock.test` / `changeit-please`.

## Configuration

All configuration is read from the environment with the `GRIPSTOCK_` prefix.
Copy `.env.example` to `.env` and adjust. The defaults boot a local SQLite
database with zero setup.

## Database & migrations

Development and tests build the schema directly from the ORM metadata
(`gripstock initdb`). Production uses Alembic:

```bash
alembic upgrade head
```

## Testing

```bash
make test       # run the pytest suite
make lint       # ruff + mypy
make cov        # coverage report
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the module map, request
flow, and the core domain state machines. The HTTP surface is catalogued in
[docs/api.md](docs/api.md).

## License

MIT — see [LICENSE](LICENSE).
