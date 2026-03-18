from __future__ import annotations

from dataclasses import dataclass

from app.models import ChatRequest, EvalMetrics
from app.services.agent_service import AgentService


@dataclass
class EvalCase:
    query: str
    expected_keywords: list[str]
    must_cite: bool = True


class EvalService:
    def __init__(self, *, agent_service: AgentService) -> None:
        self.agent_service = agent_service
        self._suites = {
            "default": [
                EvalCase(
                    query="How do I reset my password?",
                    expected_keywords=["reset", "password"],
                ),
                EvalCase(
                    query="The API returns timeout error, what should I do?",
                    expected_keywords=["timeout", "retry"],
                ),
                EvalCase(
                    query="Do you support SSO in pro plan?",
                    expected_keywords=["sso", "plan"],
                ),
            ]
        }

    def run(self, suite_id: str) -> EvalMetrics:
        cases = self._suites.get(suite_id, self._suites["default"])
        passed = 0
        grounded = 0
        tool_success = 0
        for idx, case in enumerate(cases):
            req = ChatRequest(
                session_id=f"eval-{suite_id}-{idx}",
                question=case.query,
                customer_tier="pro",
            )
            resp = self.agent_service.answer(req)
            answer_lower = resp.answer.lower()
            if any(token in answer_lower for token in case.expected_keywords):
                passed += 1
            if not case.must_cite or len(resp.citations) > 0:
                grounded += 1
            if resp.suggested_action in {"none", "open_ticket"}:
                tool_success += 1

        total = len(cases)
        return EvalMetrics(
            accuracy=round(passed / total if total else 0.0, 2),
            groundedness=round(grounded / total if total else 0.0, 2),
            tool_success_rate=round(tool_success / total if total else 0.0, 2),
            total_cases=total,
            passed_cases=passed,
        )

