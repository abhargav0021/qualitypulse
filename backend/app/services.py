from __future__ import annotations

from typing import Any

from backend.app.repositories import DefectRepository, TestCaseRepository


class QualityService:
    test_statuses = ("not_started", "in_progress", "passed", "failed", "blocked")
    defect_statuses = ("open", "triaged", "fixed", "closed")

    def __init__(
        self,
        test_cases: TestCaseRepository,
        defects: DefectRepository,
    ) -> None:
        self.test_cases = test_cases
        self.defects = defects

    def create_test_case(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._normalize_booleans(self.test_cases.create(payload))

    def list_test_cases(self) -> list[dict[str, Any]]:
        return [self._normalize_booleans(test_case) for test_case in self.test_cases.list_all()]

    def update_test_status(self, test_case_id: int, status: str) -> dict[str, Any] | None:
        if status not in self.test_statuses:
            return None
        updated = self.test_cases.update_status(test_case_id, status)
        return self._normalize_booleans(updated) if updated else None

    def create_defect(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        linked_test_case_id = payload.get("linked_test_case_id")
        if linked_test_case_id and not self.test_cases.get(linked_test_case_id):
            return None
        return self.defects.create(payload)

    def list_defects(self) -> list[dict[str, Any]]:
        return self.defects.list_all()

    def update_defect_status(self, defect_id: int, status: str) -> dict[str, Any] | None:
        if status not in self.defect_statuses:
            return None
        return self.defects.update_status(defect_id, status)

    def summary(self) -> dict[str, Any]:
        test_cases = self.list_test_cases()
        defects = self.list_defects()

        test_counts = {status: 0 for status in self.test_statuses}
        severity_counts = {"minor": 0, "major": 0, "critical": 0}
        open_defect_statuses = {"open", "triaged"}

        for test_case in test_cases:
            test_counts[test_case["status"]] += 1

        for defect in defects:
            severity_counts[defect["severity"]] += 1

        automated_count = sum(1 for test_case in test_cases if test_case["automated"])
        total_tests = len(test_cases)
        active_defects = [defect for defect in defects if defect["status"] in open_defect_statuses]
        high_risk_defects = [
            defect for defect in active_defects if defect["severity"] in {"major", "critical"}
        ]
        touched_modules = {test_case["module"] for test_case in test_cases}

        release_score = max(
            0,
            100
            - (test_counts["failed"] * 15)
            - (test_counts["blocked"] * 12)
            - (len(high_risk_defects) * 10),
        )

        return {
            "total_test_cases": total_tests,
            "total_defects": len(defects),
            "active_defects": len(active_defects),
            "automation_coverage": round((automated_count / total_tests) * 100, 1)
            if total_tests
            else 0,
            "release_readiness_score": release_score,
            "modules_under_test": sorted(touched_modules),
            "test_counts": test_counts,
            "severity_counts": severity_counts,
        }

    def _normalize_booleans(self, test_case: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(test_case)
        normalized["automated"] = bool(normalized["automated"])
        return normalized

