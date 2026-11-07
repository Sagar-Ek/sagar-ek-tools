# FastAPI Backend

Standard FastAPI backend application for `sagar-ek-tools`.

## Directory Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py
│   │       │   └── items.py
│   │       └── router.py
│   ├── core/
│   │   └── config.py
│   ├── schemas/
│   │   ├── health.py
│   │   └── item.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   └── test_items.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Setup & Running

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. Run Development Server

```bash
fastapi dev app/main.py
# or
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- Root: [http://localhost:8000/](http://localhost:8000/)
- Swagger UI (Docs): [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- ReDoc: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 3. Run Tests

```bash
pytest
```
