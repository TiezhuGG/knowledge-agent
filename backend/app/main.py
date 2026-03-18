from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies import (
    get_agent_service,
    get_eval_service,
    get_knowledge_service,
    get_trace_store,
    get_vector_store,
)
from app.models import (
    ChatRequest,
    ChatResponse,
    EvalRunRequest,
    EvalRunResponse,
    IngestRequest,
    IngestResponse,
)
from app.services.agent_service import AgentService
from app.services.eval_service import EvalService
from app.services.knowledge_base import KnowledgeBaseService
from app.services.trace_store import TraceStore
from app.services.vector_store import VectorStore

settings = get_settings()
app = FastAPI(title=settings.app_name)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/knowledge/ingest", response_model=IngestResponse)
def ingest_knowledge(
    payload: IngestRequest,
    knowledge_service: KnowledgeBaseService = Depends(get_knowledge_service),
    vector_store: VectorStore = Depends(get_vector_store),
) -> IngestResponse:
    doc_id, chunks = knowledge_service.ingest(payload.source, payload.content)
    inserted = vector_store.add_chunks(chunks)
    return IngestResponse(doc_id=doc_id, chunk_count=inserted, status="ok")


@app.post("/api/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service),
    vector_store: VectorStore = Depends(get_vector_store),
) -> ChatResponse:
    if not vector_store.has_data():
        raise HTTPException(
            status_code=400,
            detail="Knowledge base is empty. Ingest at least one document first.",
        )
    return agent_service.answer(payload)


@app.post("/api/evals/run", response_model=EvalRunResponse)
def run_evals(
    payload: EvalRunRequest,
    eval_service: EvalService = Depends(get_eval_service),
) -> EvalRunResponse:
    metrics = eval_service.run(payload.eval_suite_id)
    report_url = f"/reports/evals/{payload.eval_suite_id}.json"
    return EvalRunResponse(
        eval_suite_id=payload.eval_suite_id,
        metrics=metrics,
        report_url=report_url,
    )


@app.get("/api/traces/{trace_id}")
def get_trace(trace_id: str, trace_store: TraceStore = Depends(get_trace_store)) -> dict:
    events = trace_store.get_trace(trace_id)
    if not events:
        raise HTTPException(status_code=404, detail="Trace not found")
    return {"trace_id": trace_id, "events": events}

