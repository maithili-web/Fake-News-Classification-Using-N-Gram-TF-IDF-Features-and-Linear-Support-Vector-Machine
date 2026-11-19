"""SQLite storage for the check history."""
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / 'data' / 'history.db'


def _connect():
    connection = sqlite3.connect(os.environ.get('FAKE_NEWS_DB', DEFAULT_PATH))
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with closing(_connect()) as db, db:
        db.execute("""CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            headline TEXT NOT NULL,
            label TEXT NOT NULL,
            margin REAL NOT NULL)""")


def add_check(headline, label, margin):
    created_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with closing(_connect()) as db, db:
        db.execute('INSERT INTO checks (created_at, headline, label, margin) VALUES (?, ?, ?, ?)',
                   (created_at, headline, label, margin))


def list_checks(limit):
    with closing(_connect()) as db:
        rows = db.execute('SELECT * FROM checks ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    return [dict(row) for row in rows]


def clear_checks():
    with closing(_connect()) as db, db:
        db.execute('DELETE FROM checks')
