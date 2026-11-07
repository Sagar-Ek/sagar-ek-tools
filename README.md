# Sagar EK Tools

A full-stack project consisting of a **FastAPI** backend, a **Next.js** frontend, and a **PostgreSQL** database.

## Directory Structure

```text
sagar-ek-tools/
├── backend/            # FastAPI (Python, Pydantic v2, pytest)
├── frontend/           # Next.js (App Router, React, TypeScript, Tailwind CSS)
├── docker-compose.yml  # Multi-container orchestration (FastAPI + Next.js + PostgreSQL)
└── .env.example        # Docker Compose environment template
```

## Quick Start with Docker Compose

Run all three services (FastAPI, Next.js, and PostgreSQL) together:

```bash
# 1. (Optional) Copy environment template
cp .env.example .env

# 2. Build and start all services
docker compose up -d --build
```

### Services & URLs

| Service | Technology | URL / Port |
| :--- | :--- | :--- |
| **Frontend** | Next.js (Hot Reload) | [http://localhost:3000/](http://localhost:3000/) |
| **Backend** | FastAPI (Hot Reload) | [http://localhost:8000/](http://localhost:8000/) |
| **Swagger Docs** | OpenAPI UI | [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs) |
| **Database** | PostgreSQL 17 | `localhost:5432` (`sagar_ek_tools`) |

### Stop Containers

```bash
docker compose down
# To also delete database volumes:
# docker compose down -v
```

---

## Local Development (Without Docker)

### 1. Backend (FastAPI)

```bash
cd backend
source .venv/bin/activate
fastapi dev app/main.py
# or: uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (Next.js)

```bash
cd frontend
npm run dev
```
