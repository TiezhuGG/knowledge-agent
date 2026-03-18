# SaaS Knowledge Agent MVP

Resume-ready AI Agent project built from scratch with Python + React.

## What is implemented

- `POST /api/knowledge/ingest`: ingest FAQ or troubleshooting docs.
- `POST /api/chat`: answer questions with citations, confidence, and trace id.
- `POST /api/evals/run`: run a built-in eval suite.
- `GET /api/traces/{trace_id}`: inspect routing/retrieval/synthesis/tool events.
- React demo UI for ingesting docs, chatting, viewing citations/traces, and running evals.
- Docker Compose for local one-command startup.

## Architecture (MVP)

- Backend: `FastAPI`
- Agent orchestration: custom service + OpenAI Responses API (optional, fallback enabled)
- Retrieval: in-memory lexical vector-store replacement for demo
- Tooling: mock ticket escalation tool (MCP-like external tool integration point)
- Frontend: React + Vite

## Step-by-step: run locally

1. Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

2. Optional: set OpenAI key in `backend/.env`

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

3. Start backend

```bash
uvicorn app.main:app --reload --port 8000
```

4. Start frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

5. Open UI: `http://localhost:5173`

## Docker quickstart

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend API docs: `http://localhost:8000/docs`

## API examples

1. Ingest

```bash
curl -X POST http://localhost:8000/api/knowledge/ingest ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"kb://faq/auth.md\",\"content\":\"Password reset: use forgot password.\"}"
```

2. Chat

```bash
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\":\"demo-1\",\"question\":\"How to reset password?\",\"customer_tier\":\"pro\"}"
```

3. Evals

```bash
curl -X POST http://localhost:8000/api/evals/run ^
  -H "Content-Type: application/json" ^
  -d "{\"eval_suite_id\":\"default\"}"
```

## Resume bullets (you can paste and edit)

- Built a production-style SaaS support **AI Agent** with FastAPI + React, including doc ingestion, grounded Q&A with citations, and confidence scoring.
- Implemented tool-augmented agent workflow (route -> retrieve -> synthesize -> escalate) with trace-level observability for each request.
- Added automated evaluation pipeline for answer accuracy, groundedness, and tool success rate, enabling measurable quality iteration.
- Containerized full stack with Docker Compose for reproducible local and cloud deployment.

## Suggested next upgrades

1. Replace lexical retrieval with Qdrant + embeddings.
2. Replace mock ticket tool with real MCP server integration.
3. Add persistent storage (Postgres) for docs/sessions/traces.
4. Expand eval dataset to 100+ cases and add regression gating in CI.
