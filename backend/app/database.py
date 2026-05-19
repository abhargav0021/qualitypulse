from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterable


class Database:
    """Small SQLite helper that keeps SQL visible for interview review."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    module TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'not_started',
                    automated INTEGER NOT NULL DEFAULT 0,
                    expected_result TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS defects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    linked_test_case_id INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (linked_test_case_id) REFERENCES test_cases(id)
                );
                """
            )

    def seed(self) -> None:
        if self.fetch_one("SELECT COUNT(*) AS count FROM test_cases")["count"] > 0:
            return

        test_cases = [
            (
                "Validate AI quality report upload",
                "Reports",
                "high",
                "Bhargav",
                "passed",
                1,
                "The report is uploaded and parsed without data loss.",
            ),
            (
                "Verify defect creation from failed test",
                "Defects",
                "high",
                "Bhargav",
                "in_progress",
                0,
                "A failed test can be converted into a tracked defect.",
            ),
            (
                "Confirm dashboard release readiness score",
                "Dashboard",
                "medium",
                "QA Lead",
                "not_started",
                1,
                "The dashboard shows stable counts and coverage metrics.",
            ),
        ]

        for test_case in test_cases:
            self.execute_write(
                """
                INSERT INTO test_cases
                    (title, module, priority, owner, status, automated, expected_result)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                test_case,
            )

        self.execute_write(
            """
            INSERT INTO defects (title, severity, status, linked_test_case_id)
            VALUES (?, ?, ?, ?)
            """,
            ("Upload parser rejects large JSON payload", "critical", "open", 1),
        )

    def fetch_all(self, query: str, parameters: Iterable[Any] = ()) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(query, tuple(parameters)).fetchall()
        return [dict(row) for row in rows]

    def fetch_one(self, query: str, parameters: Iterable[Any] = ()) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(query, tuple(parameters)).fetchone()
        return dict(row) if row else None

    def execute_write(self, query: str, parameters: Iterable[Any] = ()) -> int:
        with self._lock, self._connect() as connection:
            cursor = connection.execute(query, tuple(parameters))
            connection.commit()
            return int(cursor.lastrowid or cursor.rowcount)

