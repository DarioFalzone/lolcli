import logging
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from riot_lol_cli.database.models import DatabaseManager
from riot_lol_cli.paths import OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("riot_lol_cli.meta_api")
db = DatabaseManager()


@contextmanager
def session_scope() -> Iterator:
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def output_file(filename: str) -> Path:
    return OUTPUT_DIR / filename
