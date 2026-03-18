from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class IngestRequest(BaseModel):
    source: str = Field(..., examples=["kb://faq/billing.md"])
    content: str = Field(..., min_length=1)


class IngestResponse(BaseModel):
    doc_id: str
    chunk_count: int
    status: str = "ok"


class Citation(BaseModel):
    doc_id: str
    source: str
    chunk_id: str
    quote: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., examples=["session-demo-1"])
    question: str = Field(..., min_length=1)
    customer_tier: Literal["free", "pro", "enterprise"] = "free"


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float = Field(..., ge=0, le=1)
    trace_id: str
    suggested_action: Literal["none", "open_ticket"] = "none"


class EvalRunRequest(BaseModel):
    eval_suite_id: str = Field(default="default")


class EvalMetrics(BaseModel):
    accuracy: float
    groundedness: float
    tool_success_rate: float
    total_cases: int
    passed_cases: int


class EvalRunResponse(BaseModel):
    eval_suite_id: str
    metrics: EvalMetrics
    report_url: str


class DocChunk(BaseModel):
    id: str
    doc_id: str
    source: str
    text: str
    tokens: set[str]

    @classmethod
    def from_text(cls, doc_id: str, source: str, text: str) -> "DocChunk":
        cleaned = text.strip()
        words = {w.strip(".,!?;:()[]{}<>\"'").lower() for w in cleaned.split() if w.strip()}
        words.discard("")
        return cls(
            id=f"chunk-{uuid4().hex[:12]}",
            doc_id=doc_id,
            source=source,
            text=cleaned,
            tokens=words,
        )


class TraceEvent(BaseModel):
    trace_id: str
    step: str
    status: Literal["ok", "error"]
    latency_ms: int
    tool_name: str | None = None
    detail: str | None = None
    timestamp: str = Field(default_factory=utc_now_iso)

