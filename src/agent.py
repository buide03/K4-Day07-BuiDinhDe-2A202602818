from __future__ import annotations

from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context (numbered for source traceability).
        3. Call the LLM to generate an answer without hallucinations.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3, filter_metadata: dict | None = None) -> str:
        if self.store.get_collection_size() == 0:
            return "Không tìm thấy thông tin phù hợp vì cơ sở tri thức hiện đang trống."

        if filter_metadata:
            results = self.store.search_with_filter(question, top_k=top_k, metadata_filter=filter_metadata)
        else:
            results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong cơ sở tri thức để trả lời câu hỏi."

        context_blocks = []
        for index, r in enumerate(results, start=1):
            source_info = (
                r.get("metadata", {}).get("title")
                or r.get("metadata", {}).get("doc_id")
                or r.get("id", f"tài_liệu_{index}")
            )
            content = r.get("content", "").strip()
            context_blocks.append(f"[{index}] Nguồn: {source_info}\n{content}")

        context_text = "\n\n".join(context_blocks)

        prompt = (
            "Bạn là trợ lý AI thông minh, hỗ trợ tra cứu thông tin dựa trên cơ sở tri thức.\n\n"
            "Dưới đây là các đoạn thông tin ngữ cảnh được trích xuất từ cơ sở dữ liệu:\n"
            f"{context_text}\n\n"
            "Yêu cầu trả lời:\n"
            "1. Chỉ sử dụng thông tin có trong các đoạn ngữ cảnh trên để trả lời câu hỏi.\n"
            "2. Luôn ghi rõ nguồn trích dẫn bằng cách gắn số thứ tự [1], [2] tương ứng ở mỗi luận điểm.\n"
            "3. Nếu ngữ cảnh không có đủ thông tin để trả lời câu hỏi, hãy nói rõ là 'Không tìm thấy thông tin trong tài liệu'.\n\n"
            f"Câu hỏi: {question}\n"
            "Câu trả lời:"
        )

        return self.llm_fn(prompt)
