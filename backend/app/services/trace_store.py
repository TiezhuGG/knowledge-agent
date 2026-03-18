from __future__ import annotations

from collections import defaultdict
from typing import Any
from uuid import uuid4

from app.models import TraceEvent


class TraceStore:
    def __init__(self) -> None:
        self._events: dict[str, list[TraceEvent]] = defaultdict(list)

    def new_trace_id(self) -> str:
        return f"trace-{uuid4().hex[:12]}"

    def add_event(
        self,
        trace_id: str,
        *,
        step: str,
        status: str,
        latency_ms: int,
        tool_name: str | None = None,
        detail: str | None = None,
    ) -> None:
        self._events[trace_id].append(
            TraceEvent(
                trace_id=trace_id,
                step=step,
                status=status,
                latency_ms=latency_ms,
                tool_name=tool_name,
                detail=detail,
            )
        )

    def get_trace(self, trace_id: str) -> list[dict[str, Any]]:
        return [event.model_dump() for event in self._events.get(trace_id, [])]

