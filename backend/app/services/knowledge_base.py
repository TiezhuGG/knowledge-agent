from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.models import DocChunk


@dataclass
class KnowledgeDoc:
    id: str
    source: str
    content: str


class KnowledgeBaseService:
    def __init__(self, *, max_chunk_chars: int = 800) -> None:
        self.max_chunk_chars = max_chunk_chars
        self._docs: dict[str, KnowledgeDoc] = {}

    def ingest(self, source: str, content: str) -> tuple[str, list[DocChunk]]:
        doc_id = f"doc-{uuid4().hex[:10]}"
        doc = KnowledgeDoc(id=doc_id, source=source, content=content.strip())
        self._docs[doc_id] = doc
        chunks = self._chunk_doc(doc)
        return doc_id, chunks

    def get_doc_count(self) -> int:
        return len(self._docs)

    def _chunk_doc(self, doc: KnowledgeDoc) -> list[DocChunk]:
        raw_blocks = [block.strip() for block in doc.content.split("\n\n") if block.strip()]
        if not raw_blocks:
            raw_blocks = [doc.content.strip()]

        chunks: list[DocChunk] = []
        buffer = ""
        for block in raw_blocks:
            candidate = f"{buffer}\n\n{block}".strip() if buffer else block
            if len(candidate) <= self.max_chunk_chars:
                buffer = candidate
                continue
            if buffer:
                chunks.append(DocChunk.from_text(doc.id, doc.source, buffer))
                buffer = block
            else:
                # Hard split for very long single paragraph.
                cursor = 0
                while cursor < len(block):
                    piece = block[cursor : cursor + self.max_chunk_chars]
                    chunks.append(DocChunk.from_text(doc.id, doc.source, piece))
                    cursor += self.max_chunk_chars
                buffer = ""

        if buffer:
            chunks.append(DocChunk.from_text(doc.id, doc.source, buffer))
        return chunks

