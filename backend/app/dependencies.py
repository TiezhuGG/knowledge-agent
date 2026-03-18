from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.services.agent_service import AgentService
from app.services.eval_service import EvalService
from app.services.knowledge_base import KnowledgeBaseService
from app.services.llm_service import LLMService
from app.services.ticket_tool import TicketTool
from app.services.trace_store import TraceStore
from app.services.vector_store import VectorStore


@lru_cache(maxsize=1)
def get_trace_store() -> TraceStore:
    return TraceStore()


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    return VectorStore()


@lru_cache(maxsize=1)
def get_knowledge_service() -> KnowledgeBaseService:
    settings = get_settings()
    return KnowledgeBaseService(max_chunk_chars=settings.max_chunk_chars)


@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    settings = get_settings()
    return LLMService(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        enable_live_llm=settings.enable_live_llm,
    )


@lru_cache(maxsize=1)
def get_ticket_tool() -> TicketTool:
    return TicketTool()


@lru_cache(maxsize=1)
def get_agent_service() -> AgentService:
    settings = get_settings()
    return AgentService(
        vector_store=get_vector_store(),
        trace_store=get_trace_store(),
        llm_service=get_llm_service(),
        ticket_tool=get_ticket_tool(),
        top_k_chunks=settings.top_k_chunks,
    )


@lru_cache(maxsize=1)
def get_eval_service() -> EvalService:
    return EvalService(agent_service=get_agent_service())

