# Agent System

Frontend (React + Vite + TS) and backend (FastAPI + agent-framework) for a
supervisor-agent chat system.

```
agent-app/
├── backend/   # FastAPI + Microsoft Agent Framework
└── frontend/  # React 18 + TypeScript + Vite
```

## Backend (Python 3.12)

```bash
cd agent-app/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in AZURE_OPENAI_* values
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Backend tests

```bash
cd agent-app/backend
pytest
```

External LLM calls are mocked via FastAPI dependency overrides, so tests
run without Azure OpenAI credentials.

## Frontend

```bash
cd agent-app/frontend
npm install
npm run dev          # http://localhost:5173
```

### Frontend tests

```bash
cd agent-app/frontend
npm test
```

API requests are mocked with MSW.

## Configuration

Backend reads `AZURE_OPENAI_KEY`, `AZURE_OPENAI_ENDPOINT`, and
`AZURE_OPENAI_DEPLOYMENT` from `agent-app/backend/.env`.

The frontend defaults to `http://localhost:8000` for the backend; override it
on the **Settings** page or by setting `VITE_API_BASE` at build time.
