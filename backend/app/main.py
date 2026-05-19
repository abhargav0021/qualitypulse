from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.database import Database
from backend.app.repositories import DefectRepository, TestCaseRepository
from backend.app.schemas import (
    DefectCreate,
    DefectStatusUpdate,
    TestCaseCreate,
    TestCaseStatusUpdate,
)
from backend.app.services import QualityService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DEFAULT_DB_PATH = PROJECT_ROOT / "backend" / "qualitypulse.db"


def create_app(database_path: str | Path | None = None, seed_data: bool = True) -> FastAPI:
    database = Database(database_path or os.getenv("DB_PATH", DEFAULT_DB_PATH))
    database.initialize()
    if seed_data:
        database.seed()

    service = QualityService(TestCaseRepository(database), DefectRepository(database))
    app = FastAPI(
        title="QualityPulse API",
        description="A QA dashboard API built with Python, FastAPI, SQLite, and JSON.",
        version="1.0.0",
    )
    app.state.service = service

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "qualitypulse"}

    @app.get("/api/test-cases")
    def list_test_cases() -> list[dict[str, Any]]:
        return service.list_test_cases()

    @app.post("/api/test-cases", status_code=201)
    def create_test_case(payload: TestCaseCreate) -> dict[str, Any]:
        return service.create_test_case(payload.model_dump())

    @app.put("/api/test-cases/{test_case_id}/status")
    def update_test_case_status(
        test_case_id: int, payload: TestCaseStatusUpdate
    ) -> dict[str, Any]:
        updated = service.update_test_status(test_case_id, payload.status)
        if not updated:
            raise HTTPException(status_code=404, detail="Test case not found")
        return updated

    @app.get("/api/defects")
    def list_defects() -> list[dict[str, Any]]:
        return service.list_defects()

    @app.post("/api/defects", status_code=201)
    def create_defect(payload: DefectCreate) -> dict[str, Any]:
        created = service.create_defect(payload.model_dump())
        if not created:
            raise HTTPException(status_code=404, detail="Linked test case not found")
        return created

    @app.put("/api/defects/{defect_id}/status")
    def update_defect_status(defect_id: int, payload: DefectStatusUpdate) -> dict[str, Any]:
        updated = service.update_defect_status(defect_id, payload.status)
        if not updated:
            raise HTTPException(status_code=404, detail="Defect not found")
        return updated

    @app.get("/api/summary")
    def summary() -> dict[str, Any]:
        return service.summary()

    return app


app = create_app()

