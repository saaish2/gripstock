"""Gripstock — equipment-rental operations platform.

The package is organised into thin layers:

* ``app.models``        SQLAlchemy ORM entities
* ``app.schemas``       Pydantic request/response models
* ``app.repositories``  data-access objects wrapping the ORM
* ``app.services``      business logic and invariants
* ``app.routers``       FastAPI endpoint groups
* ``app.workers``       background sweeps (overdue, late fees, webhooks)
"""

__version__ = "1.5.0"
