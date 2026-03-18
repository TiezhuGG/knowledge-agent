from __future__ import annotations

from time import perf_counter

from app.models import ChatRequest, ChatResponse, Citation
from app.services.llm_service import LLMService
from app.services.ticket_tool import TicketTool
from app.services.trace_store import TraceStore
from app.services.vector_store import VectorStore


class AgentService:
    def __init__(
        self,
        *,
        vector_store: VectorStore,
        trace_store: TraceStore,
        llm_service: LLMService,
        ticket_tool: TicketTool,
        top_k_chunks: int = 4,
    ) -> None:
        self.vector_store = vector_store
        self.trace_store = trace_store
        self.llm_service = llm_service
        self.ticket_tool = ticket_tool
        self.top_k_chunks = top_k_chunks

    def answer(self, req: ChatRequest) -> ChatResponse:
        trace_id = self.trace_store.new_trace_id()

        start = perf_counter()
        route = self._route(req.question)
        self.trace_store.add_event(
            trace_id,
            step="router",
            status="ok",
            latency_ms=int((perf_counter() - start) * 1000),
            detail=route,
        )

        retrieve_start = perf_counter()
        results = self.vector_store.search(req.question, top_k=self.top_k_chunks)
        retrieval_ms = int((perf_counter() - retrieve_start) * 1000)
        self.trace_store.add_event(
            trace_id,
            step="retrieve",
            status="ok",
            latency_ms=retrieval_ms,
            detail=f"hits={len(results)}",
        )

        if not results:
            ticket = self.ticket_tool.create_ticket(req.question, req.customer_tier)
            self.trace_store.add_event(
                trace_id,
                step="escalate",
                status="ok",
                latency_ms=5,
                tool_name="ticket_tool",
                detail=ticket.ticket_id,
            )
            return ChatResponse(
                answer=(
                    "I could not find a grounded answer in the current knowledge base. "
                    f"I opened a support escalation suggestion: `{ticket.ticket_id}` in `{ticket.queue}`."
                ),
                citations=[],
                confidence=0.2,
                trace_id=trace_id,
                suggested_action="open_ticket",
            )

        context_blocks = [chunk.text for chunk, _score in results]
        llm_start = perf_counter()
        answer = self.llm_service.draft_answer(req.question, context_blocks)
        llm_ms = int((perf_counter() - llm_start) * 1000)
        self.trace_store.add_event(
            trace_id,
            step="synthesize",
            status="ok",
            latency_ms=llm_ms,
            detail="llm" if self.llm_service.available() else "fallback",
        )

        citations = [
            Citation(
                doc_id=chunk.doc_id,
                source=chunk.source,
                chunk_id=chunk.id,
                quote=chunk.text[:220],
            )
            for chunk, _score in results
        ]
        confidence = max(min(sum(score for _chunk, score in results) / len(results), 1.0), 0.3)
        return ChatResponse(
            answer=answer,
            citations=citations,
            confidence=round(confidence, 2),
            trace_id=trace_id,
            suggested_action="none",
        )

    @staticmethod
    def _route(question: str) -> str:
        lower = question.lower()
        troubleshooting_signals = ["error", "failed", "issue", "not working", "bug", "timeout"]
        if any(signal in lower for signal in troubleshooting_signals):
            return "troubleshooting"
        return "faq"

