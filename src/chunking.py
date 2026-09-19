from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        chunks = []

        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i:i + self.max_sentences_per_chunk]
            chunk = " ".join(group)
            chunks.append(chunk)

        return chunks


class RecursiveChunker:
    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(
        self,
        separators: list[str] | None = None,
        chunk_size: int = 500,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        self.separators = (
            list(self.DEFAULT_SEPARATORS)
            if separators is None
            else list(separators)
        )
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        return self._split(text, self.separators)

    def _split(
        self,
        current_text: str,
        remaining_separators: list[str],
    ) -> list[str]:
        if not current_text:
            return []

        # Đoạn đã đủ nhỏ thì không cần chia tiếp.
        if len(current_text) <= self.chunk_size:
            return [current_text]

        # Hết dấu phân cách: cắt trực tiếp theo số ký tự.
        if not remaining_separators:
            return [
                current_text[i:i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # Chuỗi rỗng là mức cuối: chia theo ký tự.
        if separator == "":
            return [
                current_text[i:i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        # Không tìm thấy dấu phân cách này thì thử mức tiếp theo.
        if separator not in current_text:
            return self._split(current_text, next_separators)

        raw_parts = current_text.split(separator)
        small_parts = []

        for index, part in enumerate(raw_parts):
            # Giữ lại dấu phân cách để không làm mất nội dung.
            if index < len(raw_parts) - 1:
                part += separator

            if not part:
                continue

            small_parts.extend(self._split(part, next_separators))

        # Ghép các phần nhỏ liền nhau, không vượt chunk_size.
        chunks = []
        current_chunk = ""

        for part in small_parts:
            if len(current_chunk) + len(part) <= self.chunk_size:
                current_chunk += part
            else:
                if current_chunk:
                    chunks.append(current_chunk)

                current_chunk = part

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class ChunkingStrategyComparator:
    def compare(self, text: str, chunk_size: int = 200) -> dict:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        # Bảo đảm overlap luôn nhỏ hơn chunk_size.
        overlap = min(50, chunk_size - 1)

        strategies = {
            "fixed_size": FixedSizeChunker(
                chunk_size=chunk_size,
                overlap=overlap,
            ),
            "by_sentences": SentenceChunker(
                max_sentences_per_chunk=3,
            ),
            "recursive": RecursiveChunker(
                chunk_size=chunk_size,
            ),
        }

        comparison = {}

        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            count = len(chunks)

            avg_length = (
                sum(len(chunk) for chunk in chunks) / count
                if count > 0
                else 0.0
            )

            comparison[name] = {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks,
            }

        return comparison