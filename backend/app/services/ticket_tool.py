from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass
class TicketResult:
    ticket_id: str
    queue: str
    summary: str


class TicketTool:
    """Mock MCP-like ticket escalation tool."""

    def create_ticket(self, question: str, customer_tier: str) -> TicketResult:
        queue = "enterprise-support" if customer_tier == "enterprise" else "general-support"
        return TicketResult(
            ticket_id=f"TKT-{uuid4().hex[:8].upper()}",
            queue=queue,
            summary=question[:180],
        )

