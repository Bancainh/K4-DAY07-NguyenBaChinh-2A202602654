from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document




class EmbeddingStore:
    """Lưu và tìm kiếm các chunk trong bộ nhớ."""

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name

        self._store: list[dict[str, Any]] = []
        self._next_index = 0

        # Bản triển khai này chủ động sử dụng in-memory store.
        self._use_chroma = False
        self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        # Sao chép để không thay đổi metadata của đầu vào.
        metadata = dict(doc.metadata)

        # Giữ doc_id gốc nếu chunk đã được gán trước đó.
        metadata.setdefault("doc_id", doc.id)

        embedding = list(self._embedding_fn(doc.content))

        record = {
            "id": f"{self._collection_name}_{self._next_index}",
            "content": doc.content,
            "metadata": metadata,
            "embedding": embedding,
        }

        self._next_index += 1

        return record

    def _search_records(
        self,
        query: str,
        records: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        if top_k <= 0 or not records:
            return []

        query_embedding = list(self._embedding_fn(query))
        results = []

        for record in records:
            score = _dot(query_embedding, record["embedding"])

            results.append({
                "id": record["id"],
                "content": record["content"],
                "metadata": dict(record["metadata"]),
                "score": score,
            })

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        for doc in docs:
            record = self._make_record(doc)
            self._store.append(record)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        return self._search_records(
            query=query,
            records=self._store,
            top_k=top_k,
        )

    def get_collection_size(self) -> int:
        return len(self._store)

    def search_with_filter(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> list[dict[str, Any]]:
        if not metadata_filter:
            return self.search(query, top_k=top_k)

        filtered_records = [
            record
            for record in self._store
            if all(
                key in record["metadata"]
                and record["metadata"][key] == value
                for key, value in metadata_filter.items()
            )
        ]

        return self._search_records(
            query=query,
            records=filtered_records,
            top_k=top_k,
        )

    def delete_document(self, doc_id: str) -> bool:
        size_before = len(self._store)

        self._store = [
            record
            for record in self._store
            if record["metadata"].get("doc_id") != doc_id
        ]

        return len(self._store) < size_before