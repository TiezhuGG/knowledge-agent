from __future__ import annotations

from collections.abc import Iterable

from app.models import DocChunk


class VectorStore:
    """In-memory lexical retrieval for MVP."""

    def __init__(self) -> None:
        self._chunks: list[DocChunk] = []

    def add_chunks(self, chunks: Iterable[DocChunk]) -> int:
        chunk_list = list(chunks)
        self._chunks.extend(chunk_list)
        return len(chunk_list)

    def search(self, query: str, *, top_k: int = 4) -> list[tuple[DocChunk, float]]:
        query_tokens = {
            token.strip(".,!?;:()[]{}<>\"'").lower()
            for token in query.split()
            if token.strip()
        }
        if not query_tokens:
            return []

        scored: list[tuple[DocChunk, float]] = []
        for chunk in self._chunks:
            overlap = len(query_tokens.intersection(chunk.tokens))
            if overlap == 0:
                continue
            score = overlap / max(len(query_tokens), 1)
            scored.append((chunk, min(score, 1.0)))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

    def has_data(self) -> bool:
        return len(self._chunks) > 0

