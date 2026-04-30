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
