from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Priority = Literal["low", "medium", "high"]
TestStatus = Literal["not_started", "in_progress", "passed", "failed", "blocked"]
Severity = Literal["minor", "major", "critical"]
DefectStatus = Literal["open", "triaged", "fixed", "closed"]


class TestCaseCreate(BaseModel):
    title: str = Field(min_length=4, max_length=120)
    module: str = Field(min_length=2, max_length=60)
    priority: Priority = "medium"
    owner: str = Field(min_length=2, max_length=60)
    automated: bool = False
    expected_result: str = Field(min_length=8, max_length=300)


class TestCaseStatusUpdate(BaseModel):
    status: TestStatus


class DefectCreate(BaseModel):
    title: str = Field(min_length=4, max_length=140)
    severity: Severity = "major"
    linked_test_case_id: int | None = None


class DefectStatusUpdate(BaseModel):
    status: DefectStatus

