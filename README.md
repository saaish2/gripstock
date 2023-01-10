# Gripstock

Gripstock is an equipment-rental operations platform for **film & video
production rental houses**. It tracks gear inventory, reserves it for shoots,
checks it out and back in with condition inspections, prices and invoices the
rental, and handles damage, maintenance, and late fees — the day-to-day
machinery of a busy rental counter.

It is a FastAPI service backed by SQLAlchemy and Alembic, organised into clean
layers (routers → services → repositories → models) so business rules live in
one place and stay testable.

