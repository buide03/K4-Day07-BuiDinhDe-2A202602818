from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Operates in-memory using dot-product similarity over normalized embeddings.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """
        Normalize a Document into an internal stored record.
        Ensures metadata is cloned and doc_id is preserved for document deletion.
        """
        metadata = dict(doc.metadata) if doc.metadata else {}
        if "doc_id" not in metadata:
            metadata["doc_id"] = doc.id

        embedding = self._embedding_fn(doc.content)
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": embedding,
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """
        Execute similarity search over a provided list of candidate records.
        Computes dot product, sorts in descending order, and omits the raw vector in results.
        """
        if not records:
            return []

        query_vec = self._embedding_fn(query)
        scored_records = []
        for record in records:
            score = _dot(query_vec, record["embedding"])
            scored_records.append({
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": score,
            })

        scored_records.sort(key=lambda r: r["score"], reverse=True)
        return scored_records[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it in-memory.
        """
        for doc in docs:
            record = self._make_record(doc)
            self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query among all stored records.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict | None = None) -> list[dict[str, Any]]:
        """
        Search with metadata pre-filtering.
        Filters candidate records first, then runs similarity search to avoid empty top-k slots.
        """
        if not metadata_filter:
            candidates = self._store
        else:
            candidates = [
                record for record in self._store
                if all(record["metadata"].get(k) == v for k, v in metadata_filter.items())
            ]
        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document matching metadata['doc_id'].
        Returns True if any chunks were removed, False otherwise.
        """
        initial_count = len(self._store)
        self._store = [
            record for record in self._store
            if record["metadata"].get("doc_id") != doc_id
        ]
        return len(self._store) < initial_count
