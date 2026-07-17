"""SQLite-backed memory store for user interaction history and preference summaries."""

import json
import sqlite3
from datetime import datetime, timezone


class MemoryStore:
    """
    Wraps a SQLite database holding:
      - episodic memory: raw interaction history per user
      - long-term memory: rolling preference summary per user
    """

    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                clicked INTEGER NOT NULL,
                dwell_time REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions (user_id)"
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS summaries (
                user_id TEXT PRIMARY KEY,
                summary TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def log_interaction(self, user_id, item_id, clicked, dwell_time):
        self.conn.execute(
            "INSERT INTO interactions (user_id, item_id, clicked, dwell_time, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, item_id, int(bool(clicked)), dwell_time, datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()

    def get_history(self, user_id):
        rows = self.conn.execute(
            "SELECT item_id, clicked, dwell_time, timestamp FROM interactions "
            "WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
        return [
            {
                "item_id": row["item_id"],
                "clicked": bool(row["clicked"]),
                "dwell_time": row["dwell_time"],
                "timestamp": row["timestamp"],
            }
            for row in rows
        ]

    def update_summary(self, user_id, summary):
        self.conn.execute(
            "INSERT INTO summaries (user_id, summary, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET summary = excluded.summary, "
            "updated_at = excluded.updated_at",
            (user_id, json.dumps(summary), datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()

    def get_summary(self, user_id):
        row = self.conn.execute(
            "SELECT summary FROM summaries WHERE user_id = ?", (user_id,)
        ).fetchone()
        return json.loads(row["summary"]) if row else None

    def close(self):
        self.conn.close()
