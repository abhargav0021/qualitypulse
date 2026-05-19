# QualityPulse

QualityPulse is a full stack quality engineering dashboard built for a Python Developer role. It demonstrates the essential technologies from the Qualitest job description: Python 3, FastAPI, REST APIs, JSON, SQLite, SQL fundamentals, object-oriented code, HTML/CSS/JavaScript, Git-friendly project structure, unit tests, virtual environments, and Docker.

## Why This Project Fits The Role

- **Python 3.x:** backend written in modern Python with type hints.
- **FastAPI framework:** REST API with automatic OpenAPI docs at `/docs`.
- **Core programming concepts:** functions, modules, classes, inheritance, control flow, and typed data models.
- **Data structures:** lists, dictionaries, tuples, and sets are used in service logic.
- **REST and JSON:** CRUD-style endpoints return JSON and accept JSON payloads.
- **Database:** SQLite persistence with explicit `SELECT`, `INSERT`, and `UPDATE` statements.
- **Unit tests:** API tests use `pytest` and FastAPI's test client.
- **Frontend:** responsive HTML, CSS, and JavaScript consuming the backend API.
- **Docker/venv ready:** includes a `Dockerfile` and local setup instructions.

## Product Story

The app is a small Quality Engineering control center for tracking test cases, defects, automation coverage, and release readiness. It is intentionally aligned with a QA services company: the reviewer can see how backend APIs, database state, and frontend workflows connect around testing work.

## Tech Stack

- Python 3.12
- FastAPI
- SQLite
- Pydantic
- Pytest
- HTML, CSS, JavaScript
- Docker

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Open:

- App: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`

## Run Tests

```bash
pytest
```

## Run With Docker

```bash
docker build -t qualitypulse .
docker run -p 8000:8000 qualitypulse
```

## API Highlights

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/test-cases` | List test cases |
| `POST` | `/api/test-cases` | Create a test case |
| `PUT` | `/api/test-cases/{id}/status` | Update test status |
| `GET` | `/api/defects` | List defects |
| `POST` | `/api/defects` | Create a defect |
| `PUT` | `/api/defects/{id}/status` | Update defect status |
| `GET` | `/api/summary` | Dashboard metrics |

## Interview Talking Points

1. I used FastAPI to expose typed REST endpoints and automatic documentation.
2. I separated API routes, schemas, repositories, database access, and service logic to keep the code maintainable.
3. I used SQLite directly so the SQL fundamentals are visible instead of hidden behind an ORM.
4. I wrote unit tests around the API contract and used temporary databases for test isolation.
5. I built the frontend with plain JavaScript so the reviewer can see the JSON API integration clearly.

