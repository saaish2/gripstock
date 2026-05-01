"""Command-line entry point for operational tasks.

Usage::

    gripstock initdb            # create tables from ORM metadata
    gripstock seed              # load demo data
    gripstock sweep             # run overdue + late-fee sweeps once
    gripstock dispatch-webhooks # flush pending webhook deliveries
"""

from __future__ import annotations

import argparse
import sys

from app.bootstrap import create_all
from app.database import session_scope
from app.workers.sweeps import run_all
from app.workers.webhook_dispatcher import dispatch_due


def _cmd_initdb(_: argparse.Namespace) -> int:
    create_all()
    print("database schema created")
    return 0


def _cmd_seed(_: argparse.Namespace) -> int:
    from scripts.seed import seed_all

    with session_scope() as session:
        summary = seed_all(session)
    print(f"seeded: {summary}")
    return 0


def _cmd_sweep(_: argparse.Namespace) -> int:
    with session_scope() as session:
        result = run_all(session)
    print(f"sweeps complete: {result}")
    return 0
