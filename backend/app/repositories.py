from __future__ import annotations

from abc import ABC
from typing import Any

from backend.app.database import Database


class BaseRepository(ABC):
    def __init__(self, database: Database) -> None:
        self.database = database


class TestCaseRepository(BaseRepository):
    def list_all(self) -> list[dict[str, Any]]:
        return self.database.fetch_all(
            """
            SELECT id, title, module, priority, owner, status, automated,
                   expected_result, created_at
            FROM test_cases
            ORDER BY created_at DESC, id DESC
            """
        )

    def get(self, test_case_id: int) -> dict[str, Any] | None:
        return self.database.fetch_one(
            """
            SELECT id, title, module, priority, owner, status, automated,
                   expected_result, created_at
            FROM test_cases
            WHERE id = ?
            """,
            (test_case_id,),
        )

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        new_id = self.database.execute_write(
            """
            INSERT INTO test_cases
                (title, module, priority, owner, automated, expected_result)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload["title"],
                payload["module"],
                payload["priority"],
                payload["owner"],
                int(payload["automated"]),
                payload["expected_result"],
            ),
        )
        return self.get(new_id) or {}

    def update_status(self, test_case_id: int, status: str) -> dict[str, Any] | None:
        self.database.execute_write(
            """
            UPDATE test_cases
            SET status = ?
            WHERE id = ?
            """,
            (status, test_case_id),
        )
        return self.get(test_case_id)


class DefectRepository(BaseRepository):
    def list_all(self) -> list[dict[str, Any]]:
        return self.database.fetch_all(
            """
            SELECT defects.id, defects.title, defects.severity, defects.status,
                   defects.linked_test_case_id, defects.created_at,
                   test_cases.title AS linked_test_case_title
            FROM defects
            LEFT JOIN test_cases ON test_cases.id = defects.linked_test_case_id
            ORDER BY defects.created_at DESC, defects.id DESC
            """
        )

    def get(self, defect_id: int) -> dict[str, Any] | None:
        return self.database.fetch_one(
            """
            SELECT defects.id, defects.title, defects.severity, defects.status,
                   defects.linked_test_case_id, defects.created_at,
                   test_cases.title AS linked_test_case_title
            FROM defects
            LEFT JOIN test_cases ON test_cases.id = defects.linked_test_case_id
            WHERE defects.id = ?
            """,
            (defect_id,),
        )

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        new_id = self.database.execute_write(
            """
            INSERT INTO defects (title, severity, linked_test_case_id)
            VALUES (?, ?, ?)
            """,
            (payload["title"], payload["severity"], payload.get("linked_test_case_id")),
        )
        return self.get(new_id) or {}

    def update_status(self, defect_id: int, status: str) -> dict[str, Any] | None:
        self.database.execute_write(
            """
            UPDATE defects
            SET status = ?
            WHERE id = ?
            """,
            (status, defect_id),
        )
        return self.get(defect_id)

