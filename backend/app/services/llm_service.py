from __future__ import annotations

from openai import OpenAI


class LLMService:
    def __init__(self, *, api_key: str, model: str, enable_live_llm: bool = True) -> None:
        self.api_key = api_key.strip()
        self.model = model
        self.enable_live_llm = enable_live_llm
        self.client: OpenAI | None = None
        if self.enable_live_llm and self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def available(self) -> bool:
        return self.client is not None

    def draft_answer(self, question: str, context_blocks: list[str]) -> str:
        if not self.client:
            return self._fallback(question, context_blocks)

        context = "\n\n".join(context_blocks)
        prompt = (
            "You are a SaaS support knowledge assistant. "
            "Answer using only the provided context. "
            "If context is insufficient, clearly say so."
        )
        try:
            resp = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": f"Question:\n{question}\n\nContext:\n{context}",
                    },
                ],
                temperature=0.2,
            )
            # OpenAI Python SDK exposes convenience property for aggregated text.
            text = getattr(resp, "output_text", "") or ""
            return text.strip() if text.strip() else self._fallback(question, context_blocks)
        except Exception:
            return self._fallback(question, context_blocks)

    @staticmethod
    def _fallback(question: str, context_blocks: list[str]) -> str:
        if not context_blocks:
            return (
                "I could not find enough information in the current knowledge base to answer this question."
            )
        return (
            "Based on the knowledge base, here is the best answer:\n\n"
            f"{context_blocks[0][:650]}"
        )

