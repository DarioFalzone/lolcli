import logging
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

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
    return datetime.utcnow().isoformat()


def output_file(filename: str) -> Path:
    return OUTPUT_DIR / filename
